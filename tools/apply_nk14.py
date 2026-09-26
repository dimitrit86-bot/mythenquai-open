"""Reconstruct and apply a hash-guarded reviewed public-source patch. No private data."""
from pathlib import Path
import base64,gzip,json,hashlib
parts=[Path('tools/nk14/part-'+str(i)+'.txt').read_text().strip() for i in range(4)]
# Correct the single recorded transport typo, then check the entire compressed payload.
parts[0]=parts[0].replace('Xd3XvJHtmUOJJ','Xd3XvJtmUOJJ',1)
z=base64.b64decode(''.join(parts),validate=True)
assert hashlib.sha256(z).hexdigest()=='96b247d7a6263a4d53cd6d630e441f51a6ba004106a02bdeb013bc83247f6f56','Payload checksum mismatch'
changes=json.loads(gzip.decompress(z));prepared=[]
for name,op in changes.items():
 p=Path(name);assert not p.is_absolute() and '..' not in p.parts and (name.startswith('kompass/') or name=='tools/test_import14.py')
 old=p.read_text() if p.exists() else ''
 h=hashlib.sha256(old.encode()).hexdigest()
 if h==op['after']:continue
 if 'new' in op:
  assert not p.exists(),'Unexpected existing file: '+name
  new=op['new']
 else:
  assert h==op['before'],'Base changed: '+name
  new=old
  for start,end,replacement in reversed(op['edits']):new=new[:start]+replacement+new[end:]
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Result checksum mismatch: '+name
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified public source changes')
