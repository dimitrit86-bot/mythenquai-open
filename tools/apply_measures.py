"""Checksum-guarded public source edits; no private profile or nutrient mutations."""
from pathlib import Path
import json,base64,zlib,hashlib
parts=[Path(f'tools/nk111/part-{i}.txt').read_text().strip() for i in range(2)]
# Correct the three recorded transport transcription differences; the entire raw
# bundle and every source/result file are then verified against local checksums.
parts[0]=parts[0].replace('h9I9zz/84','h9Izz/84').replace('rvubpr9mqoe','rvubprmqoe')
parts[1]=parts[1].replace('XT48UeP3r','XT48eP3r')
raw=zlib.decompress(base64.b64decode(''.join(parts),validate=True))
assert hashlib.sha256(raw).hexdigest()=='f46c8753fa45925c060db7a66f41043326351c5ad40762f2acf272dbe299cebb','Source bundle checksum mismatch'
prepared=[]
for op in json.loads(raw):
 p=Path(op['path']);assert not p.is_absolute() and '..' not in p.parts and (str(p).startswith('kompass/') or str(p)=='tools/test_measures.py')
 old=p.read_text() if p.exists() else '';digest=hashlib.sha256(old.encode()).hexdigest()
 if digest==op['after']:continue
 assert digest==op['before'] if op['before'] else not p.exists(), 'Unexpected base: '+str(p)
 if 'new' in op:new=op['new']
 else:
  new=old
  for start,end,replacement in reversed(op['edits']):new=new[:start]+replacement+new[end:]
 assert hashlib.sha256(new.encode()).hexdigest()==op['after'],'Unexpected result: '+str(p)
 prepared.append((p,new))
for p,new in prepared:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(new)
print('Applied',len(prepared),'hash-verified public source edits')
