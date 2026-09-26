"""Hash-guarded public-source changes only; no access to personal profile data."""
from pathlib import Path
import json,base64,zlib,hashlib
parts=[Path('tools/nk15/part-'+str(i)+'.txt').read_text().strip() for i in range(4)]
# Restore two recorded transport transcription errors before verifying the whole bundle.
parts[0]=parts[0].replace('BmNXGG/sMC','BmNXG/sMC')
parts[1]=parts[1].replace('Nxz3fm0e/Xi','Nxz3fm0e9Xi')
raw=zlib.decompress(base64.b64decode(''.join(parts),validate=True))
assert hashlib.sha256(raw).hexdigest()=='79c469adf3c6ccc626236ee8e4b72e283589111ec9c121013de6e94b8c6ea5f5','Bundle checksum mismatch'
prepared=[]
for op in json.loads(raw):
 p=Path(op['path']);assert str(p).startswith('kompass/') and '..' not in p.parts and not p.is_absolute()
 old=p.read_text() if p.exists() else ''
 digest=hashlib.sha256(old.encode()).hexdigest()
 if digest==op['after']:continue
 assert (digest==op['before'] if op['before'] else not p.exists()),'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  lines=old.splitlines(keepends=True)
  for i,j,replacement in reversed(op['edits']):lines[i:j]=replacement
  new=''.join(lines)
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Invalid result: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified source changes')
