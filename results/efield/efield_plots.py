"""E-field and path-sensitivity plots from the HFSS field exports (healthy uniform head, 3.6 GHz).
Run from anywhere:  python results/efield/efield_plots.py   (needs data/fields/, which is not in git)
Writes efield_overview.png and efield_paths_profile.png next to this script. Viewing only; not part of any analysis.
"""
import numpy as np, matplotlib
import pandas as pd
def load(path):
    hdr=open(path).readline()
    import re
    mn=[float(v) for v in re.findall(r"Min: \[(-?\d+)mm (-?\d+)mm (-?\d+)mm\]",hdr)[0]]
    st=float(re.findall(r"Grid Size: \[(\d+)mm",hdr)[0])
    d=pd.read_csv(path,sep=r"\s+",skiprows=2,header=None,engine="c",na_values=["Nan"],dtype=float).to_numpy()
    n=round(len(d)**(1/3)); assert n**3==len(d)
    E=(d[:,3::2]+1j*d[:,4::2]).reshape(n,n,n,3)        # x outer, y, z fastest
    ax=np.round(d[:n**2*0+n,2]*1000,3)
    return E, mn[0]+st*np.arange(n), st

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.ndimage import map_coordinates
plt.rcParams.update({"font.size":12,"axes.titlesize":13,"axes.titleweight":"semibold","figure.facecolor":"white"})
import os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # repo root
FIELDS=os.path.join(ROOT,"data","fields")
OUT=os.path.dirname(os.path.abspath(__file__))
def get(k):
    E,g,_=load(os.path.join(FIELDS,f"E_Normal_{k}.fld")); return E,g
Ew,gw=get("T1_3p6GHz_wide"); E1,g=get("T1_3p6GHz"); E4,_=get("T4_3p6GHz"); E2,_=get("T2_3p6GHz")
az=np.deg2rad([-90.4,-30.4,29.6,89.6,149.6,-150.4]); RH=97.7*np.sin(np.deg2rad(60.5)); ZF=97.7*np.cos(np.deg2rad(60.5))
def idx(grid,v): return int(np.argmin(abs(grid-v)))
def db(a,ref=None):
    a=np.abs(a); ref=np.nanmax(a) if ref is None else ref
    return 20*np.log10(np.maximum(a,1e-30)/ref)
CM=plt.get_cmap("Blues").copy(); CM.set_bad("#d9d9d9")
def outline_h(ax,z):
    for r,ls,lab in [(88,"-","skin"),(83,"--","brain surface"),(25,":","hippocampus")]:
        if r>abs(z): ax.add_patch(Circle((0,0),np.sqrt(r*r-z*z),fill=False,ec="#2b2b2a",lw=1.1,ls=ls))
    for i,a in enumerate(az):
        x,y=RH*np.cos(a),RH*np.sin(a); ax.plot(x,y,"s",ms=7,mfc="#eb6834",mec="white",mew=1.2)
        ax.text(0.83*x,0.83*y,f"T{i+1}",ha="center",va="center",fontsize=10,color="#7a2d0a",weight="bold")
def outline_v(ax):
    for r,ls in [(88,"-"),(83,"--"),(25,":")]: ax.add_patch(Circle((0,0),r,fill=False,ec="#2b2b2a",lw=1.1,ls=ls))
    for s,t in [(-1,"T1"),(1,"T4")]:
        ax.plot(s*RH,ZF,"s",ms=7,mfc="#eb6834",mec="white",mew=1.2); ax.text(s*RH*0.8,ZF-9,t,ha="center",fontsize=10,color="#7a2d0a",weight="bold")
def show(ax,img,grid,title,xl,yl,vmin=-80):
    m=ax.imshow(img.T,origin="lower",extent=[grid[0],grid[-1],grid[0],grid[-1]],cmap=CM,vmin=vmin,vmax=0,interpolation="bilinear")
    ax.set_title(title,loc="left"); ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_aspect("equal"); return m

fig,axs=plt.subplots(2,2,figsize=(14,13))
zi=idx(gw,48); xi=idx(gw,0)
m=show(axs[0,0],db(np.linalg.norm(Ew[:,:,zi,:],axis=-1)),gw,"(a) T1 transmitting: |E|, ring plane z = 48 mm","x (mm)  → subject's left","y (mm)  (front = −y)")
outline_h(axs[0,0],48)
show(axs[0,1],db(np.linalg.norm(Ew[xi,:,:,:],axis=-1)),gw,"(b) T1 transmitting: |E|, vertical cut x = 0","y (mm)  (T1 front, T4 back)","z (mm)")
outline_v(axs[0,1])
zi=idx(g,48); xi=idx(g,0)
S=np.abs(np.sum(E1*E4,axis=-1))
mc=show(axs[1,0],db(S[:,:,zi]),g,"(c) T1–T4 path sensitivity |E₁·E₄|, ring plane","x (mm)","y (mm)",vmin=-110)
outline_h(axs[1,0],48); axs[1,0].set_xlim(-90,90); axs[1,0].set_ylim(-90,90)
show(axs[1,1],db(S[xi,:,:]),g,"(d) T1–T4 path sensitivity, vertical cut x = 0","y (mm)","z (mm)",vmin=-110)
outline_v(axs[1,1]); axs[1,1].set_xlim(-90,90); axs[1,1].set_ylim(-90,90)
# arc vs chord comparison (ring plane)
Sz=S[:,:,zi]; ref=np.nanmax(Sz)
p_arc=Sz[idx(g,80),idx(g,0)]; p_arc2=Sz[idx(g,-80),idx(g,0)]; p_ch=Sz[idx(g,0),idx(g,0)]
for (x,y,v,lab) in [(80,0,p_arc,"side, in air"),(-80,0,p_arc2,"side, in air"),(0,0,p_ch,"centre")]:
    axs[1,0].plot(x,y,"o",ms=7,mfc="none",mec="#e34948",mew=2)
    axs[1,0].annotate(f"{20*np.log10(v/ref):.0f} dB",(x,y),xytext=(x+(-30 if x>0 else 4 if x<0 else -12),y+7),fontsize=11,color="#b3261e",weight="semibold")
fig.colorbar(m,ax=axs[0,:],shrink=0.85,pad=0.02,label="|E| in dB, relative to the panel maximum")
fig.colorbar(mc,ax=axs[1,:],shrink=0.85,pad=0.02,label="sensitivity in dB, relative to the panel maximum")
fig.suptitle("HFSS field exports, healthy uniform head, 3.6 GHz (for viewing only)",fontsize=15,weight="bold",x=0.45,y=0.93)
fig.savefig(os.path.join(OUT,"efield_overview.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print("arc vs centre (dB rel max):",20*np.log10(p_arc/ref),20*np.log10(p_arc2/ref),20*np.log10(p_ch/ref))

# figure 2: neighbour sensitivity + radial profile into the head under T1
fig,axs=plt.subplots(1,2,figsize=(15,6.6),gridspec_kw={"width_ratios":[1,1.25]})
S2=np.abs(np.sum(E1*E2,axis=-1))
mm=show(axs[0],db(S2[:,:,zi]),g,"(e) T1–T2 (neighbour) path sensitivity, ring plane","x (mm)","y (mm)",vmin=-110)
outline_h(axs[0],48); axs[0].set_xlim(-90,90); axs[0].set_ylim(-90,90)
fig.colorbar(mm,ax=axs[0],shrink=0.8,label="dB rel. max")
u=np.array([np.sin(np.deg2rad(60.5))*np.cos(az[0]),np.sin(np.deg2rad(60.5))*np.sin(az[0]),np.cos(np.deg2rad(60.5))])
r=np.linspace(110,0,441); P=r[:,None]*u[None,:]
A=np.linalg.norm(Ew,axis=-1); A=np.where(np.isnan(A),np.nanmean(A),A)
coords=((P-gw[0])/(gw[1]-gw[0])).T
prof=map_coordinates(A,coords,order=1)
ax=axs[1]
for lo,hi,c,lab,yy in [(88,110,"#ffffff","air gap\n(antenna at ~97)",2),(83.5,88,"#e9dfd6","skin,\nfat,\nskull",-62),(76,83.5,"#e7d6e0","CSF +\ngray",-74),(25,76,"#f3eee4","white matter",2),(0,25,"#f6dcc8","hippocampus",2)]:
    ax.axvspan(lo,hi,color=c,zorder=0); ax.text((lo+hi)/2,yy,lab,ha="center",va="top",fontsize=9.5,color="#52514e")
pdb=20*np.log10(prof/prof.max())
ax.plot(r,pdb,color="#1c5cab",lw=2)
ins=(r<=80)&(r>=55); k=np.polyfit(r[ins],pdb[ins],1)[0]
ax.plot(r[ins],np.polyval(np.polyfit(r[ins],pdb[ins],1),r[ins]),color="#e34948",lw=1.5,ls="--")
ax.text(66,np.polyval(np.polyfit(r[ins],pdb[ins],1),66)+4,f"≈ {abs(k)*10:.1f} dB per cm inside the brain",color="#b3261e",fontsize=11)
ax.set_xlim(110,0); ax.set_ylim(min(-80,pdb.min()-2),6); ax.set_xlabel("distance from head centre along T1's axis (mm)  →  deeper")
ax.set_ylabel("|E| from T1 (dB rel. max)"); ax.set_title("(f) How fast T1's field fades going into the head",loc="left"); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"efield_paths_profile.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print("profile slope dB/cm:",k*10, " field at brain surface r=83 vs r=60:", np.interp(83,r[::-1],pdb[::-1]), np.interp(60,r[::-1],pdb[::-1]))
