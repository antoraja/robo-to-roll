import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_parts import *
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def finger_world(curl):
    # chain in local coords, each joint rotates by -curl about pin (0,ZP) => toward -z
    parts=[]; T=np.eye(4)
    def rotY(deg, pz):
        a=math.radians(deg); M=np.eye(4)
        # rotation in x-z plane about point (0,pz): positive deg -> toward +z ; we want toward -z
        c,s=math.cos(a),math.sin(a)
        R_=np.array([[c,0,-s,0],[0,1,0,0],[s,0,c,0],[0,0,0,1]])
        Tm=np.eye(4); Tm[2,3]=-pz; Tp=np.eye(4); Tp[2,3]=pz
        return Tp@R_@Tm
    for L,dist in ((L_PROX,False),(L_MID,False),(L_DIST,True)):
        T=T@rotY(-curl,ZP)
        p=phalanx(L,distal=dist)
        parts.append(p.transform(T[:3,:].tolist()))
        Tl=np.eye(4); Tl[0,3]=L; T=T@Tl
    out=parts[0]+parts[1]+parts[2]
    return local_to_world(out)

def tm_of(p):
    mm=p.to_mesh(); return np.asarray(mm.vert_properties)[:,:3], np.asarray(mm.tri_verts)

b,info=base()
sx,sz=info['spool_center_xz']
sp=spool().rotate((-90,0,0)).translate((sx,-4.2,sz))
servo=box(sx-6.1, sx-6.1+22.8, -16-16, -16+4.3+2.5, sz-6.1, sz+6.1)
fig=plt.figure(figsize=(14,7))
for i,(curl,el,az) in enumerate([(0,15,-60),(60,10,-90)]):
    ax=fig.add_subplot(1,2,i+1,projection='3d')
    for p,col,al in ((b,'#bbbbbb',1),(finger_world(curl),'#f0a040',1),(sp,'#4080f0',1),(servo,'#303030',0.5)):
        v,f=tm_of(p); ax.add_collection3d(Poly3DCollection(v[f],facecolors=col,alpha=al,shade=True))
    ax.set_xlim(-60,60); ax.set_ylim(-60,60); ax.set_zlim(-60,120); ax.set_box_aspect((1,1,1.5)); ax.view_init(el,az)
    ax.set_title(f'curl {curl} deg / joint')
    # collision check finger vs base
    inter=(finger_world(curl)^b).volume(); print('curl',curl,'finger/base overlap',round(inter,2),'spool/base',round((sp^b).volume(),2),'servo/base',round((servo^b).volume(),2))
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=80)
