"""Apply exact, hash-guarded client edits. No database, session or user-data access."""
from pathlib import Path
import json,hashlib
prepared=[]
for name,change in json.loads(Path('tools/nk18-edits.json').read_text()).items():
 assert '/' not in name and '..' not in name
 p=Path('kompass')/name;old=p.read_text();digest=hashlib.sha256(old.encode()).hexdigest()
 if digest==change['after']:continue
 assert digest==change['before'],'Unexpected source: '+name
 new=old
 for start,end,replacement in reversed(change['edits']):new=new[:start]+replacement+new[end:]
 assert hashlib.sha256(new.encode()).hexdigest()==change['after'],'Unexpected result: '+name
 prepared.append((p,new))
for p,new in prepared:p.write_text(new)
print('Applied',len(prepared),'verified client edits')
