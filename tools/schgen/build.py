import uuid, math, copy
from sexp import *
from lib import getsym, pins
PROJ='Si5351AVFO'
ROOT_UUID='a0000000-0000-4000-8000-000000000001'
def g(v): return round(round(v/1.27)*1.27,2)
def U(): return str(uuid.uuid4())
def f(v): s=('%.4f'%v).rstrip('0').rstrip('.'); return '0' if s in('-0','') else s
RAILS={'GND':('power','GND','down'),'+5V':('power','+5V','up'),'+3V3D':('power','+3V3','up'),
 '+3V3_CLK':('power','+3V3','up'),'+3V3_OLED':('power','+3V3','up')}
GLOBALS={'MCU_TX','MCU_RX','DTR','I2C_SCL','I2C_SDA'}
VERIFY_ALL=[]
pwr_n=[0]
class Sheet:
    def __init__(s,fname,title,sheet_uuid,page):
        s.fname=fname; s.title=title; s.su=sheet_uuid; s.page=page
        s.libs={}; s.items=[]; s.pinpos={}; s.verify=[]; s.uuid=U()
    def path(s): return '/'+ROOT_UUID+('/'+s.su if s.su else '')
    def lib(s,lib,name,src=None,libname=None):
        key=(libname or lib)+':'+name
        if key not in s.libs:
            sym=getsym(lib,name,src) if src is None else copy.deepcopy([x for x in find(src,'symbol') if uq(x[1]) in (name,(libname or lib)+':'+name,lib+':'+name)][0])
            sym[1]=q(key); s.libs[key]=sym
        return key, s.libs[key]
    def xf(s,X,Y,r,px,py):
        x,y=px,-py; c=round(math.cos(math.radians(r))); sn=round(math.sin(math.radians(r)))
        return (X+x*c+y*sn, Y-x*sn+y*c)
    def wire(s,pts):
        for a,b in zip(pts,pts[1:]):
            s.items.append(['wire',['pts',['xy',f(a[0]),f(a[1])],['xy',f(b[0]),f(b[1])]],['stroke',['width','0'],['type','default']],['uuid',q(U())]])
    def text(s,txt,x,y,size=1.27):
        s.items.append(['text',q(txt),['exclude_from_sim','no'],['at',f(x),f(y),'0'],['effects',['font',['size',f(size),f(size)]],['justify','left','top']],['uuid',q(U())]])
    def power(s,net,x,y,direction):
        x,y=g(x),g(y)
        lib,name,_=RAILS.get(net,('power',net,'up'))
        key,sym=s.lib(lib,name)
        if net=='GND': r={'down':0,'right':90,'up':180,'left':270}[direction]
        else: r={'up':0,'left':90,'down':180,'right':270}[direction]
        pwr_n[0]+=1; ref='#PWR%03d'%pwr_n[0]
        vx,vy={0:(0,-3.81),180:(0,3.81),90:(-3.81,0),270:(3.81,0)}[r] if net!='GND' else {0:(0,3.81),180:(0,-3.81),90:(3.81,0),270:(-3.81,0)}[r]
        s.items.append(['symbol',['lib_id',q(key)],['at',f(x),f(y),str(r)],['unit','1'],['exclude_from_sim','no'],['in_bom','no'],['on_board','yes'],['dnp','no'],['uuid',q(U())],
          ['property','"Reference"',q(ref),['at',f(x),f(y),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]],
          ['property','"Value"',q(net),['at',f(x+vx),f(y+vy),'0'],['effects',['font',['size','1.27','1.27']]]],
          ['property','"Footprint"','""',['at',f(x),f(y),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]],
          ['property','"Datasheet"','""',['at',f(x),f(y),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]],
          ['pin','"1"',['uuid',q(U())]],
          ['instances',['project',q(PROJ),['path',q(s.path()),['reference',q(ref)],['unit','1']]]]])
    def flag(s,x,y):
        x,y=g(x),g(y)
        key,_=s.lib('power','PWR_FLAG'); pwr_n[0]+=1; ref='#FLG%03d'%pwr_n[0]
        s.items.append(['symbol',['lib_id',q(key)],['at',f(x),f(y),'0'],['unit','1'],['exclude_from_sim','no'],['in_bom','no'],['on_board','yes'],['dnp','no'],['uuid',q(U())],
          ['property','"Reference"',q(ref),['at',f(x),f(y+1.9),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]],
          ['property','"Value"','"PWR_FLAG"',['at',f(x),f(y-3.81),'0'],['effects',['font',['size','1.27','1.27']]]],
          ['pin','"1"',['uuid',q(U())]],
          ['instances',['project',q(PROJ),['path',q(s.path()),['reference',q(ref)],['unit','1']]]]])
    def label(s,net,x,y,ang):
        x,y=g(x),g(y)
        just={0:['left','bottom'],90:['left','bottom'],180:['right','bottom'],270:['right','bottom']}[ang]
        if net in GLOBALS:
            s.items.append(['global_label',q(net),['shape','passive'],['at',f(x),f(y),str(ang)],['fields_autoplaced','yes'],['effects',['font',['size','1.27','1.27']],['justify',just[0]]],['uuid',q(U())],
              ['property','"Intersheetrefs"','"${INTERSHEET_REFS}"',['at',f(x),f(y),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]]])
        else:
            s.items.append(['label',q(net),['at',f(x),f(y),str(ang)],['effects',['font',['size','1.27','1.27']],['justify',*just]],['uuid',q(U())]])
    def nc(s,x,y): s.items.append(['no_connect',['at',f(x),f(y)],['uuid',q(U())]])
    def place(s,lib,name,ref,value,X,Y,conns,r=0,fp=None,dnp=False,fields=None,src=None,libname=None,vfy=None,fieldpos=None):
        X,Y=g(X),g(Y)
        key,sym=s.lib(lib,name,src,libname)
        ps=[p for p in pins(sym) if p['unit'] in (0,1)]
        props={uq(p[1]):p for p in find(sym,'property')}
        inst=['symbol',['lib_id',q(key)],['at',f(X),f(Y),str(r)],['unit','1'],['exclude_from_sim','no'],['in_bom','yes'],['on_board','yes'],['dnp','yes' if dnp else 'no'],['uuid',q(U())]]
        allf={'Reference':ref,'Value':value,'Footprint':fp if fp is not None else uq(props['Footprint'][2]) if 'Footprint' in props else '',
              'Datasheet':uq(props['Datasheet'][2]) if 'Datasheet' in props else '','Description':uq(props['Description'][2]) if 'Description' in props else ''}
        if fields: allf.update(fields)
        if vfy: allf['VERIFY']=vfy; s.verify.append('%s: %s'%(ref,vfy))
        for k,v in allf.items():
            if k in('Reference','Value'):
                if fieldpos: fx,fy=fieldpos[k]; fx+=X; fy+=Y
                elif k in props and r==0:
                    a=props[k][3]; fx,fy=X+float(a[1]),Y-float(a[2])
                else: fx,fy=X,Y+(-3.2 if k=='Reference' else 3.2)
                just=['justify','left'] if (r==0 and fx>X+0.1) else None
                eff=['effects',['font',['size','1.27','1.27']]]+([just] if just else [])
                inst.append(['property',q(k),q(v),['at',f(fx),f(fy),'0' if r in (0,180) else '90'],eff])
            else:
                inst.append(['property',q(k),q(v),['at',f(X),f(Y),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]])
        for p in ps: inst.append(['pin',q(p['num']),['uuid',q(U())]])
        inst.append(['instances',['project',q(PROJ),['path',q(s.path()),['reference',q(ref)],['unit','1']]]])
        s.items.append(inst)
        done=set()
        for p in ps:
            x,y=s.xf(X,Y,r,p['x'],p['y']); x,y=round(x,2),round(y,2)
            s.pinpos[(ref,p['num'])]=(x,y)
            out=(p['a']+180+r)%360
            if (x,y) in done: continue
            done.add((x,y))
            spec=conns.get(p['num'], conns.get(p['name'],'NC' if p['type']!='no_connect' or True else None))
            if p['num'] not in conns and p['name'] not in conns:
                if p['hidden']: continue
                print('WARN unconnected-default NC',ref,p['num'],p['name'])
            stub=0
            if isinstance(spec,tuple): spec,stub=spec
            if spec=='WIRE': continue
            if spec=='NC': s.nc(x,y); continue
            if (spec in RAILS or spec.startswith('+')) and out in (0,180) and not stub: stub=2.54
            dx,dy={0:(1,0),90:(0,-1),180:(-1,0),270:(0,1)}[out]
            if stub: nx,ny=x+dx*stub,y+dy*stub; s.wire([(x,y),(nx,ny)]); x,y=nx,ny
            if spec in RAILS or spec.startswith('+'):
                d={0:'right',90:'up',180:'left',270:'down'}[out]
                if stub: d='down' if spec=='GND' else 'up'
                s.power(spec,x,y,d)
            else: s.label(spec,x,y,out)
        return ref
    def save(s,root_extra=None):
        doc=['kicad_sch',['version','20250114'],['generator','"eeschema"'],['generator_version','"10.0"'],['uuid',q(s.uuid)],['paper','"A3"'],
             ['title_block',['title',q('Si5351A VFO - '+s.title)],['date','"2026-10-22"'],['rev','"A"'],['company','"Etherkit / NT7S"'],['comment','1','"Draft schematic, not reviewed. See VERIFY notes."']],
             ['lib_symbols']+list(s.libs.values())]+s.items
        if root_extra: doc+=root_extra
        open(s.fname,'w').write(dump(doc)+'\n')
