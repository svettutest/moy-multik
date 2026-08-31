"""Точки садятся на рёбра меша — получается та самая сетка из точек, как в референсе."""
import sys, base64, numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-moy-multik/fe05547a-e1fe-542e-820a-95eac5813d83/scratchpad")
from glbtools import mesh_triangles, sample_points

def vertex_normals(V, F):
    a, b, c = V[F[:,0]], V[F[:,1]], V[F[:,2]]
    fn = np.cross(b-a, c-a)
    N = np.zeros_like(V)
    for k in range(3):
        np.add.at(N, F[:,k], fn)
    n = np.linalg.norm(N, axis=1, keepdims=True)
    return N / np.maximum(n, 1e-12)

def build(path, spacing=0.0022, fill=40000, crop_y=None, seed=3):
    V, F = mesh_triangles(path)
    lo, hi = V.min(0), V.max(0)
    ctr = (lo+hi)/2; s = 1.0/(hi[1]-lo[1])
    V = (V-ctr)*s
    N = vertex_normals(V, F)

    E = np.vstack([F[:,[0,1]], F[:,[1,2]], F[:,[2,0]]])
    E = np.unique(np.sort(E, axis=1), axis=0)
    A, B = V[E[:,0]], V[E[:,1]]
    NA, NB = N[E[:,0]], N[E[:,1]]
    L = np.linalg.norm(B-A, axis=1)
    steps = np.clip(np.ceil(L/spacing).astype(int), 1, 24)

    P, Nn = [], []
    for k in range(1, steps.max()+1):
        m = steps >= k
        t = (k / steps[m])[:, None]
        P.append(A[m] + (B[m]-A[m])*t)
        Nn.append(NA[m] + (NB[m]-NA[m])*t)
    P = np.vstack(P); Nn = np.vstack(Nn)

    if fill:                                   # лёгкая подсыпка внутри треугольников
        Pf, Nf = sample_points(V, F, fill, seed=seed)
        P = np.vstack([P, Pf]); Nn = np.vstack([Nn, Nf])
    Nn /= np.maximum(np.linalg.norm(Nn, axis=1, keepdims=True), 1e-12)

    if crop_y is not None:
        m = P[:,1] > crop_y
        P, Nn = P[m], Nn[m]
    return P, Nn

def pack(P, N, flags, path):
    lo, hi = P.min(0), P.max(0)
    sc = (hi-lo)
    q = np.clip(((P-lo)/sc * 65535.0).round(), 0, 65535).astype("<u2")
    nq = np.clip((N*127.0).round(), -127, 127).astype("<i1")
    buf = bytearray()
    buf += q.tobytes()
    buf += nq.tobytes()
    buf += flags.astype("<u1").tobytes()
    open(path, "wb").write(buf)
    return dict(count=len(P), lo=[round(float(v),5) for v in lo], size=[round(float(v),5) for v in sc],
                bytes=len(buf))
