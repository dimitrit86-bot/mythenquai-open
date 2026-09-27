"""Apply reviewed public source only, guarded by compressed and per-file checksums."""
from pathlib import Path
import base64,gzip,hashlib,json
chunks=[Path(f'tools/cups110/part-{i}.txt').read_text().strip() for i in range(3)]
# Transport corrections, when needed, are explicitly verified against the full hash.
fix=Path('tools/cups110/transport.json')
if fix.exists():
 for key,edits in json.loads(fix.read_text()).items():
  i=int(key)
  for a,b,replacement in reversed(edits):chunks[i]=chunks[i][:a]+replacement+chunks[i][b:]
z=base64.b64decode(''.join(chunks),validate=True)
assert hashlib.sha256(z).hexdigest()=='f156acafe6bda40d635317d59ed4724fa1a9c130ce28ab1156aae74125d8cd79','Transport checksum mismatch'
prepared=[]
for op in json.loads(gzip.decompress(z)):
 p=Path(op['path']);assert not p.is_absolute() and '..' not in p.parts and (str(p).startswith('kompass/') or str(p)=='tools/test_cups_recipes.py')
 old=p.read_text() if p.exists() else '';digest=hashlib.sha256(old.encode()).hexdigest()
 if digest==op['after']:continue
 assert (digest==op['before'] if op['before'] else not p.exists()),'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  new=old
  for a,b,replacement in reversed(op['edits']):new=new[:a]+replacement+new[b:]
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Invalid result: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified source edits.')
