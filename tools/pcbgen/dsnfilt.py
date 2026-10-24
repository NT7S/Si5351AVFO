# Prepare fr.dsn for freerouting: drop pre-routed RF nets from the netlist (left as fixed wiring),
# keep GND (vias to In1 plane already exist) and add clearance margin.
import re
s=open('fr.dsn').read()
def blk(s,i):
    d=0
    for j in range(i,len(s)):
        if s[j]=='(':d+=1
        elif s[j]==')':
            d-=1
            if d==0:return j+1
n0=s.find('(network'); net=s[n0:blk(s,n0)]
i=net.find('(class RF50'); rfc=net[i:blk(net,i)]
names=re.findall(r'"[^"]*"|[^\s()"]+',rfc[len('(class RF50'):rfc.find('(circuit') if '(circuit' in rfc else len(rfc)])
out=net
for n in names:
    k=out.find('(net %s\n'%n); k=k if k>=0 else out.find('(net %s '%n)
    if k>=0: out=out[:k]+out[blk(out,k):]
k=out.find('(class RF50'); out=out[:k]+out[blk(out,k):]
s=s[:n0]+out+s[n0+len(net):]
import re as _r
s=_r.sub(r'\(wire_keepout "" \(polygon In1\.Cu 0  100000 -100000[^)]*\)\s*\)','',s)
s=s.replace('(layer In1.Cu\n      (type signal)','(layer In1.Cu\n      (type power)')
s=s.replace('(clearance 150)','(clearance 170)')
print('dropped RF nets',len(names))
open('fr.dsn','w').write(s)
