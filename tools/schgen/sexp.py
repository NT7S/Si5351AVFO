import re
tok=re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)',re.S)
def parse(s):
    st=[[]];
    for m in tok.finditer(s):
        t=m.group(1)
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t)
    return st[0][0]
def dump(x,ind=0):
    if not isinstance(x,list): return x
    if all(not isinstance(i,list) for i in x): return '('+' '.join(x)+')'
    out='('+' '.join(i for i in x if not isinstance(i,list)) if False else None
    parts=[];head=[]
    for i in x:
        parts.append(dump(i,ind+1) if isinstance(i,list) else i)
    s='('+parts[0]
    for p,i in zip(parts[1:],x[1:]):
        s+=('\n'+'\t'*(ind+1)+p) if isinstance(i,list) else ' '+p
    return s+')'
def q(s): return '"'+s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
def uq(s): return s[1:-1].replace('\\"','"').replace('\\\\','\\') if s.startswith('"') else s
def find(x,key): return [i for i in x if isinstance(i,list) and i and i[0]==key]
