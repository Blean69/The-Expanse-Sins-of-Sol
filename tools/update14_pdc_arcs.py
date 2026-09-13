"""Offline outgoing-ray audit and rectangular Raptor/Pella PDC arc proposal.

Read-only game/assets. Only writes the caller-selected audit/build directories.
Uses a double-precision, two-sided triangle BVH; no graphics backface assumptions.
"""
from pathlib import Path
import argparse, ctypes, hashlib, json, math, subprocess
import numpy as np

CPP = r'''
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>
struct V { double x[3]; };
V sub(V a,V b){V c;for(int k=0;k<3;k++)c.x[k]=a.x[k]-b.x[k];return c;}
V cross(V a,V b){return V{{a.x[1]*b.x[2]-a.x[2]*b.x[1],a.x[2]*b.x[0]-a.x[0]*b.x[2],a.x[0]*b.x[1]-a.x[1]*b.x[0]}};}
double dot(V a,V b){double v=0;for(int k=0;k<3;k++)v+=a.x[k]*b.x[k];return v;}
struct T {V a,e1,e2,lo,hi,c;};
struct N {V lo,hi;int begin,end,left=-1,right=-1;};
struct Tree {
std::vector<T> ts;std::vector<int> ids;std::vector<N> ns;
int build(int a,int b){N n;n.begin=a;n.end=b;for(int k=0;k<3;k++){n.lo.x[k]=1e100;n.hi.x[k]=-1e100;}
for(int i=a;i<b;i++)for(int k=0;k<3;k++){n.lo.x[k]=std::min(n.lo.x[k],ts[ids[i]].lo.x[k]);n.hi.x[k]=std::max(n.hi.x[k],ts[ids[i]].hi.x[k]);}
int me=ns.size();ns.push_back(n);if(b-a<=8)return me;int axis=0;for(int k=1;k<3;k++)if(n.hi.x[k]-n.lo.x[k]>n.hi.x[axis]-n.lo.x[axis])axis=k;
int mid=(a+b)/2;std::nth_element(ids.begin()+a,ids.begin()+mid,ids.begin()+b,[&](int i,int j){return ts[i].c.x[axis]<ts[j].c.x[axis];});
int l=build(a,mid),r=build(mid,b);ns[me].left=l;ns[me].right=r;return me;}
bool box(const N&n,V o,V d,double best){double low=0,high=best;for(int k=0;k<3;k++){if(std::abs(d.x[k])<1e-15){if(o.x[k]<n.lo.x[k]-1e-8||o.x[k]>n.hi.x[k]+1e-8)return false;continue;}
double a=(n.lo.x[k]-1e-8-o.x[k])/d.x[k],b=(n.hi.x[k]+1e-8-o.x[k])/d.x[k];if(a>b)std::swap(a,b);low=std::max(low,a);high=std::min(high,b);if(low>high)return false;}return true;}
void visit(int ni,V o,V d,double&best){const N&n=ns[ni];if(!box(n,o,d,best))return;if(n.left>=0){visit(n.left,o,d,best);visit(n.right,o,d,best);return;}
for(int j=n.begin;j<n.end;j++){const T&t=ts[ids[j]];V p=cross(d,t.e2);double det=dot(t.e1,p);if(std::abs(det)<1e-12)continue;double inv=1/det;V s=sub(o,t.a);double u=dot(s,p)*inv;if(u< -1e-8||u>1+1e-8)continue;V q=cross(s,t.e1);double v=dot(d,q)*inv;if(v< -1e-8||u+v>1+1e-8)continue;double hit=dot(t.e2,q)*inv;if(hit>1e-5&&hit<best)best=hit;}}
};
extern "C" void* make_tree(const double*p,int count){Tree*t=new Tree;for(int i=0;i<count;i++){V a,b,c;for(int k=0;k<3;k++){a.x[k]=p[i*9+k];b.x[k]=p[i*9+3+k];c.x[k]=p[i*9+6+k];}T q;q.a=a;q.e1=sub(b,a);q.e2=sub(c,a);for(int k=0;k<3;k++){q.lo.x[k]=std::min({a.x[k],b.x[k],c.x[k]});q.hi.x[k]=std::max({a.x[k],b.x[k],c.x[k]});q.c.x[k]=(a.x[k]+b.x[k]+c.x[k])/3;}t->ts.push_back(q);t->ids.push_back(i);}t->build(0,count);return t;}
extern "C" void destroy_tree(void*p){delete (Tree*)p;}
extern "C" void rays(void*p,const double*os,const double*ds,int count,double limit,double*out){Tree*t=(Tree*)p;for(int i=0;i<count;i++){V o,d;for(int k=0;k<3;k++){o.x[k]=os[3*i+k];d.x[k]=ds[3*i+k];}double best=limit;t->visit(0,o,d,best);out[i]=best<limit?best:-1;}}
'''


class Rays:
    def __init__(self, tri, build):
        build.mkdir(parents=True, exist_ok=True)
        source, binary = build/'ray-bvh.cpp', build/'ray-bvh.so'
        if not source.exists() or source.read_text() != CPP or not binary.exists():
            source.write_text(CPP)
            subprocess.run(['g++','-O3','-std=c++17','-shared','-fPIC',str(source),'-o',str(binary)],check=True)
        self.lib=ctypes.CDLL(str(binary)); ptr=ctypes.POINTER(ctypes.c_double)
        self.lib.make_tree.argtypes=[ptr,ctypes.c_int];self.lib.make_tree.restype=ctypes.c_void_p
        self.lib.rays.argtypes=[ctypes.c_void_p,ptr,ptr,ctypes.c_int,ctypes.c_double,ptr]
        self.lib.destroy_tree.argtypes=[ctypes.c_void_p]
        tri=np.ascontiguousarray(tri,dtype=np.float64);self.handle=self.lib.make_tree(tri.ctypes.data_as(ptr),len(tri));self.ptr=ptr

    def __call__(self, origin, direction, limit=4500.):
        origin=np.ascontiguousarray(origin,dtype=np.float64);direction=np.ascontiguousarray(direction,dtype=np.float64)
        out=np.zeros(len(origin));self.lib.rays(self.handle,origin.ctypes.data_as(self.ptr),direction.ctypes.data_as(self.ptr),len(origin),limit,out.ctypes.data_as(self.ptr));return out

    def close(self):
        self.lib.destroy_tree(self.handle)


def pose(mount,turret,yaw,pitch,dyaw=0.,dpitch=0.):
    """Column vectors: B @ Ry(yaw) @ Rx(pitch); +pitch aims toward -up."""
    up=np.array(mount['up']);forward=np.array(mount['forward']);B=np.column_stack([np.cross(up,forward),up,forward])
    assert np.allclose(B.T@B,np.eye(3),atol=1e-7) and np.linalg.det(B)>.999999
    y,p=np.radians(yaw),np.radians(pitch);off=np.array(turret['barrel_position']);m=np.array(turret['muzzle_positions'][0])
    pitched=np.column_stack([np.full(len(y),m[0]),np.cos(p)*m[1]-np.sin(p)*m[2],np.sin(p)*m[1]+np.cos(p)*m[2]])+off
    turned=np.column_stack([np.cos(y)*pitched[:,0]+np.sin(y)*pitched[:,2],pitched[:,1],-np.sin(y)*pitched[:,0]+np.cos(y)*pitched[:,2]])
    origin=turned@B.T+mount['weapon_position'];y,p=np.radians(yaw+dyaw),np.radians(pitch+dpitch)
    direction=np.column_stack([np.sin(y)*np.cos(p),-np.sin(p),np.cos(y)*np.cos(p)])@B.T
    return origin,direction


def sample(ray,mount,turret,yaws,pitches,tolerance):
    yy,pp=np.meshgrid(yaws,pitches);yy=yy.ravel();pp=pp.ravel();blocked=np.zeros(len(yy),bool);first=None;total=0
    offsets=[(0.,0.)] if tolerance==0 else [(a,b) for a in [-tolerance,0.,tolerance] for b in [-tolerance,0.,tolerance]]
    for dy,dp in offsets:
        o,d=pose(mount,turret,yy,pp,dy,dp);hit=ray(o,d);bad=hit>0;blocked|=bad;total+=len(hit)
        if first is None and bad.any():
            j=int(np.flatnonzero(bad)[0]);first={'yaw':float(yy[j]),'pitch':float(pp[j]),'direction_yaw_offset':dy,'direction_pitch_offset':dp,'distance_from_muzzle':float(hit[j]),'muzzle':o[j].tolist(),'direction':d[j].tolist(),'intersection':(o[j]+hit[j]*d[j]).tolist()}
    return blocked.reshape(len(pitches),len(yaws)),first,total


def choose(mask,yaws,pitches):
    # A rectangular native arc containing neutral yaw; retain full outward elevation.
    # Grid-edge inset 2 degrees; extra 3-degree outgoing direction envelope sampled.
    best=None
    for row,pmax in enumerate(pitches):
        if pmax < -65 or pmax > -5:continue
        safe=~mask[:row+1].any(0);z=int(np.argmin(abs(yaws)))
        if not safe[z]:continue
        left=right=z
        while left>0 and safe[left-1]:left-=1
        while right<len(yaws)-1 and safe[right+1]:right+=1
        lo=float(yaws[left]+(2 if left>0 else 0));hi=float(yaws[right]-(2 if right<len(yaws)-1 else 0));pmax=float(pmax-2)
        if hi-lo<30:continue
        area=math.radians(hi-lo)*(math.sin(math.radians(85))-math.sin(math.radians(-pmax)))
        if best is None or area>best[0]:best=(area,lo,hi,pmax)
    if best is None:raise ValueError('No safe useful forward-containing rectangle')
    return {'yaw_arc':{'min_angle':best[1],'max_angle':best[2]},'pitch_arc':{'min_angle':-85.,'max_angle':best[3]}},best[0]


def self_check(build):
    tri=np.array([[[-1,-1,2],[1,-1,2],[0,1,2]]],float)
    for triangles in [tri,tri[:,[0,2,1]]]:
        r=Rays(triangles,build);v=r([[0,0,0],[0,0,4],[2,0,0]],[[0,0,1],[0,0,-1],[0,0,1]])
        assert np.allclose(v,[2,2,-1]);assert r([[0,0,0]],[[0,0,1]],1)[0]<0;r.close()
    return 'PASS: both windings, both ray directions, miss and range cutoff'


def independent_check(ray,tri,mount,turret):
    """Brute-force NumPy comparison validates BVH culling/traversal independently."""
    rng=np.random.default_rng(140014);y=rng.uniform(-180,180,64);p=rng.uniform(-30,5,64)
    origins,directions=pose(mount,turret,y,p);actual=ray(origins,directions);expected=[]
    e1,e2=tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]
    for origin,direction in zip(origins,directions):
        h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);good=abs(det)>1e-12
        inv=np.divide(1.,det,out=np.zeros_like(det),where=good);s=origin-tri[:,0]
        u=np.einsum('ij,ij->i',s,h)*inv;q=np.cross(s,e1);v=np.einsum('ij,j->i',q,direction)*inv
        t=np.einsum('ij,ij->i',e2,q)*inv;good&=(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-5)&(t<4500)
        expected.append(float(t[good].min()) if good.any() else -1.)
    assert np.allclose(actual,expected,atol=1e-7),list(zip(actual,expected))
    return {'rays':64,'blocked':int((actual>0).sum()),'result':'PASS BVH equals independent brute-force NumPy nearest intersections'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--hull',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--audit',type=Path,required=True);ap.add_argument('--build',type=Path,required=True);ap.add_argument('--variant',choices=['raptor','pella'],default='raptor');args=ap.parse_args()
    args.audit.mkdir(parents=True,exist_ok=True);identity='expanse12_'+args.variant
    tri=np.load(args.hull)['tri'];ray=Rays(tri,args.build);checks=self_check(args.build)
    unit=json.loads((args.baseline/'entities'/(identity+'.unit')).read_text());mounts=[w for w in unit['weapons']['weapons'] if '_pdc_' in w['weapon']];assert len(mounts)==9
    entries=[];yaws=np.arange(-180,181,2.);pitches=np.arange(-85,6,2.);independent=None
    for mount in mounts:
        weapon=json.loads((args.baseline/'entities'/(mount['weapon']+'.weapon')).read_text());turret=weapon['turret']
        if independent is None:independent=independent_check(ray,tri,mount,turret)
        old,example,nold=sample(ray,mount,turret,yaws,pitches,7.5)
        mask,_,nsearch=sample(ray,mount,turret,yaws,pitches,3.)
        arcs,area=choose(mask,yaws,pitches)
        ya,pa=arcs['yaw_arc'],arcs['pitch_arc'];new,after,nnew=sample(ray,mount,turret,np.arange(ya['min_angle'],ya['max_angle']+1,1.),np.arange(pa['min_angle'],pa['max_angle']+1,1.),3.)
        assert not new.any(),(mount['weapon'],after)
        rng=np.random.default_rng(140000+len(entries));ry=rng.uniform(ya['min_angle'],ya['max_angle'],20000);rp=rng.uniform(pa['min_angle'],pa['max_angle'],20000)
        ro,rd=pose(mount,turret,ry,rp,rng.uniform(-3,3,20000),rng.uniform(-3,3,20000));random_hits=ray(ro,rd);assert not (random_hits>0).any(),(mount['weapon'],'random between-grid obstruction')
        entry={'weapon':mount['weapon'],'old_mount_arcs':{k:mount[k]for k in ['yaw_arc','pitch_arc']},'mount_overrides':arcs,'weapon_overrides':{'yaw_firing_tolerance':1.,'pitch_firing_tolerance':1.},'old_sampled_blocked_poses':int(old.sum()),'old_sampled_poses':int(old.size),'old_ray_count':nold,'old_example':example,'search_ray_count':nsearch,'new_sampled_blocked_poses':int(new.sum()),'new_sampled_poses':int(new.size),'new_ray_count':nnew,'retained_solid_angle_fraction':area/(2*math.pi*(math.sin(math.radians(85))+math.sin(math.radians(5))))}
        entry['random_between_grid_rays']=20000;entry['random_blocked_rays']=int((random_hits>0).sum())
        entries.append(entry);print(mount['weapon'],arcs,'old blocked',int(old.sum()),'new',int(new.sum()),flush=True)
        (args.build/(identity+'-progress.json')).write_text(json.dumps(entries,indent=2)+'\n')
    ray.close()
    report={'status':'PASS OFFLINE SAMPLED RAYS; runtime NOT RUN','identity':identity,'hull_source':str(args.hull),'hull_sha256':hashlib.sha256(args.hull.read_bytes()).hexdigest(),'triangle_count':len(tri),'self_check':checks,'coordinate_convention':'Right-handed game coordinates +Z forward, +Y up; B columns right=cross(up,forward), up, forward. Muzzle=pivot+B*Ry(yaw)*(barrel_position+Rx(pitch)*muzzle_position); outgoing ray=B*Ry(yaw+delta_yaw)*Rx(pitch+delta_pitch)*(0,0,1). Positive pitch points toward -up. Native dorsal flak mounts use negative pitch for outward elevation; compiled basis must match these unit vectors.','method':'Two-sided double-precision BVH triangle intersections from ACTUAL MUZZLE to unchanged 4500 range. Search 2 degree pose grid, final independent 1 degree pose grid including endpoints. Nine outgoing-direction combinations at +/-3 degrees per axis model aim tolerance plus 2-degree margin; proposed native firing tolerances are 1 degree. Old comparison samples unchanged 7.5-degree tolerance. Retain outward -85-degree pitch limit. Rectangles contain forward yaw zero and are inset 2 degrees from blocked search columns/rows.','limits':'Sampled rays are evidence, not continuous swept-volume proof or a game-engine runtime test. Native schema/data corroborate signs but engine source is unavailable. Hull triangles exclude other moving turrets; self-turret swept geometry is outside this line-of-fire check. Reduced arcs intentionally trade broadside coverage for hull clearance; tighter tolerance may delay shots while slewing.','entries':entries}
    report['independent_bvh_check']=independent
    report['native_data_evidence']={'file':'Sins2/entities/trader_antifighter_frigate.unit','port_mount':{'position_x':-10.803879,'up':[0,1,0],'forward':[0,0,1],'yaw_arc':[-160,10],'pitch_arc':[-70,15]},'starboard_mount':{'position_x':10.778546,'up':[0,1,0],'forward':[0,0,1],'yaw_arc':[-10,160],'pitch_arc':[-70,15]},'interpretation':'Port X-negative gun permits mostly negative yaw; starboard permits mostly positive yaw. Dorsal guns permit mostly negative pitch. This corroborates the matrix convention; engine source is not available.'}
    (args.audit/(identity+'-proposal.json')).write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
