from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Arc
from matplotlib import font_manager
import numpy as np

DEST = Path(__file__).resolve().parents[1]
for f in (DEST / "fonts").glob("STIXTwoText-*.ttf"):
    font_manager.fontManager.addfont(str(f))
plt.rcParams.update({"font.family":"STIX Two Text", "font.size":11,
                     "mathtext.fontset":"stix", "pdf.fonttype":42,
                     "svg.fonttype":"none"})
ink, teal, rust = "#202a34", "#167b80", "#b35732"
fig, ax = plt.subplots(figsize=(7.3,3.85))
fig.subplots_adjust(left=.02,right=.98,top=.97,bottom=.03)
ax.set(xlim=(0,100),ylim=(0,52)); ax.axis("off")
ax.text(50,50,"The locked-box experiment",ha="center",va="top",
        fontsize=17,color=ink)
for x, text in [(15,"Hidden integers"),(50,"Noisy relationships"),
                (84,"Recovered prime names")]:
    ax.text(x,41,text,ha="center",fontsize=11.2,color=ink)
for x,y,label in [(5,26,"1"),(17,26,"2"),(5,13,"3"),(17,13,"N")]:
    box=FancyBboxPatch((x,y),9,10,boxstyle="round,pad=.1,rounding_size=.8",
                       facecolor="#f2f6f6",edgecolor=ink,linewidth=.8)
    ax.add_patch(box)
    ax.text(x+4.5,y+5.6,"?",ha="center",va="center",fontsize=19,color=teal)
    ax.text(x+4.5,y+1.1,label,ha="center",va="bottom",fontsize=9,color=ink)
    ax.add_patch(Rectangle((x+3.2,y+8.4),2.6,2.0,facecolor="white",
                           edgecolor=ink,linewidth=.8))
    ax.add_patch(Arc((x+4.5,y+10.3),1.5,2.0,theta1=0,theta2=180,
                     edgecolor=ink,linewidth=.8))
ax.text(15,4,"Labelled boxes; values hidden",ha="center",fontsize=10,color=ink)
pattern=np.array([[0,1,1,0,1,0,1,0],
                  [1,0,0,1,1,1,0,1],
                  [1,0,0,1,0,1,1,0],
                  [0,1,1,0,1,0,0,1],
                  [1,1,0,1,0,1,0,0],
                  [0,1,1,0,1,0,1,1],
                  [1,0,1,0,0,1,0,1],
                  [0,1,0,1,0,1,1,0]])
for i in range(8):
    for j in range(8):
        color="#e8e9eb" if i==j else (teal if pattern[i,j] else "white")
        ax.add_patch(Rectangle((39+2.6*j,13+2.6*(7-i)),2.25,2.25,
                               facecolor=color,edgecolor="#b7c0c6",lw=.4))
ax.text(50,8,"One answer per pair",ha="center",fontsize=10.5,color=ink)
ax.text(50,4,"Independent flips",ha="center",fontsize=10.5,color=rust)
ax.text(84,32,"Denoise and estimate",ha="center",fontsize=10.5,color=ink)
ax.text(84,28,"relationship frequencies",ha="center",fontsize=10.5,color=ink)
ax.text(84,20,r"$d_i d_j/c_{ij}=2/7$",ha="center",fontsize=15,color=teal)
ax.annotate("",xy=(84,12.4),xytext=(84,16.5),
            arrowprops={"arrowstyle":"->","color":ink,"lw":.9})
ax.text(84,8,r"$\{2,3,7\}$",ha="center",fontsize=17,color=teal)
ax.text(84,3,"An exact decoding example",ha="center",fontsize=10,color=ink)
for left,right in [(28,36),(62,68)]:
    ax.annotate("",xy=(right,24),xytext=(left,24),
                arrowprops={"arrowstyle":"->","color":ink,"lw":1.1})
for ext in ["pdf","svg","png"]:
    fig.savefig(DEST / "figures" / ("04_locked_boxes."+ext),dpi=220,
                facecolor="white")
plt.close(fig)
print("Built the locked-box schematic in PDF, SVG and PNG.")
