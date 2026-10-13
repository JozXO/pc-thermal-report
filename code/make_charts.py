import pandas as pd, warnings, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')
L='logs'  # folder holding the HWiNFO CSV logs
OUT='charts/'
B,O,INK,MUT,GRID,SURF='#2a78d6','#eb6834','#0b0b0b','#52514e','#e6e5e1','#fcfcfb'
plt.rcParams.update({'font.size':10,'axes.edgecolor':GRID,'axes.labelcolor':MUT,'xtick.color':MUT,'ytick.color':MUT,'figure.facecolor':SURF,'axes.facecolor':SURF,'axes.spines.top':False,'axes.spines.right':False})
def game(f):
    df=pd.read_csv(f'{L}/{f}',encoding='latin-1',low_memory=False)
    df=df[pd.to_datetime(df['Date'],errors='coerce',dayfirst=True).notna()]
    l=pd.to_numeric(df['GPU Core Load [%]'],errors='coerce'); return df[l>50]
def m(g,c): return pd.to_numeric(g[c],errors='coerce').dropna().mean()
def mx(g,c): return pd.to_numeric(g[c],errors='coerce').dropna().max()
def pair(fa,fb,la,lb,metrics,title,fn):
    a,b=game(fa),game(fb)
    fig,axs=plt.subplots(1,len(metrics),figsize=(3.1*len(metrics),3.2))
    for ax,(col,lab,fmt,agg) in zip(axs,metrics):
        va=(mx if agg=='max' else m)(a,col); vb=(mx if agg=='max' else m)(b,col)
        bars=ax.bar([la,lb],[va,vb],color=[O,B],width=0.55)
        for r,v in zip(bars,[va,vb]): ax.text(r.get_x()+r.get_width()/2,v,fmt.format(v),ha='center',va='bottom',color=INK,fontsize=10)
        ax.set_title(lab,fontsize=10,color=INK,loc='left'); ax.set_ylim(0,max(va,vb)*1.18); ax.yaxis.grid(True,color=GRID); ax.set_axisbelow(True)
        ax.tick_params(axis='x',labelsize=9)
    fig.suptitle(title,x=0.01,ha='left',fontsize=11.5,color=INK,fontweight='bold'); fig.tight_layout(); fig.savefig(OUT+fn,dpi=170); plt.close(fig)
pair('taiwan4game.CSV','taiwan5game.CSV','Auto-tuning on','Undervolt restored',
 [('GPU Temperature [°C]','GPU core, avg °C','{:.1f}','mean'),('GPU Hot Spot Temperature [°C]','Hot spot, avg °C','{:.1f}','mean'),('GPU Power [W]','GPU power, avg W','{:.0f}','mean'),('Frame Time [ms]','Worst frame time, ms','{:.0f}','max')],
 'Root cause fixed: NVIDIA App auto-tuning was overriding the undervolt (17 Sep 2026)','1_regression_fix.png')
pair('taiwan10game.CSV','taiwan9game.CSV','Top fan exhaust','Top fan intake (chosen)',
 [('GPU Temperature [°C]','GPU core, avg °C','{:.1f}','mean'),('GPU Hot Spot Temperature [°C]','Hot spot, avg °C','{:.1f}','mean'),('GPU Fan1 [RPM]','GPU fan, avg RPM','{:.0f}','mean')],
 'A/B airflow test: top fan as exhaust vs intake (18 and 20 Sep 2026)','2_airflow_ab.png')
# timeline
S=[('log.CSV','2 Aug','UK baseline'),('log2.CSV','2 Aug','First undervolt'),('log3.CSV','2 Aug',''),('log1taiwan.CSV','16 Sep','In Taiwan'),('log2taiwan.CSV','16 Sep',''),
   ('taiwan4game.CSV','17 Sep','Auto-tuning\noverride'),('taiwan5game.CSV','17 Sep','Fix restored'),('taiwan6game.CSV','17 Sep',''),('taiwan7game.CSV','17 Sep',''),('taiwan8game.CSV','18 Sep',''),('taiwan9game.CSV','18 Sep',''),('taiwan10game.CSV','20 Sep',''),('taiwan11game.CSV','21 Sep','')]
rows=[]
for f,d,lab in S:
    g=game(f); th=[c for c in g.columns if 'Performance Limit - Thermal' in c]
    rows.append((d,lab,m(g,'GPU Temperature [°C]'),(g[th[0]].astype(str).str.strip()=='Yes').sum() if th else 0,m(g,'Fan 1 [RPM]')))
x=list(range(len(rows)))
fig,ax=plt.subplots(figsize=(10,3.8))
ax.plot(x,[r[2] for r in rows],color=B,lw=2,marker='o',ms=6,zorder=3)
for i,r in enumerate(rows):
    if r[3]>0: ax.plot(i,r[2],'o',ms=13,mfc='none',mec=O,mew=2,zorder=4); ax.text(i,r[2]+1.6,f'throttling\n({r[3]} samples)',ha='center',fontsize=8,color=INK)
    if r[1]: ax.annotate(r[1],(i,r[2]),xytext=((14,-4) if r[3] else (0,-38)),textcoords='offset points',ha=('left' if r[3] else 'center'),va=('top' if r[3] else 'baseline'),fontsize=8,color=MUT)
ax.axhline(87,color=MUT,lw=1,ls='--'); ax.text(len(rows)-0.6,87.4,'87°C limit',ha='right',fontsize=8,color=MUT)
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows],fontsize=8); ax.set_ylim(55,93)
ax.annotate('Fans slowed for noise:\ncase runs warmer,\nstill no throttling',(12,rows[12][2]),xytext=(-95,-62),textcoords='offset points',fontsize=8,color=MUT,arrowprops=dict(arrowstyle='-',color=MUT)); ax.set_ylabel('GPU core, avg °C while gaming')
ax.yaxis.grid(True,color=GRID); ax.set_axisbelow(True)
ax.set_title('Every logged gaming session, Aug to Sep 2026',loc='left',fontsize=11.5,color=INK,fontweight='bold')
fig.tight_layout(); fig.savefig(OUT+'3_session_timeline.png',dpi=170); plt.close(fig)
fig,ax=plt.subplots(figsize=(10,3.2))
ax.plot(x,[r[4] for r in rows],color=B,lw=2,marker='o',ms=6)
for i,r in enumerate(rows): ax.text(i,r[4]+60,f'{r[4]:.0f}',ha='center',fontsize=8,color=INK)
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows],fontsize=8); ax.set_ylim(0,2900); ax.set_ylabel('Radiator fan, avg RPM')
ax.yaxis.grid(True,color=GRID); ax.set_axisbelow(True)
ax.annotate('iCUE fixed 30%\n(fans on AIO controller)',(10,rows[10][4]),xytext=(-70,-45),textcoords='offset points',fontsize=8,color=MUT,arrowprops=dict(arrowstyle='-',color=MUT))
ax.set_title('Noise fix: AIO radiator fan speed while gaming',loc='left',fontsize=11.5,color=INK,fontweight='bold')
fig.tight_layout(); fig.savefig(OUT+'4_aio_fan_rpm.png',dpi=170); plt.close(fig)
for r in rows: print(r)
