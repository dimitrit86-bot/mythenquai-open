"""Apply checksum-guarded reviewed source changes; no user data or credentials."""
from pathlib import Path
import json,base64,gzip,hashlib
s=''.join(Path(f'tools/nk17/part-{i:02}.txt').read_text().strip() for i in range(17))
z=base64.b64decode(s,validate=True)
assert hashlib.sha256(z).hexdigest()=='2117d18223afb23c957a77a2fa3db8ec2701ec5ec6ebc3541fa7132029a8e807','Bundle checksum mismatch'
prepared=[]
for op in json.loads(gzip.decompress(z)):
 p=Path(op['path']);assert not p.is_absolute() and '..' not in p.parts and (str(p).startswith('kompass/') or str(p)=='tools/test_visual_reports.py')
 old=p.read_text() if p.exists() else '';h=hashlib.sha256(old.encode()).hexdigest()
 if h==op['after']:continue
 assert (h==op['before'] if op['before'] else not p.exists()),'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  lines=old.splitlines(keepends=True)
  for i,j,replacement in reversed(op['patches']):lines[i:j]=replacement
  new=''.join(lines)
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Result checksum mismatch: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified source changes')
