#!/usr/bin/env bash
set -euo pipefail
repo_dir=$(cd -- "$(dirname -- "$0")" && pwd)
test_dir=$(mktemp -d)
trap 'rm -rf -- "$test_dir"' EXIT
for base in 01_gia_pi4 02_tam_servo 03_tam_thiet_bi 04_khung_duoi_mau 05_khung_tren_mau 06_vo_dau_mau; do
 QT_QPA_PLATFORM=offscreen openscad -o "$test_dir/$base.stl" "$repo_dir/$base.scad" >"$test_dir/$base.log" 2>&1
 python - "$repo_dir/$base.stl" "$test_dir/$base.stl" <<'PY'
import sys, re, math
from collections import Counter
from pathlib import Path
def metrics(path):
    v=[tuple(map(float,m)) for m in re.findall(r'^\s*vertex\s+(\S+)\s+(\S+)\s+(\S+)',Path(path).read_text(),re.M)]
    assert len(v)>0 and len(v)%3==0
    tris=[v[i:i+3] for i in range(0,len(v),3)]
    edges=Counter(tuple(sorted((tuple(round(x,5) for x in t[i]),tuple(round(x,5) for x in t[(i+1)%3])))) for t in tris for i in range(3))
    assert all(n==2 for n in edges.values()),f'nonmanifold: {path}'
    bbox=tuple((min(x[i] for x in v),max(x[i] for x in v)) for i in range(3))
    volume=0
    for a,b,c in tris:
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    return bbox,volume
b1,v1=metrics(sys.argv[1]);b2,v2=metrics(sys.argv[2])
assert all(abs(b1[i][j]-b2[i][j])<0.02 for i in range(3) for j in range(2)),(b1,b2)
assert v1>0 and abs(v1-v2)<max(1,abs(v1)*.001),(v1,v2)
print(Path(sys.argv[1]).name,': tái xuất kín, kích thước và thể tích tương đồng')
PY
done
