import sys
from array import array



def read_lines(path):
    with open(path, "rb") as f:          
        data = f.read()
    lines = data.split(b"\n")            
    if lines[-1] == b"":                 
        lines.pop()
    return lines



def myers_algorithm(a, b):
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return []

    off = n + m + 1                      
    V = [0] * (2 * off + 1)              

    
    a = list(a) + [-1] * (2 * off)
    b = list(b) + [-2] * (2 * off)
    trace = []                           

    for d in range(n + m + 1):
        lo, hi = off - d, off + d        
        for kk in range(lo, hi + 1, 2):
            
            if kk == lo or (kk != hi and V[kk - 1] < V[kk + 1]):
                x = V[kk + 1]
            else:
                x = V[kk - 1] + 1
            y = x - (kk - off)

            
            while a[x] == b[y]:
                x += 1
                y += 1

            V[kk] = x
            if x >= n and y >= m:        
                return backtrack(trace, d, n, m)

        
        trace.append(array("i", V[lo:hi + 1:2]))

    return []                            


def backtrack(trace, D, n, m):
    matches = []
    x, y = n, m                          
    for d in range(D, 0, -1):
        Vp = trace[d - 1]                
        k = x - y
        if k == -d or (k != d and Vp[(k - 1 + d - 1) // 2] < Vp[(k + 1 + d - 1) // 2]):
            pk = k + 1                   
            px = Vp[(pk + d - 1) // 2]
            sx = px                      
        else:
            pk = k - 1                   
            px = Vp[(pk + d - 1) // 2]
            sx = px + 1
        py = px - pk

        while x > sx:                    
            x -= 1
            y -= 1
            matches.append((x, y))
        x, y = px, py

    while x > 0:                        
        x -= 1
        y -= 1
        matches.append((x, y))

    matches.reverse()                    
    return matches



def diff(a, b):
    n, m = len(a), len(b)

   
    p = 0
    while p < n and p < m and a[p] == b[p]:
        p += 1
    s = 0
    while s < n - p and s < m - p and a[n - 1 - s] == b[m - 1 - s]:
        s += 1

   
    ids = {}
    a_mid = [ids.setdefault(v, len(ids)) for v in a[p:n - s]]
    b_mid = [ids.setdefault(v, len(ids)) for v in b[p:m - s]]

   
    in_a, in_b = set(a_mid), set(b_mid)
    a_idx = [i for i, v in enumerate(a_mid) if v in in_b]
    b_idx = [j for j, v in enumerate(b_mid) if v in in_a]
    a_f = [a_mid[i] for i in a_idx]
    b_f = [b_mid[j] for j in b_idx]

    matches = [(i, i) for i in range(p)]
    for i, j in myers_algorithm(a_f, b_f):
        matches.append((p + a_idx[i], p + b_idx[j]))
    for t in range(s):
        matches.append((n - s + t, m - s + t))
    return matches



def ranges_text(length, matched_positions):
    out = []
    pos = 0
    for q in matched_positions + [length]:   
        if q > pos:
            out.append(str(pos) + "-" + str(q))
        pos = q + 1
    return ",".join(out) if out else "."


def highlight_line(old, new):
    o = old.decode("utf-8", "surrogateescape")   
    w = new.decode("utf-8", "surrogateescape")
    matches = diff(o, w)
    old_r = ranges_text(len(o), [i for i, _ in matches])
    new_r = ranges_text(len(w), [j for _, j in matches])
    return ("? " + old_r + " | " + new_r + "\n").encode()



def build_output(a, b, highlight):
    out = []
    i = j = 0
    for mi, mj in diff(a, b) + [(len(a), len(b))]:   
        dels = a[i:mi]                   
        ins = b[j:mj]
        for line in dels:               
            out.append(b"-" + line + b"\n")
        for t, line in enumerate(ins):   
            out.append(b"+" + line + b"\n")
            if highlight and t < len(dels):          
                out.append(highlight_line(dels[t], line))
        if mi < len(a):
            out.append(b" " + a[mi] + b"\n")        
        i, j = mi + 1, mj + 1
    return out


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        sys.stderr.write("Usage: main.py lines|highlight A B\n")
        sys.exit(2)

    try:
        a = read_lines(sys.argv[2])
        b = read_lines(sys.argv[3])
    except OSError as e:
        sys.stderr.write("error: cannot read file: " + str(e) + "\n")
        sys.exit(2)

    out = build_output(a, b, sys.argv[1] == "highlight")
    sys.stdout.buffer.write(b"".join(out))


if __name__ == "__main__":
    main()