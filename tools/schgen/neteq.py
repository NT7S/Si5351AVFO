import re,sys
def load(p):
    t=open(p).read(); nets=[]
    for blk in re.split(r'\(net\s*\n',t)[1:]:
        name=re.search(r'\(name "([^"]*)"\)',blk).group(1)
        nets.append((name,frozenset(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"',blk))))
    return nets
A=load(sys.argv[1]); B=load(sys.argv[2])
# apply intended changes to A
MCU={('U4','1'),('C15','1'),('C16','1'),('R12','1'),('R26','1'),('R27','1'),('R28','1'),('D5','1'),('D6','1')}|{('R%d'%i,'1') for i in range(20,26)}
DROP={'JP1','JP2'}
A2=[]
for n,s in A:
    s=frozenset(x for x in s if x[0] not in DROP and x not in MCU)
    if n=='+3V3D': s=s|{('D6','2')}
    if s: A2.append((n,s))
A2.append(('+3V3_MCU',frozenset(MCU)))
# drop singleton nets (unconnected) for comparison
norm=lambda L:{s for n,s in L if len(s)>1}
a,b=norm(A2),norm(B)
print('equal' if a==b else 'DIFF')
for s in a-b: print(' only expected:',sorted(s)[:12])
for s in b-a: print(' only new    :',sorted(s)[:12])
ra={x for _,s in A2 for x in s}; rb={x for _,s in B for x in s}
print('pins only expected',sorted(ra-rb)[:20]); print('pins only new',sorted(rb-ra)[:20])
