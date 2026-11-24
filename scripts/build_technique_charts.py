"""Build descriptive charts from percentages transcribed from supplied heatmaps.

No raw counts are available. Stage summaries use equal stage weights, not pooled
turn counts. Entropy uses all 16 techniques, normalized for display rounding.
Run from the repository root with python3 scripts/build_technique_charts.py.
"""
import csv
import math
from pathlib import Path

TECHNIQUES = [
    'Affirmation', 'Open Questioning', 'Reflective Listening', 'Summarization',
    'Alternative Perspective', 'Behavior Experiment', 'Changing Rules to Wishes',
    'Continuum Technique', 'Decatastrophizing', 'Efficiency Evaluation',
    'Evidence-Based Questioning', 'Pie Chart Technique',
    'Problem-Solving Skills Training', 'Pros and Cons Analysis', 'Reality Testing',
    'Systematic Exposure',
]
# Each row is one technique: Easy E/M/L, Normal E/M/L, Hard E/M/L.
# Model assignments follow the heatmap titles, not attachment order.
TRANSCRIBED = {
'SFT': '''
13.9 21.5 19.5 16.7 20 22 17.8 19 19.5
25 29 26 18.3 26.5 30 18.3 17.5 25
21.7 14 15.5 22.8 17.5 13 19.4 24 18
17.8 15.5 17.5 18.9 17 20 18.3 18 18
5.6 4 5 7.2 9 3 8.9 3.5 3.5
0 0 0 0 0 0 0 0 0
0 .5 0 1.7 0 .5 0 0 0
0 0 0 0 0 0 0 0 0
11.7 13.5 13.5 9.4 9 10.5 6.7 16.5 12.5
0 0 0 0 0 0 .6 0 0
0 0 .5 .6 0 0 2.2 0 1.5
.6 0 0 .6 0 0 .6 0 0
0 0 0 0 0 0 0 0 0
2.2 1.5 1 3.9 .5 1 6.1 1.5 2
1.7 .5 1.5 0 .5 0 1.1 0 0
0 0 0 0 0 0 0 0 0
''',
'D1': '''
13.9 15 10 11.7 11.5 12.5 15.6 13.5 12.5
15.6 13.5 17.5 8.9 14.5 11 11.7 8.5 13.5
5.6 5 5.5 9.4 8.5 7.5 8.9 10 4.5
10.6 11.5 17 12.2 11.5 9 12.8 13.5 15
17.2 18 13.5 19.4 16.5 14 16.1 15.5 13.5
0 0 .5 0 0 0 0 0 0
.6 0 0 .6 0 0 1.1 1 0
0 0 0 0 0 0 .6 0 0
22.2 26.5 29.5 17.2 27 33 21.1 25.5 31
0 0 0 0 0 .5 0 .5 0
1.7 2 3 2.2 2 2 1.7 2 3
0 0 0 2.8 0 0 0 0 0
0 0 0 0 .5 0 0 0 0
11.7 7 2 10.6 5.5 5.5 9.4 7.5 4
1.1 1.5 1.5 5 2.5 5 1.1 2.5 3
0 0 0 0 0 0 0 0 0
''',
'D2': '''
16.7 18 18.5 19.4 16 20.5 18.9 19 19
22.8 29 32.5 21.1 19 28.5 16.1 21.5 31
22.8 14.5 13.5 25 17.5 13 18.9 22.5 20
18.3 18 19.5 11.7 18 19.5 13.9 14.5 13.5
10 7.5 6 9.4 11.5 5.5 6.7 8 5
0 0 0 0 0 0 0 0 0
.6 0 0 0 0 0 0 .5 .5
0 0 0 0 0 0 0 0 0
7.2 11.5 8.5 8.3 15 11.5 12.2 8.5 6.5
.6 0 0 0 0 0 0 0 0
.6 0 .5 0 .5 1 .6 1 .5
0 0 0 1.1 0 0 2.8 0 0
0 0 0 0 0 0 0 0 0
0 1.5 0 3.9 2.5 .5 7.8 4.5 2.5
.6 0 1 0 0 0 2.2 0 1.5
0 0 0 0 0 0 0 0 0
''',
'D3': '''
17.8 15.5 17.5 16.1 16 21.5 16.7 20.5 13
20.6 32.5 28 16.7 30 24.5 17.8 20 21
21.7 18 13 27.2 16.5 15.5 22.8 21 13.5
15 20 18 18.9 18 17.5 17.8 19.5 23.5
10.6 4 7 6.1 8 4.5 7.8 4.5 9
0 0 0 0 0 0 0 0 0
.6 0 0 1.1 0 0 0 0 0
0 0 0 0 0 0 0 0 0
10.6 9.5 14.5 7.8 9.5 13 9.4 9.5 16.5
0 0 0 0 0 0 1.1 0 0
0 0 .5 .6 0 .5 .6 1.5 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 .5 0 0 0
3.3 .5 .5 5 2 1 5.6 2.5 2.5
0 0 1 .6 0 1.5 .6 1 1
0 0 0 0 0 0 0 0 0
'''
}
MODELS = list(TRANSCRIBED)
MODES = ['Easy','Normal','Hard']
STAGES = ['Early','Middle','Late']
DATA = {}
for model, text in TRANSCRIBED.items():
    rows = [[float(x) for x in line.split()] for line in text.strip().splitlines()]
    assert len(rows) == 16 and all(len(row) == 9 for row in rows)
    DATA[model] = rows
    for col in range(9):
        total = sum(row[col] for row in rows)
        assert abs(total-100) <= .5, (model,col,total)
Path('data').mkdir(exist_ok=True)
with Path('data/technique_stage_shares.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['model','difficulty','stage','technique','share_percent'])
    for model,rows in DATA.items():
        for d,mode in enumerate(MODES):
            for t,stage in enumerate(STAGES):
                for technique,row in zip(TECHNIQUES,rows):
                    w.writerow([model,mode,stage,technique,row[d*3+t]])

def cbt(model,d,t): return sum(row[d*3+t] for row in DATA[model][4:])
def diversity(model,d,t):
    v=[row[d*3+t] for row in DATA[model]]; total=sum(v)
    return math.exp(-sum((x/total)*math.log(x/total) for x in v if x))

# Native vector plots, compiled by pgfplots in the report. No raster scaling.
colors=['blue!75!black','orange!90!black','teal!80!black','purple!80!black']
base=r'width=0.87\textwidth,height=4.1cm,scale only axis=false,axis lines=left,grid=major,grid style={gray!20},tick label style={font=\footnotesize},label style={font=\small},title style={font=\small\bfseries},legend style={font=\footnotesize,draw=none},clip=false'
def wrapper(axes):
    return '\\begingroup\n\\linespread{1}\\selectfont\n'+'\n\\par\\smallskip\n'.join(axes)+'\n\\endgroup\n'
def linecharts(name,func,ylabel,ymin,ymax):
    axes=[]
    for d,mode in enumerate(MODES):
        opt=base+f',title={{{mode}}},ylabel={{{ylabel}}},ymin={ymin},ymax={ymax},xtick={{1,2,3}},xticklabels={{Early,Middle,Late}},xmin=0.85,xmax=3.15'
        if d==0: opt+=r',legend columns=4,legend to name=technique-model-legend-'+name
        lines=[r'\begin{tikzpicture}',r'\begin{axis}['+opt+']']
        for k,model in enumerate(MODELS):
            coords=' '.join(f'({t+1},{func(model,d,t):.4f})' for t in range(3))
            lines.append(r'\addplot+[thick,color='+colors[k]+',mark='+['*','square*','triangle*','diamond*'][k]+'] coordinates {'+coords+'};')
            if d==0: lines.append(r'\addlegendentry{'+model+'}')
        lines += [r'\end{axis}',r'\end{tikzpicture}']
        axes.append('\n'.join(lines))
    axes.append(r'\pgfplotslegendfromname{technique-model-legend-'+name+'}')
    Path('figures/technique_'+name+'.tex').write_text(wrapper(axes))
linecharts('cbt_stages',cbt,r'CBT share (\%)',0,65)
linecharts('diversity',diversity,'Effective techniques',0,12)

axes=[]
catcolors=['blue!60','orange!75','teal!65','purple!45','gray!55']
for d,mode in enumerate(MODES):
    opt=base+r',ybar stacked,bar width=19pt,ymin=0,ymax=100,ylabel={Share (\%)},title={'+mode+r'},xtick={1,2,3,4},xticklabels={SFT,D1,D2,D3},xmin=0.5,xmax=4.5'
    if d==0: opt+=r',legend columns=3,legend to name=technique-mix-legend'
    lines=[r'\begin{tikzpicture}',r'\begin{axis}['+opt+']']
    for k,cat in enumerate(['Affirmation','Open questioning','Reflection','Summarization','CBT (all)']):
        vals=[]
        for model in MODELS:
            val=sum(DATA[model][k][d*3+t] for t in range(3))/3 if k<4 else sum(cbt(model,d,t) for t in range(3))/3
            vals.append(val)
        lines.append(r'\addplot+[fill='+catcolors[k]+',draw=white] coordinates {'+' '.join(f'({i+1},{v:.4f})' for i,v in enumerate(vals))+'};')
        if d==0: lines.append(r'\addlegendentry{'+cat+'}')
    lines += [r'\end{axis}',r'\end{tikzpicture}']
    axes.append('\n'.join(lines))
axes.append(r'\pgfplotslegendfromname{technique-mix-legend}')
Path('figures/technique_mix.tex').write_text(wrapper(axes))

# Derived summaries for review; raw source percentages remain in the CSV.
with Path('data/technique_summary.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['model','difficulty','stage','cbt_share_percent','effective_techniques'])
    for model in MODELS:
        for d,mode in enumerate(MODES):
            for t,stage in enumerate(STAGES):
                w.writerow([model,mode,stage,f'{cbt(model,d,t):.1f}',f'{diversity(model,d,t):.3f}'])
for model in MODELS:
    print(model)
    for d,mode in enumerate(MODES):
        print(mode,'CBT', [round(cbt(model,d,t),1) for t in range(3)], 'diversity', [round(diversity(model,d,t),2) for t in range(3)])
