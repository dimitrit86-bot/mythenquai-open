"""Apply checksum-guarded changes to public source only. No user state or credentials."""
from pathlib import Path
import gzip,base64,json,hashlib
z=base64.b64decode(''.join(Path(f'tools/nk15/part-{i}.txt').read_text().strip() for i in range(7)),validate=True)
assert hashlib.sha256(z).hexdigest()=='987f3635b62931087806086f84a1b6d92ae6b52460a59e0dcae8e00d02876eac','Payload checksum mismatch'
prepared=[]
for op in json.loads(gzip.decompress(z)):
 p=Path(op['path']);assert not p.is_absolute() and '..' not in p.parts and (str(p).startswith('kompass/') or str(p)=='tools/test_goals.py')
 old=p.read_text() if p.exists() else '';h=hashlib.sha256(old.encode()).hexdigest()
 if h==op['after']:continue
 assert h==op['before'] if op['before'] else not p.exists(), 'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  lines=old.splitlines(keepends=True)
  for i,j,replacement in reversed(op['patches']):lines[i:j]=replacement
  new=''.join(lines)
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Result checksum mismatch: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified source changes')
