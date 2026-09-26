"""Plot roots of two exact quadratic examples from the same artificial mask."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[1]
for font in (ROOT/'fonts').glob('STIXTwoText-*.ttf'):
    font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':'STIX Two Text','font.size':12,
                     'mathtext.fontset':'stix','pdf.fonttype':42,'svg.fonttype':'none'})
teal,rust,ink='#167b80','#b35732','#202a34'
fig,axes=plt.subplots(1,2,figsize=(7.5,3.25),gridspec_kw={'wspace':.35})
polys=[[1/72,7/30,1],[1/(12*np.pi**2),7/30,1]]
titles=['Condition on coprimality','Average over all tuples']
formula=[r'$\Phi_g(z)=1+\frac{7}{30}z+\frac{1}{72}z^2$',
         r'$\Psi_g(z)=1+\frac{7}{30}z+\frac{1}{12\pi^2}z^2$']
roots=[]
for i,(ax,coef,title,eq) in enumerate(zip(axes,polys,titles,formula)):
    rr=np.roots(coef).astype(complex); roots.append([[float(z.real),float(z.imag)] for z in rr])
    ax.axhline(0,color='#89929b',lw=.75)
    ax.axvline(0,color='#89929b',lw=.75)
    ax.scatter(rr.real,rr.imag,s=80,c=[rust if i==0 else teal],zorder=4)
    ax.set(xlim=(-25,1.8),ylim=(-2.2,2.2),xticks=[-24,-16,-8,0],yticks=[-2,0,2])
    ax.spines[['top','right','left','bottom']].set_visible(False)
    ax.tick_params(length=0,labelsize=10)
    ax.set_title(title,fontsize=12.5,pad=36,color=ink)
    ax.text(.5,1.07,eq,ha='center',va='bottom',transform=ax.transAxes,fontsize=13)
    ax.set_xlabel('Real part',fontsize=11)
    if i==0: ax.set_ylabel('Imaginary part',fontsize=11)
    ax.text(.5,-.60,'Two nonreal zeros' if i==0 else 'Two negative real zeros',
            transform=ax.transAxes,ha='center',color=rust if i==0 else teal,fontsize=12)
fig.subplots_adjust(left=.09,right=.97,top=.68,bottom=.28)
for ext in ['pdf','svg','png']:
    fig.savefig(ROOT/'figures'/f'05_two_averages.{ext}',dpi=220,bbox_inches='tight',facecolor='white')
(ROOT/'figures'/'two_average_roots.json').write_text(json.dumps({'mask':[3,5],
    'phi_roots':roots[0],'psi_roots':roots[1],
    'scope':'Exact polynomial coefficients; root coordinates shown numerically.'},indent=2))
print('Built the two-average root comparison.')
