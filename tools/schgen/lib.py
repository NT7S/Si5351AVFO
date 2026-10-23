import os,copy
from sexp import *
LIBDIR='/workspace/kisym'
_c={}
def libfile(n):
    if n not in _c: _c[n]=parse(open(os.path.join(LIBDIR,n+'.kicad_sym')).read())
    return _c[n]
def getsym(lib,name,src=None):
    root=src if src is not None else libfile(lib)
    syms={uq(s[1]):s for s in find(root,'symbol')}
    s=copy.deepcopy(syms[name])
    ext=find(s,'extends')
    if ext:
        base=getsym(lib,uq(ext[0][1]),src)
        bname=uq(base[1]).split(":",1)[-1]
        # take base, replace props by derived props
        props={uq(p[1]):p for p in find(s,'property')}
        new=[ 'symbol', q(name)]
        for i in base[2:]:
            if isinstance(i,list) and i[0]=='property' and uq(i[1]) in props:
                new.append(props.pop(uq(i[1])))
            elif isinstance(i,list) and i[0]=='symbol':
                j=copy.deepcopy(i); j[1]=q(uq(j[1]).replace(bname,name,1)); new.append(j)
            else: new.append(i)
        idx=max(i for i,x in enumerate(new) if isinstance(x,list) and x[0]=='property')+1
        for p in props.values(): new.insert(idx,p); idx+=1
        s=new
    s[1]=q(lib+':'+name)
    return s
def pins(sym):
    out=[]
    def walk(x,unit):
        for i in x:
            if isinstance(i,list):
                if i[0]=='symbol':
                    u=int(uq(i[1]).split('_')[-2]); walk(i,u)
                elif i[0]=='pin':
                    at=find(i,'at')[0]; nm=uq(find(i,'name')[0][1]); no=uq(find(i,'number')[0][1])
                    hid='hide' in i or any(isinstance(k,list) and k[0]=='hide' and k[1:]==['yes'] for k in i)
                    out.append(dict(name=nm,num=no,x=float(at[1]),y=float(at[2]),a=int(float(at[3])),unit=unit,type=i[1],hidden=hid))
    walk(sym,0); return out
