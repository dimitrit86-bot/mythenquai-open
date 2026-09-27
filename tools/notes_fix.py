"""Reviewed template interpolation correction. No private data."""
from pathlib import Path
p=Path('kompass/release-notes.js');s=p.read_text()
a="""data-release-action="'+(view==='archive'?'new':'archive')+'" '+(view==='archive'&&!unread.length?'hidden':'')+'>"""
b="""data-release-action="${view==='archive'?'new':'archive'}" ${view==='archive'&&!unread.length?'hidden':''}>"""
assert s.count(a)==1 or b in s
p.write_text(s.replace(a,b))
print('Archive switch uses template interpolation.')
