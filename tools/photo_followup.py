"""Test fixture compatibility: WebKit surfaces same-origin blob images to routing.
These are local memory URLs, not network uploads. The external request guard remains.
"""
from pathlib import Path
p=Path('tools/test_photo.py');s=p.read_text()
a="  if r.request.url.startswith(URL):return r.continue_()"
b="  if r.request.url.startswith(URL) or r.request.url.startswith('blob:'+URL.split('/kompass/')[0]+'/'):return r.continue_()"
assert s.count(a)==1 or b in s
s=s.replace(a,b);p.write_text(s)
print('Allow only local same-origin blob image URLs; retain external request assertions.')
