"""Apply reviewed app-only source edits after full-bundle and per-file hash checks."""
from pathlib import Path
import base64,gzip,hashlib,json
parts=[Path(f'tools/nk18/part-{i:02d}.txt').read_text().strip() for i in range(13)]
# Correct two identified transport typos, then verify the entire original payload.
parts[5]=parts[5].replace('NUbRIc81','NUbRs81',1)
parts[11]=parts[11].replace('DIH8MgTyz','DIH8MwTyz',1)
z=base64.b64decode(''.join(parts),validate=True)
assert hashlib.sha256(z).hexdigest()=='29ae6898530c5338545a075989958198b602d593044f76eb20e6890d221203be','Bundle checksum mismatch'
prepared=[]
for op in json.loads(gzip.decompress(z)):
 p=Path(op['path']);assert str(p).startswith('kompass/') and not p.is_absolute() and '..' not in p.parts
 old=p.read_text() if p.exists() else ''
 h=hashlib.sha256(old.encode()).hexdigest()
 if h==op['after']:continue
 assert (h==op['before'] if op['before'] else not p.exists()), 'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  lines=old.splitlines(keepends=True)
  for i,j,content in reversed(op['edits']):lines[i:j]=content
  new=''.join(lines)
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Invalid result: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified public-source changes; no user data accessed.')
