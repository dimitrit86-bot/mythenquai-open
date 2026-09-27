"""Cross-browser fixture and readable photo controls; no private data changes."""
from pathlib import Path
p=Path('tools/test_photo.py');s=p.read_text()
a="  if r.request.url.startswith(URL):return r.continue_()"
b="  if r.request.url.startswith(URL) or r.request.url.startswith('blob:'+URL.split('/kompass/')[0]+'/'):return r.continue_()"
assert s.count(a)==1 or b in s
s=s.replace(a,b)
a="  check('Recognition did not save a product',p.evaluate('NK_APP.getState().foods.length')==0)"
b=a+"\n  p.wait_for_function('!document.querySelector(\"#scan-status\").textContent.includes(\"geladen\")');check('Completed product search clears stale OCR progress')"
assert s.count(a)==1 or b in s
if b not in s:s=s.replace(a,b)
p.write_text(s)
p=Path('kompass/scanner.js');s=p.read_text()
a="try{await root.NK_PHOTO_PRODUCT.identify({image,load,readText:readPhotoText,current:()=>scanCurrent(generation),transfer:photoTransfer});}"
b="try{await root.NK_PHOTO_PRODUCT.identify({image,load,readText:readPhotoText,current:()=>scanCurrent(generation),transfer:photoTransfer});if(scanCurrent(generation))message('');}"
assert s.count(a)==1 or b in s
s=s.replace(a,b);p.write_text(s)
p=Path('kompass/photo-product.css');s=p.read_text()
css='''
/* Match existing rounded app inputs and keep option explanations below their titles. */
.scan-photo-actions .button{display:block;width:100%}
.photo-product-panel input:not([type=checkbox]),.photo-product-panel select{border:1px solid #c9d9d2;border-radius:12px;background-color:#fff;color:#213c32;min-height:48px;padding:11px 12px;font-family:inherit}
.photo-product-panel input:focus-visible,.photo-product-panel select:focus-visible{outline:2px solid #215a48;outline-offset:2px}
.photo-product-panel button[type=submit]{margin-top:8px}
'''
if css not in s:p.write_text(s+css)
print('Same-origin blob fixtures allowed; readable controls and accurate finished status applied.')
