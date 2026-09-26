"""Public OFF bulk import; no access to private app data or credentials."""
import csv,gzip,io,json,math,re,time,urllib.request
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
URL='https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'
UA='Naehrstoff-Kompass/1.2 (+https://github.com/dimitrit86-bot/mythenquai-open)'
MAP={'energy-kcal':'energy','energy':'energyKJ','proteins':'protein','fat':'fat','saturated-fat':'saturated','carbohydrates':'carbs','sugars':'sugar','fiber':'fiber','salt':'salt','vitamin-c':'vitC','vitamin-b1':'vitB1','vitamin-b2':'vitB2','vitamin-b6':'vitB6','pantothenic-acid':'vitB5','calcium':'calcium','magnesium':'magnesium','potassium':'potassium','phosphorus':'phosphorus','iron':'iron','zinc':'zinc','sodium':'sodium','vitamin-d':'vitD','vitamin-b12':'vitB12','vitamin-k':'vitK','biotin':'biotin','iodine':'iodine','selenium':'selenium'}
MG={'vitC','vitB1','vitB2','vitB6','vitB5','calcium','magnesium','potassium','phosphorus','iron','zinc','sodium'}
UG={'vitD','vitB12','vitK','biotin','iodine','selenium'}
def tags(s):return {x.strip().lower() for x in (s or '').split(',') if x.strip()}
def finite(s):
 try:
  v=float(s);return v if math.isfinite(v) and v>=0 else None
 except (ValueError,TypeError):return None
def transform(r):
 b=tags(r.get('brands_tags') or r.get('brands'));alpro='alpro' in b
 st=tags(r.get('stores_tags') or r.get('stores'));stores=[n for n in ('Migros','Coop','Lidl','Aldi') if any(x==n.lower() or x.startswith(n.lower()+'-') or x.endswith('-'+n.lower()) for x in st)]
 countries=tags(r.get('countries_tags'));labels=tags(r.get('labels_tags'))
 diet='vegan' if labels & {'en:vegan','en:european-vegetarian-union-vegan','en:vegan-society'} else 'vegetarisch' if labels & {'en:vegetarian','en:european-vegetarian-union-vegetarian'} else 'unknown'
 if not(alpro or ('en:switzerland' in countries and stores and diet!='unknown')):return None,'out-of-scope'
 code=r.get('code','').strip();name=(r.get('product_name_de') or r.get('product_name') or '').strip()
 if not re.fullmatch(r'\d{8,14}',code):return None,'invalid-barcode'
 if not name:return None,'missing-name'
 n={};q={}
 for col,key in MAP.items():
  v=finite(r.get(col+'_100g'))
  if v is not None:
   v*=1000 if key in MG else 1000000 if key in UG else 1
   if v<=1e9:n[key]=round(v,8)
 if n.get('energy') is None and n.get('energyKJ') is not None:n['energy']=round(n['energyKJ']/4.184,2);q['energy']='Aus kJ mit 4,184 kJ/kcal umgerechnet.'
 if not all(k in n for k in ('energy','protein','fat','carbs')):return None,'missing-core-nutrition'
 if n['energy']>950 or any(n[k]>100.5 for k in ('protein','fat','carbs')):return None,'implausible-core-nutrition'
 if sum(n[k] for k in ('protein','fat','carbs'))>105:return None,'implausible-macro-sum'
 for a,b in [('sugar','carbs'),('saturated','fat')]:
  if a in n and n[a]>n[b]+.5:n.pop(a);q[a]='Widerspruch in der Quelle; Wert nicht übernommen.'
 quantity=r.get('quantity','');hint='ml' if re.search(r'\d\s*(?:ml|cl|dl|l|litre|liter)\b',quantity,re.I) else 'g'
 brand=r.get('brands','').strip()[:160]
 if brand and not name.lower().startswith(brand.lower()):name=brand+' · '+name
 return {'id':'off-'+code,'code':code,'name':name[:230],'brand':brand,'quantity':quantity[:80],'stores':stores,'market':'CH' if 'en:switzerland' in countries else 'International','countries':sorted(countries),'isAlpro':alpro,'diet':diet,'dietEvidence':'Keine ausreichende explizite Veggie-Kennzeichnung.' if diet=='unknown' else 'Explizites Label im Community-Datensatz; Packung prüfen.','basisHint':hint,'needsBasisConfirmation':True,'n':n,'q':q,'modifiedAt':r.get('last_modified_datetime') or r.get('last_modified_t') or '','url':'https://world.openfoodfacts.org/product/'+code},None
def main():
 csv.field_size_limit(10485760);start=time.monotonic();records={};rejected=Counter();scanned=0
 with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':UA}),timeout=90) as response:
  date=response.headers.get('Last-Modified','unknown');print('Bulk export HTTP',response.status,'Last-Modified',date,flush=True)
  with gzip.GzipFile(fileobj=response) as gz,io.TextIOWrapper(gz,encoding='utf-8',errors='replace',newline='') as text:
   reader=csv.reader(text,delimiter='\t');header=next(reader)
   if 'code' not in header or 'proteins_100g' not in header:raise RuntimeError('Unsupported CSV schema')
   print('CSV columns:',json.dumps(header),flush=True)
   ix={k:header.index(k) for k in ['brands_tags','brands','stores_tags','stores','countries_tags'] if k in header}
   for v in reader:
    scanned+=1
    b=','.join(v[ix[k]] for k in ('brands_tags','brands') if k in ix and ix[k]<len(v)).lower();s=','.join(v[ix[k]] for k in ('stores_tags','stores') if k in ix and ix[k]<len(v)).lower();c=v[ix['countries_tags']] if 'countries_tags' in ix and ix['countries_tags']<len(v) else ''
    if 'alpro' not in b and not('switzerland' in c and any(x in s for x in ['migros','coop','lidl','aldi'])):continue
    rec,reason=transform(dict(zip(header,v)))
    if rec:records[rec['id']]=rec
    else:rejected[reason]+=1
 products=sorted(records.values(),key=lambda p:(p['market']!='CH',p['name'].casefold(),p['code']))
 if not products:raise RuntimeError('No matching validated records; existing catalogue untouched.')
 counts={s:sum(s in p['stores'] and p['market']=='CH' for p in products) for s in ('Migros','Coop','Lidl','Aldi')};counts['Alpro']=sum(p['isAlpro'] for p in products)
 report={'version':'1.2.0','importedAt':datetime.now(timezone.utc).isoformat(),'source':'Open Food Facts public CSV export','sourceUrl':URL,'sourceLastModified':date,'license':'ODbL 1.0','scanned':scanned,'count':len(products),'counts':counts,'dietCounts':dict(Counter(p['diet'] for p in products)),'excluded':dict(rejected),'seconds':round(time.monotonic()-start,1),'coverage':'All matching export records with usable core nutrition; not a complete current retailer assortment. Barcode/pack variants remain separate.','basis':'Confirm per 100 g/ml against the pack before first use.'}
 out=Path('kompass');out.mkdir(exist_ok=True)
 (out/'retail-data.js').write_text('/* Open Food Facts contributors; ODbL 1.0. Public facts only. */\nwindow.NK_RETAIL='+json.dumps({'meta':report,'products':products},ensure_ascii=True,separators=(',',':'))+';\n')
 (out/'RETAIL-IMPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
