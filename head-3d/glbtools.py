import json, struct, math
import numpy as np

CT = {5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
NC = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def load_glb(path):
    d = open(path,'rb').read()
    assert d[:4] == b'glTF', "не GLB"
    n = struct.unpack('<I', d[12:16])[0]
    js = json.loads(d[20:20+n])
    off = 20 + n
    bins = b''
    while off < len(d):
        ln, ty = struct.unpack('<II', d[off:off+8])
        if ty == 0x004E4942: bins = d[off+8:off+8+ln]
        off += 8 + ln + ((-ln) % 4)
    return js, bins

def accessor(js, bins, i):
    a = js['accessors'][i]
    bv = js['bufferViews'][a['bufferView']]
    fmt, size = CT[a['componentType']]
    nc = NC[a['type']]
    stride = bv.get('byteStride') or size*nc
    start = bv.get('byteOffset',0) + a.get('byteOffset',0)
    out = np.empty((a['count'], nc), dtype=np.float64 if fmt=='f' else np.int64)
    for k in range(a['count']):
        o = start + k*stride
        out[k] = struct.unpack_from('<'+fmt*nc, bins, o)
    return out

def node_matrix(nd):
    if 'matrix' in nd:
        return np.array(nd['matrix'], dtype=np.float64).reshape(4,4).T
    M = np.eye(4)
    if 'scale' in nd: M = M @ np.diag(list(nd['scale'])+[1.0])
    if 'rotation' in nd:
        x,y,z,w = nd['rotation']
        R = np.array([
            [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w),   0],
            [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w),   0],
            [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y), 0],
            [0,0,0,1]], dtype=np.float64)
        M = R @ M
    if 'translation' in nd:
        T = np.eye(4); T[:3,3] = nd['translation']; M = T @ M
    return M

def mesh_triangles(path):
    js, bins = load_glb(path)
    V, F = [], []
    def walk(idx, parent):
        nd = js['nodes'][idx]
        M = parent @ node_matrix(nd)
        if 'mesh' in nd:
            for pr in js['meshes'][nd['mesh']]['primitives']:
                if pr.get('mode', 4) != 4: continue
                p = accessor(js, bins, pr['attributes']['POSITION'])
                p = (M[:3,:3] @ p.T).T + M[:3,3]
                idxs = (accessor(js, bins, pr['indices'])[:,0].astype(np.int64)
                        if 'indices' in pr else np.arange(len(p)))
                base = sum(len(v) for v in V)
                V.append(p); F.append(idxs.reshape(-1,3) + base)
        for c in nd.get('children', []): walk(c, M)
    sc = js['scenes'][js.get('scene',0)]
    for r in sc['nodes']: walk(r, np.eye(4))
    return np.vstack(V), np.vstack(F)

def sample_points(V, F, n, seed=1):
    rng = np.random.default_rng(seed)
    a, b, c = V[F[:,0]], V[F[:,1]], V[F[:,2]]
    fn = np.cross(b-a, c-a)
    area = np.linalg.norm(fn, axis=1) * 0.5
    nrm = fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12)
    prob = area / area.sum()
    pick = rng.choice(len(F), size=n, p=prob)
    u = rng.random((n,1)); v = rng.random((n,1))
    over = (u+v) > 1
    u[over] = 1-u[over]; v[over] = 1-v[over]
    P = a[pick] + u*(b[pick]-a[pick]) + v*(c[pick]-a[pick])
    return P, nrm[pick]

def render(P, N, yaw=0.0, pitch=0.0, W=520, H=640, zoom=1.0):
    cy, sy = math.cos(yaw), math.sin(yaw)
    R1 = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    cx, sx = math.cos(pitch), math.sin(pitch)
    R2 = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    R = R2 @ R1
    p = P @ R.T; nn = N @ R.T
    view = np.array([0,0,1.0])
    face = nn @ view
    fres = np.power(1 - np.abs(face), 3.0)
    back = 0.3 + 0.7*np.clip((face+0.3)/0.7, 0, 1)
    b = (0.10 + 1.6*fres) * back
    img = np.zeros((H, W))
    sx_ = (p[:,0]*zoom*0.5 + 0.5) * W
    sy_ = (0.5 - p[:,1]*zoom*0.5) * H
    xi = sx_.astype(int); yi = sy_.astype(int)
    m = (xi>=0)&(xi<W)&(yi>=0)&(yi<H)
    np.add.at(img, (yi[m], xi[m]), b[m])
    img = 1 - np.exp(-img*0.55)
    return (np.clip(img,0,1)*255).astype(np.uint8)
