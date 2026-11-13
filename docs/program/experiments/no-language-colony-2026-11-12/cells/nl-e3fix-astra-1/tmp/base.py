def enc(x):
    x=bytes(x)
    a=bytes(sorted(set(x)))
    if not x: return b'\0'
    bits=(len(a)-1).bit_length()
    ids={c:i for i,c in enumerate(a)}
    n=len(x); head=bytearray([1,len(a)-1]);head.extend(a)
    while n>=128: head.append((n&127)|128);n>>=7
    head.append(n)
    acc=0; count=0
    for c in x:
        acc=(acc<<bits)|ids[c];count+=bits
        while count>=8:
            count-=8;head.append((acc>>count)&255)
        acc &= (1<<count)-1
    if count: head.append(acc<<(8-count))
    return bytes(head) if len(head)<len(x)+1 else b'\0'+x

def dec(y):
    if y[0]==0:return bytes(y[1:])
    k=y[1]+1;a=y[2:2+k];p=2+k;n=0;shift=0
    while True:
        c=y[p];p+=1;n|=(c&127)<<shift
        if c<128:break
        shift+=7
    bits=(k-1).bit_length();acc=0;count=0;out=bytearray()
    if not bits:return bytes(a)*n
    for c in y[p:]:
        acc=(acc<<8)|c;count+=8
        while count>=bits and len(out)<n:
            count-=bits;out.append(a[(acc>>count)&((1<<bits)-1)])
        acc &= (1<<count)-1
    return bytes(out)

if __name__=='__main__':
    x=open('x.bin','rb').read();y=enc(x)
    assert dec(y)==x
    assert len(y)<=2*len(x)
    print(100*(1-len(y)/len(x)))
