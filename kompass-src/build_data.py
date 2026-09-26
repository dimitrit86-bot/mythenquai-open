"""Build the nutrition app from the exact official BLV workbook and pinned scanners.
No food-value imputation. Npm distributions are integrity-checked before extraction.
"""
import argparse,base64,collections,datetime,hashlib,io,json,math,pathlib,re,tarfile,time,urllib.request,urllib.parse,zipfile
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
APP=ROOT/'kompass'
DOWNLOAD='https://naehrwertdaten.ch/wp-content/uploads/2026/07/Schweizer_Nahrwertdatenbank.xlsx'
EXPECTED='f4bb854944ef811f9b8463984389f8121e73278c4fd24fc3e8d16336cb711270'
fields=[('energy', 'L', 'Energie', 'kcal', 'macro'), ('protein', 'BB', 'Protein', 'g', 'macro'), ('carbs', 'AP', 'Kohlenhydrate', 'g', 'macro'), ('fat', 'O', 'Fett', 'g', 'macro'), ('fiber', 'AY', 'Ballaststoffe', 'g', 'macro'), ('sugar', 'AS', 'Zucker', 'g', 'macro'), ('saturated', 'R', 'Gesättigte Fettsäuren', 'g', 'macro'), ('salt', 'BE', 'Salz', 'g', 'macro'), ('vitA', 'BQ', 'Vitamin A · RAE', 'µg', 'vitamin'), ('vitD', 'DD', 'Vitamin D', 'µg', 'vitamin'), ('vitE', 'DG', 'Vitamin E · α-Tocopherol', 'mg', 'vitamin'), ('vitK', None, 'Vitamin K', 'µg', 'vitamin'), ('vitB1', 'CC', 'Vitamin B1', 'mg', 'vitamin'), ('vitB2', 'CF', 'Vitamin B2', 'mg', 'vitamin'), ('niacinEq', 'CO', 'Niacin-Äquivalente', 'mg', 'vitamin'), ('vitB5', 'CX', 'Pantothensäure · B5', 'mg', 'vitamin'), ('vitB6', 'CI', 'Vitamin B6', 'mg', 'vitamin'), ('biotin', None, 'Biotin', 'µg', 'vitamin'), ('folate', 'CU', 'Nahrungsfolat', 'µg', 'vitamin'), ('vitB12', 'CL', 'Vitamin B12', 'µg', 'vitamin'), ('vitC', 'DA', 'Vitamin C', 'mg', 'vitamin'), ('calcium', 'DS', 'Calcium', 'mg', 'mineral'), ('magnesium', 'DV', 'Magnesium', 'mg', 'mineral'), ('potassium', 'DJ', 'Kalium', 'mg', 'mineral'), ('sodium', 'DM', 'Natrium', 'mg', 'mineral'), ('phosphorus', 'DY', 'Phosphor', 'mg', 'mineral'), ('iron', 'EB', 'Eisen', 'mg', 'mineral'), ('zinc', 'EH', 'Zink', 'mg', 'mineral'), ('iodine', 'EE', 'Jod', 'µg', 'mineral'), ('selenium', 'EK', 'Selen', 'µg', 'mineral'), ('chloride', 'DP', 'Chlorid', 'mg', 'mineral'), ('energyKJ', 'I', 'Energie', 'kJ', 'other'), ('monoFat', 'U', 'Einfach ungesättigte Fettsäuren', 'g', 'other'), ('polyFat', 'X', 'Mehrfach ungesättigte Fettsäuren', 'g', 'other'), ('linoleic', 'AA', 'Linolsäure', 'g', 'other'), ('ala', 'AD', 'Alpha-Linolensäure', 'g', 'other'), ('epa', 'AG', 'EPA', 'g', 'other'), ('dha', 'AJ', 'DHA', 'g', 'other'), ('cholesterol', 'AM', 'Cholesterin', 'mg', 'other'), ('starch', 'AV', 'Stärke', 'g', 'other'), ('alcohol', 'BH', 'Alkohol', 'g', 'other'), ('water', 'BK', 'Wasser im Lebensmittel', 'g', 'other'), ('vitARE', 'BN', 'Vitamin A · RE (nicht RAE)', 'µg', 'other'), ('retinol', 'BT', 'Retinol', 'µg', 'other'), ('betaCaroteneActivity', 'BW', 'Betacarotin-Aktivität', 'µg', 'other'), ('betaCarotene', 'BZ', 'Betacarotin', 'µg', 'other'), ('niacin', 'CR', 'Niacin (ohne Äquivalente)', 'mg', 'other')]

def fetch(url):
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Naehrstoff-Kompass-Build/1.0 (+https://github.com/dimitrit86-bot/mythenquai-open)'})
   with urllib.request.urlopen(req,timeout=70) as r:
    if r.status!=200:raise RuntimeError('HTTP '+str(r.status))
    return r.read()
  except Exception:
   if attempt==2:raise
   time.sleep(2+attempt*3)

def rows(workbook):
 ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 z=zipfile.ZipFile(io.BytesIO(workbook))
 ss=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  ss=[''.join(t.text or '' for t in si.findall('.//m:t',ns)) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
 out={}
 for si in (1,2,3):
  sheet=[]
  for row in ET.fromstring(z.read(f'xl/worksheets/sheet{si}.xml')).findall('.//m:sheetData/m:row',ns):
   record={}
   for cell in row.findall('m:c',ns):
    col=re.sub(r'\d','',cell.attrib['r']);typ=cell.attrib.get('t');value=cell.find('m:v',ns)
    if typ=='s':val=ss[int(value.text)] if value is not None else None
    elif typ=='inlineStr':val=''.join(t.text or '' for t in cell.findall('.//m:t',ns))
    else:val=value.text if value is not None else None
    record[col]=val
   sheet.append(record)
  out[si]=sheet
 return out

def numeric(x):
 try:
  y=float(x)
  return y if math.isfinite(y) and y>=0 else None
 except (TypeError,ValueError):return None

def colnext(s,delta):
 n=0
 for c in s:n=n*26+ord(c)-64
 n+=delta;o=''
 while n:n,r=divmod(n-1,26);o=chr(65+r)+o
 return o

def food_data(workbook):
 digest=hashlib.sha256(workbook).hexdigest()
 if digest!=EXPECTED:raise RuntimeError('Official workbook changed: review schema/data version before updating expected hash. '+digest)
 raw=rows(workbook);foods=[];counts={};methods=[]
 for si,kind in ((1,'generic'),(2,'brand')):
  count=0
  for r in raw[si]:
   if not str(r.get('A','')).isdigit() or not r.get('D'):continue
   if r.get('H')!='pro 100g essbarer Anteil':raise RuntimeError('Unexpected reference quantity '+repr(r.get('H')))
   n={};q={};p={}
   for key,col,label,unit,group in fields:
    val=r.get(col) if col else None;n[key]=numeric(val)
    if n[key] is None and val not in (None,'k.A.'):q[key]=val
    if col:
     method=r.get(colnext(col,1));source=r.get(colnext(col,2))
     if method and method not in methods:methods.append(method)
     if method or source:p[key]=[methods.index(method) if method else None,source]
   foods.append(dict(id='blv-'+r['A'],name=r['D'],synonyms=r.get('E') or '',category=r.get('F') or '',density=numeric(r.get('G')),basis='g',source='BLV 7.1',kind=kind,n=n,q=q,provenance=p));count+=1
  counts[kind]=count
 if len(foods)!=1246 or len(set(f['id'] for f in foods))!=1246:raise RuntimeError('Wrong food count or duplicate IDs')
 sources={r['A']:r['B'] for r in raw[3] if str(r.get('A') or '').isdigit() and r.get('B')}
 data=dict(meta=dict(name='Schweizer Nährwertdatenbank (BLV)',version='7.1',dataDate='2026-07-01',importDate=datetime.datetime.now(datetime.timezone.utc).date().isoformat(),count=len(foods),counts=counts,url='https://naehrwertdaten.ch/de/downloads/',download=DOWNLOAD,sha256=digest,note='Alle 1246 Lebensmittel aus dem offiziellen Download. Nicht alle Nährstoffe sind für jedes Lebensmittel verfügbar. Vitamin K und Biotin sind im Download nicht enthalten. Spuren und Werte unter der Bestimmungsgrenze bleiben markiert und werden nicht als exakte Null addiert.'),nutrients=[dict(key=k,label=l,unit=u,group=g,available=c is not None) for k,c,l,u,g in fields],foods=foods,methods=methods,sources=sources)
 (APP/'data.js').write_text('/* BLV Swiss Food Composition Database 7.1. Source and methods preserved. */\nwindow.NK_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+';\n')
 return {'foods':len(foods),'counts':counts,'nutrientFields':len(fields),'workbookSha256':digest,'download':DOWNLOAD,'source':'BLV 7.1'}

def npm_distribution(package,version,mapping):
 escaped=urllib.parse.quote(package,safe='@')
 meta=json.loads(fetch('https://registry.npmjs.org/'+escaped+'/'+version))
 if meta.get('name')!=package or meta.get('version')!=version:raise RuntimeError('Package metadata mismatch')
 archive=fetch(meta['dist']['tarball']);integrity=meta['dist']['integrity']
 algorithm,expected=integrity.split('-',1)
 if algorithm not in ('sha512','sha256') or base64.b64encode(hashlib.new(algorithm,archive).digest()).decode()!=expected:raise RuntimeError('Package integrity failure '+package)
 tar=tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz')
 for source,target in mapping.items():
  member=tar.getmember('package/'+source)
  if not member.isfile() or member.size>30000000:raise RuntimeError('Unexpected package asset')
  p=APP/'vendor'/target;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(member).read())
 licenses=[m for m in tar.getmembers() if m.isfile() and re.search(r'(^|/)(LICENSE|COPYING)(\.[^/]*)?$',m.name,re.I)]
 for index,m in enumerate(licenses[:5]):
  out=APP/'vendor'/'licenses'/(re.sub(r'[^a-zA-Z0-9.-]','_',package)+'-'+str(index)+'.txt');out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(tar.extractfile(m).read())
 return {'name':package,'version':version,'integrity':integrity,'license':meta.get('license'),'assets':list(mapping.values())}

def vendors():
 deps=[]
 deps.append(npm_distribution('tesseract.js','6.0.1',{'dist/tesseract.min.js':'tesseract.min.js','dist/worker.min.js':'worker.min.js'}))
 core={}
 for variant in ('tesseract-core-lstm','tesseract-core-simd-lstm'):
  for suffix in ('.wasm.js','.wasm'):core[variant+suffix]='core/'+variant+suffix
 deps.append(npm_distribution('tesseract.js-core','6.0.0',core))
 deps.append(npm_distribution('@zxing/browser','0.1.5',{'umd/zxing-browser.min.js':'zxing-browser.min.js'}))
 for language in ('eng','deu'):
  url='https://tessdata.projectnaptha.com/4.0.0_fast/'+language+'.traineddata.gz';b=fetch(url)
  if not b.startswith(b'\x1f\x8b'):raise RuntimeError('Invalid language archive')
  target=APP/'vendor/lang'/f'{language}.traineddata.gz';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
  deps.append({'language':language,'url':url,'sha256':hashlib.sha256(b).hexdigest(),'license':'Apache-2.0; Tesseract tessdata'})
 (APP/'vendor/vendor-lock.json').write_text(json.dumps(deps,indent=2,ensure_ascii=False))
 return deps

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--workbook');parser.add_argument('--skip-vendor',action='store_true');a=parser.parse_args()
 APP.mkdir(exist_ok=True)
 report=food_data(pathlib.Path(a.workbook).read_bytes() if a.workbook else fetch(DOWNLOAD))
 report['builtAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();report['dependencies']=[] if a.skip_vendor else vendors()
 (ROOT/'kompass-src/build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps(report,ensure_ascii=False,indent=2))
