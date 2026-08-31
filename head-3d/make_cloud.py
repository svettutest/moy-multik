import sys, json, base64, numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-moy-multik/fe05547a-e1fe-542e-820a-95eac5813d83/scratchpad")
from build_cloud import build

def make(glb, out_b64, out_json, spacing=0.0030, fill=25000, crop_y=-0.32,
         eyes=None, hair_y=None, seed=5):
    P, N = build(glb, spacing=spacing, fill=fill, crop_y=crop_y)
    rng = np.random.default_rng(seed)
    n = len(P)
    region = np.zeros(n, dtype=np.uint8)
    if hair_y is not None:
        region[P[:,1] > hair_y] = 64                     # «волосы» — верх и затылок
    if eyes:
        for (ex, ey, ez, rx, ry, rz) in eyes:
            for sx in (-1, 1):
                d = ((P[:,0]-sx*ex)/rx)**2 + ((P[:,1]-ey)/ry)**2 + ((P[:,2]-ez)/rz)**2
                region[(d < 1) & (P[:,2] > ez - rz)] = 128   # светящиеся глаза
    seeds = rng.integers(0, 256, n).astype(np.uint8)

    lo, hi = P.min(0), P.max(0); size = hi - lo
    q = np.clip(((P - lo) / size * 65535.0).round(), 0, 65535).astype("<u2")
    nq = np.clip((N * 127.0).round(), -127, 127).astype("<i1")
    blob = q.tobytes() + nq.tobytes() + region.tobytes() + seeds.tobytes()
    open(out_b64, "w").write(base64.b64encode(blob).decode())
    meta = dict(count=int(n), lo=[float(v) for v in lo], size=[float(v) for v in size],
                bytes=len(blob), eyes=int((region == 128).sum()), hair=int((region == 64).sum()))
    json.dump(meta, open(out_json, "w"))
    print(json.dumps(meta)[:200], "\nbase64:", len(base64.b64encode(blob))//1024, "КБ")
    return meta

if __name__ == "__main__":
    make("Nefertiti_plain.glb", "cloud.b64", "cloud.json",
         spacing=0.0030, fill=25000, crop_y=-0.32,
         eyes=[(0.050, 0.147, 0.232, 0.036, 0.022, 0.040)],
         hair_y=0.21)
