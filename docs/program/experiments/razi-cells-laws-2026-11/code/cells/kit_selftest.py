"""Selftest for kit.py through the real sandbox runner in cell.py.
Reference bodies must score > 0. Wrong bodies and cheating bodies must score 0 or be unable to cheat."""
import os, sys, tempfile, shutil
from pathlib import Path
os.environ["CELL_KIT"] = "maze"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cell, kit  # noqa: E402

GOOD = {
 "fibmod": ("fibmod.py", '''import sys
M=10**9+7
def f(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M
        a,b=(d,(c+d)%M) if bit=="1" else (c,d)
    return a
print("\\n".join(str(f(int(x))) for x in sys.stdin.read().split()))
'''),
 "csvsum": ("csvsum.py", '''import sys
from decimal import Decimal
s={}
it=iter(sys.stdin); next(it)
for l in it:
    _,c,v=l.rstrip("\\n").split(",")
    s[c]=s.get(c,Decimal(0))+Decimal(v)
for c in sorted(s): print(f"{c},{s[c]:.2f}")
'''),
 "maze": ("maze.py", '''import sys
from collections import deque
rows=sys.stdin.read().split()
h=len(rows); w=len(rows[0]); g="".join(rows); s=g.index("S"); e=g.index("E")
d=[-1]*(h*w); d[s]=0; q=deque([s]); ans=-1
while q:
    p=q.popleft()
    if p==e: ans=d[p]; break
    r,c=divmod(p,w)
    for ok,n in ((c>0,p-1),(c<w-1,p+1),(r>0,p-w),(r<h-1,p+w)):
        if ok and d[n]<0 and g[n]!="#": d[n]=d[p]+1; q.append(n)
print(ans)
'''),
 "compress": ("squeeze.py", '''import sys,zlib
d=sys.stdin.buffer.read()
sys.stdout.buffer.write(zlib.compress(d,9) if sys.argv[1]=="c" else zlib.decompress(d))
'''),
}
BAD = {  # name -> (kit, file, code, what it tries)
 "wrong answer": ("maze", "maze.py", 'print(-1)\n'),
 "reads hidden input from disk": ("maze", "maze.py", f'print(open("{kit.HIDDEN}/maze/out-0.txt").read())\n'),
 "caches answer in own folder": ("fibmod", "fibmod.py", GOOD["fibmod"][1] + 'open("cache.txt","w").write("x")\n'),
 "identity compressor that lies on d": ("compress", "squeeze.py", 'import sys\nsys.stdout.buffer.write(b"x" if sys.argv[1]=="c" else b"y")\n'),
 "crash": ("csvsum", "csvsum.py", 'raise SystemExit(3)\n'),
}
fails = 0
tmp = Path(tempfile.mkdtemp(prefix="kitself-", dir=os.path.realpath(tempfile.gettempdir())))
for name, (f, code) in GOOD.items():
    kit.ensure(name)
    d = tmp / ("good-" + name); d.mkdir()
    (d / f).write_text(code)
    runs = [kit.score(name, d, cell.kit_run) for _ in range(3)]
    pub = kit.score(name, d, cell.kit_run, kit.PUBLIC)
    ss = [r[0] for r in runs]
    sp = (max(ss) - min(ss)) / sorted(ss)[1] if sorted(ss)[1] else 9
    ok = all(s > 0 for s in ss) and pub[0] > 0
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} good {name}: hidden {[round(s, 4) for s in ss]} spread {sp:.1%} public {pub[0]:.4f} {runs[0][1]}")
for what, (name, f, code) in BAD.items():
    d = tmp / ("bad-" + what.replace(" ", "_")); d.mkdir()
    (d / f).write_text(code)
    s, why = kit.score(name, d, cell.kit_run)
    ok = s == 0.0 and bool(why)
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} bad  {what}: score {s} reason {why!r} extra files {[p.name for p in d.iterdir() if p.name != f]}")
# the cell's own shell: can it read samples, and is it locked out of hidden inputs and harness files?
c = tmp / "cellbox" / "maze"; c.mkdir(parents=True); (c / "NEED").write_text("x"); (c / "ASSAY.json").write_text("{}")
checks = [
 ("reads public sample", f"head -c 5 {kit.PUBLIC}/maze/in-0.txt >/dev/null && echo yes", True),
 ("reads hidden input", f"head -c 5 {kit.HIDDEN}/maze/in-0.txt >/dev/null && echo yes", False),
 ("lists hidden folder", f"ls {kit.HIDDEN}/maze >/dev/null && echo yes", False),
 ("writes public sample", f"echo x >> {kit.PUBLIC}/maze/in-2.txt && echo yes", False),
 ("overwrites ASSAY.json", "echo '{\"baseline\":0.001}' > ASSAY.json && echo yes", False),
 ("writes own body", "echo 1 > a.py && echo yes", True),
]
for what, cmd, want in checks:
    out = cell.sandboxed(c, cmd)[0]
    got = "yes" in out.split()
    fails += got != want
    print(f"{'ok  ' if got == want else 'FAIL'} cell shell {what}: {'allowed' if got else 'denied'} (want {'allowed' if want else 'denied'})")
shutil.rmtree(tmp, ignore_errors=True)
print("selftest", "PASSED" if not fails else f"FAILED ({fails})")
raise SystemExit(1 if fails else 0)
