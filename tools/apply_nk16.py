"""Apply reviewed reports source, guarded by before/after checksums. No user data."""
from pathlib import Path
import base64,zlib,json,hashlib
parts=[Path('tools/nk16/part-'+str(i)+'.txt').read_text().strip() for i in range(4)]
# Two recorded transport transcription errors; verify the entire restored payload.
parts[2]=parts[2].replace('QQHjzAmAk','QQjzAmAk').replace('3b8cceePxh','3b8ceePxh')
raw=zlib.decompress(base64.b64decode(''.join(parts),validate=True))
assert hashlib.sha256(raw).hexdigest()=='2bf0f8fc905b601b90bd45e56c957cc39d3356aea276500f6f1e6ca78d7458d3','Payload checksum mismatch'
prepared=[]
for op in json.loads(raw):
 p=Path(op['path']);assert not p.is_absolute() and '..' not in p.parts and (str(p).startswith('kompass/') or str(p)=='tools/test_reports.py')
 old=p.read_text() if p.exists() else '';digest=hashlib.sha256(old.encode()).hexdigest()
 if digest==op['after']:continue
 assert (digest==op['before'] if op['before'] else not p.exists()),'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  new=old
  for start,end,replacement in reversed(op['edits']):new=new[:start]+replacement+new[end:]
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Result checksum mismatch: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'verified public source changes')
