"""Hash-guarded public source changes. Never reads private household state."""
from pathlib import Path
import base64,zlib,json,hashlib
parts=[Path(f'tools/nk113/part-{i}.txt').read_text().strip() for i in range(6)]
# Restore three recorded transport transcription errors, then verify the complete bundle.
parts[2]=parts[2].replace('C1y/15avUe','C1y/19avUe').replace('fvN9tirNVr','fvN9vNVr').replace('WHcdyWcyHAMyf','WHcdyW4CAMyf')
raw=zlib.decompress(base64.b64decode(''.join(parts),validate=True))
assert hashlib.sha256(raw).hexdigest()=='d74967fc6982c9c78cd7b4d50165f1a2ca1f2011b81c358d8bdedea0fc1fc513','Bundle checksum mismatch'
prepared=[]
for op in json.loads(raw):
 p=Path(op['path']);assert not p.is_absolute() and '..' not in p.parts and (str(p).startswith('kompass/') or str(p)=='tools/test_recalc_browser.py')
 old=p.read_text() if p.exists() else '';digest=hashlib.sha256(old.encode()).hexdigest()
 if digest==op['after']:continue
 assert digest==op['before'] if op['before'] else not p.exists(), 'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  lines=old.splitlines(keepends=True)
  for i,j,replacement in reversed(op['patches']):lines[i:j]=replacement
  new=''.join(lines)
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Invalid result: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified source edits.')
