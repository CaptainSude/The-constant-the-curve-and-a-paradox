from pathlib import Path
import csv, json, math, hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT
FIG = STARTER / "figures"
FIG.mkdir(parents=True, exist_ok=True)
FONTS = STARTER / "fonts"
INK, TEAL, RUST, GREY = "#202a34", "#167b80", "#b35732", "#89929b"
PALE = "#edf4f4"
for fontfile in FONTS.glob("*.ttf"):
    font_manager.fontManager.addfont(str(fontfile))
plt.rcParams.update({
    "font.family": "STIX Two Text", "font.size": 11,
    "axes.labelcolor": INK, "text.color": INK, "axes.edgecolor": "#b9c0c5",
    "xtick.color": INK, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "svg.fonttype": "none", "pdf.fonttype": 42,
    "mathtext.fontset": "stix",
})
def primes_to(n):
    a = np.ones(n+1, dtype=bool); a[:2] = False
    for p in range(2, math.isqrt(n)+1):
        if a[p]: a[p*p::p] = False
    return np.flatnonzero(a).tolist()

def lam_and_lpf(nmax):
    lpf = np.zeros(nmax+1, dtype=int)
    for p in primes_to(nmax):
        for n in range(p, nmax+1, p):
            if not lpf[n]: lpf[n] = p
    lam = np.ones(nmax+1, dtype=int)
    for n in range(2, nmax+1):
        lam[n] = -lam[n // lpf[n]]
    return lam, lpf

def savefig(fig, name):
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

# Exact finite divisor experiment. The blocked lane is deliberately artificial.
lam, lpf = lam_and_lpf(240)
base = (1-lam)//2; base[0] = 0
toy = base.copy(); toy[lpf == 7] = 0
ns = np.arange(1, 49)
def divisor_counts(bits):
    return np.array([sum(1-2*int(bits[d]) for d in range(1,m+1) if m%d==0)
                     for m in ns])
cb, ct = divisor_counts(base), divisor_counts(toy)
assert np.array_equal(cb, np.array([int(math.isqrt(m)**2 == m) for m in ns]))
assert np.all(ct >= 0) and np.all(ct[ns % 7 == 0] >= 2)
assert np.all(base[4*np.arange(1,25)] == base[np.arange(1,25)])
with (FIG / "divisor_readings.csv").open("w", newline="") as f:
    w=csv.writer(f); w.writerow(["m","all_enabled_c_m","artificial_lane_7_blocked_c_m"])
    w.writerows(zip(ns,cb,ct))
fig = plt.figure(figsize=(7.2,4.6))
gs = fig.add_gridspec(3,1,height_ratios=[1.12,1,1],hspace=.7)
ax=fig.add_subplot(gs[0])
for row, vals, label in [(2,base[1:25],"All-enabled digits"),
                         (1,base[4*np.arange(1,25)],"Every fourth digit"),
                         (0,toy[1:25],"Toy: lane 7 blocked")]:
    for j,v in enumerate(vals):
        ischanged = row==0 and v != base[j+1]
        ax.text(j+1,row,str(v),ha="center",va="center",fontsize=10.5,
                color=RUST if ischanged else INK,
                bbox=dict(boxstyle="square,pad=.17",
                          facecolor="#f6e8df" if ischanged else ("#eaf3f3" if v else "white"),
                          edgecolor="none"))
    ax.text(-.5,row,label,ha="right",va="center",fontsize=10)
ax.set_xlim(0,25);ax.set_ylim(-.6,2.6);ax.axis("off")
for idx, counts, color, title in [(1,cb,TEAL,"Divisor sums: only squares remain"),
                                (2,ct,RUST,"Block lane 7: every multiple of 7 contributes")]:
    ax=fig.add_subplot(gs[idx]);ax.vlines(ns,0,counts,color=color,lw=1.5)
    ax.scatter(ns[counts>0],counts[counts>0],s=11,color=color,zorder=3)
    ax.set_xlim(0,49);ax.set_ylim(0, max(2.5,counts.max()+.5))
    ax.set_yticks([0,1,2] if idx==1 else [0,2,4,6])
    ax.set_ylabel(r"$c_m$",rotation=0,labelpad=13)
    ax.set_title(title,loc="left",fontsize=11,pad=6)
    if idx==2: ax.set_xlabel("Integer m")
savefig(fig,"01_digits_and_divisors")

# Positive-axis density preview. Conditional Monte Carlo; no certified density error claimed.
seed, samples, cutoff = 271828, 180000, 2000
rng=np.random.default_rng(seed)
pp=primes_to(cutoff)
logv=np.zeros(samples)
for p in pp[1:]:
    logv += math.log(p/(p-1)) - rng.exponential(size=samples)/(p-1)
q=np.sort(2*np.exp(logv)); weights=1/q
tail=np.r_[np.cumsum(weights[::-1])[::-1],0.0]/samples
grid=np.linspace(0,4.8,401)
fx=tail[np.searchsorted(q,grid,side="right")]
c2=float(np.prod([p*(p-2)/(p-1)**2 for p in pp[1:]]))
with (FIG / "density_preview.csv").open("w",newline="") as f:
    w=csv.writer(f);w.writerow(["x","conditional_mc_density"])
    w.writerows(zip(grid,fx))
fig=plt.figure(figsize=(7.2,3.5))
gs=fig.add_gridspec(2,1,height_ratios=[4,1.1],hspace=.58)
ax=fig.add_subplot(gs[0]);ax.plot(grid,fx,color=TEAL,lw=2)
ax.fill_between(grid,fx,alpha=.07,color=TEAL)
ax.set_xlim(0,4.8);ax.set_ylim(0,.85)
ax.set_xlabel("Positive value of W");ax.set_ylabel("Density")
ax.text(2.05,.66,"Coprimality determines the moments.\nPrimality determines Taylor support.",
        fontsize=11.5,linespacing=1.5)
ax.text(.05,.79,r"$f(0)=1/(2C_2)$",fontsize=12,color=TEAL)
ax=fig.add_subplot(gs[1]);vals=np.arange(2,32)
for n in vals:
    isp=n in pp
    ax.scatter(n,0,s=36,marker="o",facecolor=TEAL if isp else "white",
               edgecolor=TEAL if isp else "#aab1b7",lw=.8)
    ax.text(n,-.3,str(n),ha="center",va="top",fontsize=8)
ax.text(1,.35,"n + 2",ha="left",fontsize=10)
ax.text(16,.35,"Filled: the n-th derivative at zero is nonzero",ha="center",fontsize=10)
ax.set_xlim(1,32);ax.set_ylim(-.65,.65);ax.axis("off")
savefig(fig,"02_prime_density")

# Exact synchronous deletion in a closed finite window.
primes=primes_to(127); B=set(primes)-{7}; stages=[B.copy()]
deleted={p:(0 if p==7 else -1) for p in primes}
for k in range(1,9):
    new={p for i,p in enumerate(primes,1)
         if p in B and any(q in B and 2*(i+1)-q in B for q in B if q<=2*(i+1))}
    for p in B-new: deleted[p]=k
    stages.append(new.copy());B=new
assert B=={2,3,5}
expected_path=STARTER/"code"/"delete7_expected.csv"
if not expected_path.exists():
    expected_path=ROOT/"work"/"delete7_expected.csv"
if expected_path.exists():
    with expected_path.open(newline="",encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            p=int(row["prime"])
            assert deleted[p]==int(row["round"]), (p,deleted[p],row)
with (FIG/"delete7_rounds.csv").open("w",newline="") as f:
    w=csv.writer(f);w.writerow(["prime","deletion_round_minus1_means_survives"])
    w.writerows(sorted(deleted.items()))
fig=plt.figure(figsize=(7.2,4.7))
gs=fig.add_gridspec(2,2,height_ratios=[2.4,1.8],hspace=.72,wspace=.42)
ax=fig.add_subplot(gs[0,:])
showprimes=primes[:30]
for k in range(6):
    for j,p in enumerate(showprimes):
        alive=p in stages[k]
        ax.scatter(j,k,marker="s",s=75,color=TEAL if alive else "#eceeef",
                   edgecolor=TEAL if alive else "#d8dcdf",lw=.4)
        if p==7 and k==0:ax.scatter(j,k,marker="x",s=40,color=RUST,lw=1.3)
ax.set_xticks(range(30));ax.set_xticklabels(showprimes,rotation=90,fontsize=8)
ax.set_yticks(range(6));ax.invert_yaxis()
ax.set_xlabel("Prime (first 30 primes only)");ax.set_ylabel("Round")
ax.spines["left"].set_visible(False);ax.spines["bottom"].set_visible(False)
ax.set_title("Delete 7, then remove unsupported prime lanes",loc="left",fontsize=12)
ax=fig.add_subplot(gs[1,0])
x=np.arange(1,4);prob=np.array([1,9,6])/16
ax.bar(x,prob,color=[TEAL,TEAL,TEAL],width=.53)
for xx,y,label in zip(x,prob,["1/16","9/16","6/16"]):
    ax.text(xx,y+.022,label,ha="center",fontsize=11)
ax.set_ylim(0,.7);ax.set_xticks(x);ax.set_xlabel("Selected subset size")
ax.set_ylabel("Limiting probability")
ax.set_title("Infinite deletion first",loc="left",fontsize=11)
ax=fig.add_subplot(gs[1,1]);ax.axis("off")
ax.text(0,.92,"Three exact final readings",fontsize=12)
for y,text in [(.64,"Surviving prime lanes   {2, 3, 5}"),
               (.38,"Proportion of ones      11/30"),
               (.12,"Graph-operator rank     8")]:
    ax.text(0,y,text,fontsize=11)
savefig(fig,"03_delete_seven")

manifest={
  "title":"The constant, the curve and a paradox",
  "font_release":"STIX Two v2.13b171",
  "font_source":"https://github.com/stipub/stixfonts/tree/v2.13b171",
  "density_illustration":{"method":"conditional Monte Carlo for finite-prime product",
      "seed":seed,"samples":samples,"prime_cutoff":cutoff,"number_of_primes":len(pp),
      "estimated_f_zero":float(fx[0]),"finite_product_C2":c2,
      "warning":"Plot is an explicitly labelled finite-prime Monte Carlo preview; no certified approximation error or proof by plot is claimed."},
  "finite_examples":{"divisor_max":48,"artificial_blocked_prime":7,
      "delete7_max_prime":127,"shown_prime_count":30,"last_round_computed":8},
  "files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in FONTS.iterdir() if p.is_file()}
}
manifest_path = STARTER / "visual_data_manifest.json"
if manifest_path.exists():
    previous = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    manifest = {**previous, **manifest}
manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")


print("Rebuilt figures 01–03 and their numerical data.")
