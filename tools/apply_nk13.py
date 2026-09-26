"""Apply reviewed, hash-guarded text edits to app sources only. No user data."""
from pathlib import Path
import gzip,base64,json,hashlib
z=base64.b64decode(''.join(p.read_text().strip() for p in sorted(Path('tools/nk13').glob('part-*.txt'))),validate=True)
assert hashlib.sha256(z).hexdigest()=='388ab963f52a4a4136a0e53ddc01ed3ed6d91bd48fdb8b6463ac92c1a3f9b571','Bundle checksum mismatch'
changes=json.loads(gzip.decompress(z));prepared=[]
for op in changes:
 path=Path(op['path']);assert not path.is_absolute() and '..' not in path.parts and (str(path).startswith('kompass/') or str(path)=='tools/test_browser.py')
 old=path.read_text() if path.exists() else ''
 h=hashlib.sha256(old.encode()).hexdigest()
 if h==op['after']:continue
 assert (h==op['before'] if op['before'] else not path.exists()), 'Unexpected base: '+str(path)
 lines=old.splitlines(keepends=True)
 for i,j,replacement in reversed(op['patches']):lines[i:j]=replacement
 new=''.join(lines);assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Result checksum mismatch: '+str(path)
 prepared.append((path,new))
for path,new in prepared:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(new)
print('Applied',len(prepared),'verified source changes')
