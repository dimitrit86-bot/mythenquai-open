"""Apply checksum-guarded, reviewed text patches on the verification branch only."""
from pathlib import Path
import base64,zlib,hashlib,json
chunks=[Path(f'tools/nk14/part-{i}.txt').read_text().strip() for i in range(6)]
# Repair one known transport transcription character, then verify the entire payload.
chunks[3]=chunks[3].replace('Bumqj87Xevby','Bumqj87evby')
raw=zlib.decompress(base64.b64decode(''.join(chunks),validate=True))
assert hashlib.sha256(raw).hexdigest()=='3a184bf2565be26c91c180301e20a1701697b53a43e6e3356bce141e294e506e','Payload checksum mismatch'
prepared=[]
for op in json.loads(raw):
 p=Path(op['path']);assert not p.is_absolute() and '..' not in p.parts and (str(p).startswith('kompass/') or str(p)=='tools/nk14_browser.py')
 old=p.read_text() if p.exists() else ''
 digest=hashlib.sha256(old.encode()).hexdigest()
 if digest==op['after']:continue
 assert (digest==op['before'] if op['before'] else not p.exists()),'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  lines=old.splitlines(keepends=True)
  for i,j,replacement in reversed(op['patches']):lines[i:j]=replacement
  new=''.join(lines)
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Result checksum mismatch: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified text-file changes')
