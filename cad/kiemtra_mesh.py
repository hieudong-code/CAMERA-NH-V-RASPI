#!/usr/bin/env python3
"""Two independent STL checks: ASCII triangle-edge incidence and volume/bounds."""
from pathlib import Path
from collections import Counter
import re, sys, math
p=Path(__file__).parent
for stl in sorted(p.glob('*.stl')):
    data=stl.read_text()
    verts=[tuple(map(float, match)) for match in re.findall(r'^\s*vertex\s+(\S+)\s+(\S+)\s+(\S+)', data, re.M)]
    assert verts and len(verts)%3==0,(stl,'invalid triangle list')
    assert all(math.isfinite(x) for v in verts for x in v)
    tris=[verts[i:i+3] for i in range(0,len(verts),3)]
    # Quantization absorbs harmless decimal representation differences.
    def quant(v): return tuple(round(x,5) for x in v)
    edges=Counter(tuple(sorted((quant(t[i]),quant(t[(i+1)%3])))) for t in tris for i in range(3))
    bad=sum(n!=2 for n in edges.values())
    volume=0.
    for a,b,c in tris:
        cross=(b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0])
        volume+=sum(a[i]*cross[i] for i in range(3))/6
    ext=[max(v[i] for v in verts)-min(v[i] for v in verts) for i in range(3)]
    print(f'{stl.name}: faces={len(tris)}, extents_mm={[round(x,2) for x in ext]}, volume_mm3={volume:.1f}, nonmanifold_edges={bad}')
    if bad or volume<=0: sys.exit(1)
