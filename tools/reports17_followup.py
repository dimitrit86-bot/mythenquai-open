"""Preserve searchable PDF qualifiers and fit long names/partial macro values."""
from pathlib import Path
p=Path('kompass/report-pdf.js');s=p.read_text()
def replace(old,new):
 global s
 assert s.count(old)==1 or new in s,old[:90]
 s=s.replace(old,new)
replace('.replace(/[“”«»]/g', '.replace(/[„“”«»]/g')
replace("para(snap.name,M+24,194,WIDTH-180,11,COL.white,false,14);", "para(snap.name,M+24,192,WIDTH-48,10,COL.white,false,12);")
replace("txt(V.range(report.period),M+24,215,10,'#dbe7da');", "txt(V.range(report.period),M+24,219,10,'#dbe7da');")
old="para(V.amount(r),x+12,510,cardW-20,18,COL.ink,true,21);progress(x+12,528,cardW-24,r.percent,V.tone(r));"
new="if(r.hasGaps&&r.average!==null)txt('Bekannte Teilmenge',x+12,499,7,COL.blue);const value=r.average===null?'—':V.fmt(r.average,r.unit==='kcal'?0:1)+' '+r.unit;let size=17;font(size,true);while(doc.getTextWidth(clean(value))>cardW-24&&size>7){size-=.5;font(size,true);}txt(value,x+12,519,size,COL.ink,true);progress(x+12,533,cardW-24,r.percent,V.tone(r));"
replace(old,new)
p.write_text(s)
p=Path('kompass/tests/report-export.test.js');s=p.read_text()
new="check('German quotation marks remain searchable PDF text',()=>assert.equal(NK_REPORT_PDF.clean('„mind.“ bedeutet bekannte Teilmenge'),'\"mind.\" bedeutet bekannte Teilmenge'));\n"
anchor="console.log('TOTAL REPORT EXPORT TESTS',passed);"
assert anchor in s
if new not in s:s=s.replace(anchor,new+anchor)
p.write_text(s)
print('PDF: searchable German qualifiers, full-width name row, partial macro tag separate from value and bar.')
