import lzma
d=open('x.bin','rb').read()
print(100*(1-len(lzma.compress(d,preset=9))/len(d)))
