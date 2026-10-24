import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as la
def solve(w,s,h=0.2104,er=4.4,t=0.035,mask=0.0,erm=3.8,dx=0.005,W=3.0,Htop=1.0,gw=None):
    nx=int(W/dx); ny=int((h+t+Htop)/dx)
    X=(np.arange(nx)+0.5)*dx-W/2; Y=np.arange(ny)*dx  # y=0 ground plane
    eps=np.ones((ny,nx)); ih=int(round(h/dx)); it=int(round(t/dx))
    eps[:ih,:]=er
    if mask>0:
        im=int(round(mask/dx)); eps[ih:ih+it+im,:]=erm  # crude conformal-ish slab
    cond=np.zeros((ny,nx),bool); V=np.zeros((ny,nx))
    sig=(abs(X)<=w/2); gnd=(abs(X)>=w/2+s)
    for j in range(ih,ih+it): cond[j,sig]=True; V[j,sig]=1; cond[j,gnd]=True
    if mask>0:
        for j in range(ih,ih+it): eps[j,~sig&~gnd]=erm
    cond[0,:]=True; V[0,:]=0
    def cap(eps):
        N=nx*ny; idx=lambda j,i:j*nx+i
        rows=[];cols=[];vals=[];b=np.zeros(N)
        for j in range(ny):
            for i in range(nx):
                k=idx(j,i)
                if cond[j,i] or j==ny-1 or i==0 or i==nx-1:
                    rows.append(k);cols.append(k);vals.append(1);b[k]=V[j,i] if cond[j,i] else 0;continue
                # face eps averages
                e_n=(eps[j,i]+eps[j+1,i])/2; e_s=(eps[j,i]+eps[j-1,i])/2
                e_e=(eps[j,i]+eps[j,i+1])/2; e_w=(eps[j,i]+eps[j,i-1])/2
                rows+= [k]*5; cols+=[k,idx(j+1,i),idx(j-1,i),idx(j,i+1),idx(j,i-1)]
                vals+=[-(e_n+e_s+e_e+e_w),e_n,e_s,e_e,e_w]
        A=sp.csr_matrix((vals,(rows,cols)),shape=(N,N)); phi=la.spsolve(A,b).reshape(ny,nx)
        # energy method
        ex=np.diff(phi,axis=1)/dx; ey=np.diff(phi,axis=0)/dx
        epsx=(eps[:,1:]+eps[:,:-1])/2; epsy=(eps[1:,:]+eps[:-1,:])/2
        return 8.854e-12*(np.sum(epsx*ex**2)+np.sum(epsy*ey**2))*dx*dx
    C=cap(eps); C0=cap(np.ones_like(eps))
    return 1/(3e8*np.sqrt(C*C0)), C/C0
import sys
for w,s in [(0.35,0.2),(0.40,0.25),(0.45,0.25),(0.45,0.3),(0.50,0.3)]:
    z,e=solve(w,s,dx=0.01); print(w,s,round(z,1),round(e,2),flush=True)
