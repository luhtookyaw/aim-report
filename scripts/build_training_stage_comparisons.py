"""Reproduce paired GRPO-minus-SFT differences and Holm-adjusted annotations.

Values are recorded directly from the supplied training-stage comparison.
The p=0.001 entries retain the supplied ** annotation (p-values are rounded).
Run from the repository root; uses only the Python standard library.
"""
from pathlib import Path
import csv
DATA = [
('Easy',[
[(.041,'ns','1.000'),(-.138,'ns','1.000'),(-.081,'ns','1.000'),(-.129,'ns','.188')],
[(-.191,'ns','1.000'),(.163,'ns','.568'),(.238,'ns','.244'),(.142,'ns','.052')],
[(-.918,'**','.001'),(.000,'ns','1.000'),(.431,'**','.001'),(.200,'*','.020')]]),
('Normal',[
[(-.032,'ns','1.000'),(-.100,'ns','1.000'),(-.189,'ns','.334'),(-.317,'ns','.064')],
[(-.532,'*','.033'),(-.050,'ns','1.000'),(.190,'*','.033'),(.058,'ns','1.000')],
[(-1.150,'***','<.001'),(-.175,'ns','1.000'),(.385,'**','.001'),(.158,'ns','.277')]]),
('Hard',[
[(-.027,'ns','1.000'),(-.062,'ns','1.000'),(-.222,'ns','.500'),(-.217,'ns','.491')],
[(-.795,'**','.001'),(.037,'ns','1.000'),(.158,'ns','.751'),(.096,'ns','1.000')],
[(-1.018,'***','<.001'),(.062,'ns','1.000'),(.289,'**','.006'),(.212,'*','.030')]])]
METRICS=['CTRS','MITI','WAI-O','WAI-O-S']
with Path('data/training_stage_comparisons.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['difficulty','comparison','metric','mean_difference','holm_adjusted_p','significance'])
 for mode,rows in DATA:
  for i,row in enumerate(rows):
   for metric,(value,stars,p) in zip(METRICS,row):
    w.writerow([mode,f'D{i+1}-SFT',metric,f'{value:.3f}',p if p.startswith('<') else f'{float(p):.3f}',stars])

out=[r'\begingroup',r'\linespread{1}\selectfont',r'\begin{tikzpicture}[x=2.65cm,y=1.2cm,font=\small]',r'\definecolor{stageblue}{HTML}{053061}',r'\definecolor{stagered}{HTML}{67001F}']
for d,(mode,rows) in enumerate(DATA):
 y=-d*4.65
 out.append(r'\node[font=\bfseries] at (2,'+str(y+.43)+') {'+mode+'};')
 for i,row in enumerate(rows):
  out.append(r'\node[anchor=east] at (-0.06,'+str(y-i-.5)+') {D'+str(i+1)+' -- SFT};')
  for j,(value,stars,p) in enumerate(row):
   intensity=abs(value)/1.15*100
   color=('stageblue' if value>=0 else 'stagered')+'!'+f'{intensity:.3f}'+'!white'
   out.append(r'\fill['+color+'] ('+str(j)+','+str(y-i)+') rectangle ('+str(j+1)+','+str(y-i-1)+');')
   symbol=r'\;\mathrm{ns}' if stars=='ns' else '^{'+stars+'}'
   ptext='p < 0.001' if p.startswith('<') else f'p = {float(p):.3f}'
   out.append(r'\node[align=center,text='+('white' if intensity>65 else 'black')+'] at ('+str(j+.5)+','+str(y-i-.5)+') {$'+f'{value:+.3f}'+symbol+r'$\\[2pt]$'+ptext+'$};')
 out.append(r'\draw (0,'+str(y)+') rectangle (4,'+str(y-3)+');')
 for j,m in enumerate(METRICS): out.append(r'\node at ('+str(j+.5)+','+str(y-3.28)+') {'+m+'};')
out += [r'\end{tikzpicture}',r'\endgroup']
Path('figures/training_stage_heatmap.tex').write_text('\n'.join(out)+'\n')

colors=['orange!85!black','teal!80!black','purple!80!black']
axes=[]
for d,(mode,rows) in enumerate(DATA):
 opts=r'width=0.88\textwidth,height=4.3cm,axis lines=left,ybar,bar width=9pt,ymin=-1.35,ymax=0.65,xmin=0.5,xmax=4.5,xtick={1,2,3,4},xticklabels={CTRS,MITI,WAI-O,WAI-O-S},ylabel={Mean difference},title={'+mode+r'},title style={font=\small\bfseries},tick label style={font=\footnotesize},label style={font=\small},ymajorgrids,grid style={gray!20},extra y ticks={0},extra y tick labels={},extra y tick style={grid=major,grid style={black}},legend style={font=\footnotesize,draw=none},legend columns=3'
 if d==0: opts+=r',legend to name=training-stage-bar-legend'
 lines=[r'\begin{tikzpicture}',r'\begin{axis}['+opts+']']
 for i,row in enumerate(rows):
  lines.append(r'\addplot+[fill='+colors[i]+',draw='+colors[i]+'] coordinates {'+' '.join(f'({j+1},{value:.3f})' for j,(value,stars,p) in enumerate(row))+'};')
  if d==0: lines.append(r'\addlegendentry{D'+str(i+1)+' -- SFT}')
 lines += [r'\end{axis}',r'\end{tikzpicture}']
 axes.append('\n'.join(lines))
axes.append(r'\pgfplotslegendfromname{training-stage-bar-legend}')
Path('figures/training_stage_differences.tex').write_text('\\begingroup\n\\linespread{1}\\selectfont\n'+'\n\\par\\smallskip\n'.join(axes)+'\n\\endgroup\n')
