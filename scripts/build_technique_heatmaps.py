"""Recreate appendix heatmaps from the recorded technique percentages.

Run from the repository root. Output is vector TikZ with a common 0--35% scale.
"""
import csv
from pathlib import Path

rows=list(csv.DictReader(Path('data/technique_stage_shares.csv').open()))
techniques=list(dict.fromkeys(r['technique'] for r in rows))
lookup={(r['model'],r['difficulty'],r['stage'],r['technique']):float(r['share_percent']) for r in rows}
assert len(lookup)==576
for model in ['SFT','D1','D2','D3']:
    out=[r'\begingroup',r'\linespread{1}\selectfont',r'\begin{tikzpicture}[x=0.92cm,y=0.65cm,font=\scriptsize]',r'\definecolor{techniquelow}{HTML}{FFFFD9}',r'\definecolor{techniquehigh}{HTML}{7FCDBB}']
    for i,technique in enumerate(techniques):
        label=('MI: ' if i<4 else 'CBT: ')+technique
        out.append(r'\node[anchor=east,align=right,text width=4.8cm] at (-0.15,'+str(-i-.5)+') {'+label+'};')
    for d,mode in enumerate(['Easy','Normal','Hard']):
        origin=d*3.25
        out.append(r'\node[font=\small\bfseries] at ('+str(origin+1.5)+',0.5) {'+mode+'};')
        for t,stage in enumerate(['Early','Middle','Late']):
            out.append(r'\node at ('+str(origin+t+.5)+',-16.4) {'+stage+'};')
            for i,technique in enumerate(techniques):
                value=lookup[(model,mode,stage,technique)]
                out.append(r'\fill[techniquehigh!'+f'{value/35*100:.4f}'+'!techniquelow] ('+str(origin+t)+','+str(-i)+') rectangle ('+str(origin+t+1)+','+str(-i-1)+');')
                out.append(r'\node at ('+str(origin+t+.5)+','+str(-i-.5)+') {'+f'{value:.1f}'+'};')
        out.append(r'\draw ('+str(origin)+',0) rectangle ('+str(origin+3)+',-16);')
    # Compact shared scale with explicit endpoints.
    for i in range(100):
        out.append(r'\fill[techniquehigh!'+str(i)+'!techniquelow] ('+str(2+i*.04)+',-17.1) rectangle ('+str(2+(i+1)*.04)+',-17.35);')
    out.extend([r'\node[anchor=east] at (1.9,-17.225) {0\%};',r'\node[anchor=west] at (6.1,-17.225) {35\%};',r'\end{tikzpicture}',r'\endgroup'])
    Path('figures/technique_heatmap_'+model.lower()+'.tex').write_text('\n'.join(out)+'\n')
