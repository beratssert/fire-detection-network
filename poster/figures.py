import math, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import params
plt.rcParams.update({"font.family":"DejaVu Sans","pdf.fonttype":42,"font.size":22,
 "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#6b6a66","axes.linewidth":1.4,
 "xtick.color":"#3d3c39","ytick.color":"#3d3c39","axes.labelcolor":"#1c1c1a","axes.grid":True,
 "grid.color":"#dcdad3","grid.linewidth":1.0,"xtick.major.size":0,"ytick.major.size":0,"xtick.minor.size":0,"ytick.minor.size":0,
 "axes.labelsize":22,"xtick.labelsize":20,"ytick.labelsize":20,"legend.frameon":False,"legend.fontsize":19})
B,O,A,Y,INK,MUT="#2a78d6","#eb6834","#1baf7a","#eda100","#1c1c1a","#52514e"
FS=(9.6,4.7)
def fig():
    f,a=plt.subplots(figsize=FS); f.subplots_adjust(left=.12,right=.76,top=.96,bottom=.19); return f,a
def lab(a,x,y,t,dy=0,dx=12): a.annotate(t,(x,y),xytext=(dx,dy),textcoords="offset points",va="center",fontsize=19,color=INK,fontweight="bold")
def save(f,n): f.savefig(f"figures/{n}.pdf"); f.savefig(f"figures/{n}.png",dpi=110); plt.close(f)

# 1 range (M1): 90 % link range per deployment and radio scenario; trunk curves also show the rear (through-trunk) range
r=pd.read_csv("results/range.csv"); f,a=fig(); f.subplots_adjust(right=.97)
for ((dep,scen),txt),c,m in zip(params.FIG1_CURVES,(B,B,O,O),("o","s","^","v")):
    d=r[(r.deploy==dep)&(r.scen==scen)]; ls="-" if scen=="opt" else (0,(5,2))
    if (dep,scen)==params.RADIO_UPPER:     # A1: unverified upper bound, drawn thin and grey
        a.plot(d.sf,d.range90_m,color=MUT,lw=1.8,ls=(0,(2,2)),marker=m,ms=7,mfc="white",mec=MUT,label=txt); continue
    a.plot(d.sf,d.range90_m,color=c,lw=3,ls=ls,marker=m,ms=10,mec="white",mew=1.8,label=txt)
    if dep=="M" and scen=="cons":
        a.plot(d.sf,d.range90_rear_m,color=c,lw=1.8,ls=(0,(1,2)),label="trunk, conservative, rear")
a.plot([params.FERREIRA_SF],[params.FERREIRA_D_MAX_M],ls="none",marker="X",ms=13,color=INK,label="measured limit, rainforest (915 MHz)")
a.plot([params.BOONLOM_SF],[params.BOONLOM_D_MAX_M],ls="none",marker="D",ms=10,mfc="white",mec=INK,mew=2,label="measured link, GW at 8 m (923 MHz)")
a.legend(loc="lower right",ncol=2,fontsize=12.5,handlelength=2.0,columnspacing=0.8)
a.set_ylim(12,3500)
a.set_yscale("log"); a.set_yticks([100,200,500,1000,2000]); a.set_yticklabels(["100","200","500","1000","2000"])
a.set_xlabel(params.FIG1_XLABEL); a.set_ylabel("90 % link range (m)")
a.set_xticks(range(7,13)); save(f,"f1_range")

# 2 connectivity (M2): fraction of nodes reaching a gateway, SF7, conservative scenarios, G = 1 and 4, 95 % CI band
c=pd.read_csv("results/connectivity.csv"); f,a=fig(); f.subplots_adjust(right=.97); a.set_xscale("log")
c=c[(c.sf==params.FIG2_SF)&(c.area_ha==round(params.SIDE_M**2/1e4))]
for ((dep,scen),g),col,ls in zip(params.FIG2_CURVES,(B,B,O,O),("-",(0,(5,2)),"-",(0,(5,2)))):
    d=c[(c.deploy==dep)&(c.scen==scen)&(c.gw==g)].sort_values("density_per_ha")
    lbl=("trunk" if dep=="M" else "scattered")+f", {scen}., G = {g}"
    a.plot(d.density_per_ha,d.reach_mean,color=col,lw=3,ls=ls,marker="o",ms=7,mec="white",mew=1.2,label=lbl)
    a.fill_between(d.density_per_ha,d.reach_mean-d.reach_ci95,np.minimum(d.reach_mean+d.reach_ci95,1),color=col,alpha=.15,lw=0)
a.axhline(params.CONN_REACH_TARGET,color=MUT,ls=":",lw=1.4)
a.set_xticks([0.05,0.1,0.2,0.5,1,2,5]); a.set_xticklabels(["0.05","0.1","0.2","0.5","1","2","5"])
a.set_xlabel("sensor density (nodes / ha)"); a.set_ylabel("reach fraction")
a.legend(loc="lower right",fontsize=14,handlelength=2.2)
a.set_ylim(-0.03,1.05); save(f,"f2_connectivity")

# 3 detection (M3): P(detected within T_BASE) vs density; heat-only band over r_T, gas designs at R_T_BASE
d=pd.read_csv("results/detection.csv"); f,a=fig(); f.subplots_adjust(right=.97); a.set_xscale("log")
h=d[d.design=="heat"]; lo=h[h.r_T_m==min(params.R_T_SCEN)]; hi=h[h.r_T_m==max(params.R_T_SCEN)]; md=h[h.r_T_m==params.R_T_BASE]
a.fill_between(lo.density_per_ha,lo.p_detect,hi.p_detect.values,color=Y,alpha=.25,lw=0)
a.plot(md.density_per_ha,md.p_detect,color=Y,lw=3,label=f"heat only, r_T = {params.R_T_SCEN[0]:g}–{params.R_T_SCEN[-1]:g} m")
for rg,col in zip(params.R_G_SCEN,(A,O,B)):
    e=d[(d.design=="gas")&(d.r_G_m==rg)]
    a.plot(e.density_per_ha,e.p_detect,color=col,lw=3,marker="o",ms=7,mec="white",mew=1.2,label=f"gas r_G = {rg:g} m")
a.axhline(params.DETECT_TARGET_P,color=MUT,ls=":",lw=1.4)
a.set_xticks([0.1,0.3,1,3,10,30]); a.set_xticklabels(["0.1","0.3","1","3","10","30"])
a.set_xlabel("sensor density (nodes / ha)"); a.set_ylabel(f"P(detected ≤ {params.T_BASE:g} min)")
a.legend(loc="upper left",fontsize=15,handlelength=1.6); a.set_ylim(0,1.05); save(f,"f3_detection")

# 4 required density (M3): vs deadline T at ROS_BASE and R_T_BASE (ROS range is reported in the poster table)
q=pd.read_csv("results/required_density.csv"); q=q[q.theta_deg.isin([0,round(math.degrees(params.THETA))])&(q.r_T_m==params.R_T_BASE)]
f,a=fig(); f.subplots_adjust(right=.97)
for (kind,rg),col,lbl in zip([("heat",0.0)]+[("gas",x) for x in params.R_G_SCEN],(Y,A,O,B),
                             ["heat only"]+[f"gas r_G = {x:g} m" for x in params.R_G_SCEN]):
    e=q[(q.design==kind)&(q.r_G_m==rg)]
    base=e[e.ros==params.ROS_BASE].sort_values("T_min")
    a.plot(base.T_min,base.req_density_per_ha,color=col,lw=3,marker="o",ms=8,mec="white",mew=1.2,label=lbl)
mada=params.VENDOR_DRYAD_MADA_SENSORS/params.VENDOR_DRYAD_MADA_HA
a.axhline(mada,color=MUT,ls=(0,(4,2)),lw=1.6); a.text(16,mada*1.12,"Dryad Mada (vendor)",fontsize=14,color=MUT)
a.set_yscale("log"); a.set_ylim(0.6,60); a.set_yticks([1,3,10,30]); a.set_yticklabels(["1","3","10","30"])
a.set_xticks(params.T_SCEN); a.set_xticklabels([f"{t:g}" for t in params.T_SCEN])
a.set_xlabel("detection deadline T (min)"); a.set_ylabel(f"nodes / ha for {params.DETECT_TARGET_P:.0%}")
a.legend(loc="upper right",fontsize=14,ncol=2); save(f,"f4_required")

# 5 energy (M5): average node power (log) for leaf / relays, T_w 2 s vs 30 s, scattered conservative, G = 1, 25 C
e=pd.read_csv("results/energy.csv"); e=e[(e.deploy=="S")&(e.gw==1)&(e.temp=="25C")]
f,a=fig(); f.subplots_adjust(left=.30,right=.97,top=.86)
labels=[]; ypos=0; yt=[]
names={("heat","leaf"):"heat, leaf",("gas","leaf"):"gas, leaf",("gas","relay_mean"):"gas, mean relay",("gas","relay_max"):"gas, busiest relay"}
for (des,role) in params.FIG5_CASES:
    for slot,col,dy in (("opt",B,-0.18),("cons",O,0.18)):
        r=e[(e.design==des)&(e.role==role)&(e.slot==slot)].iloc[0]
        a.barh(ypos+dy,r.p_avg_mW,height=0.34,color=col,label=f"T_w = {params.SLOT_TW_S[slot]:g} s" if ypos==0 else None)
    yt.append(ypos); labels.append(names[(des,role)]); ypos+=1
for k,ls in (("low",":"),("high","--")):
    a.axvline(params.P_HARVEST_MW[k],color="#14532d",ls=ls,lw=1.8)
    a.text(params.P_HARVEST_MW[k],1.02,f"PV {k}",fontsize=14,color="#14532d",ha="center",va="bottom",transform=a.get_xaxis_transform())
cap,sd=params.BATT["Li-SOCl2 AA (2.6 Ah)"]; p10=(cap*3600/(10*params.YEAR)-sd*cap*3600/params.YEAR)*params.V*1e3
a.axvline(p10,color=MUT,ls=(0,(1,2)),lw=1.8); a.text(p10,1.02,"AA 10 yr",fontsize=14,color=MUT,ha="center",va="bottom",transform=a.get_xaxis_transform())
a.set_xscale("log"); a.set_yticks(yt); a.set_yticklabels(labels); a.invert_yaxis()
a.set_xticks([0.01,0.03,0.1,0.3,1]); a.set_xticklabels(["0.01","0.03","0.1","0.3","1"])
a.set_xlabel("average node power (mW)"); a.legend(loc="upper right",fontsize=15)
a.grid(axis="y",visible=False); save(f,"f5_energy")
print("ok")
