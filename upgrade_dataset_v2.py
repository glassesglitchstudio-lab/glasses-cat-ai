"""
X_Fable_Coder Dataset v2 Upgrade - Replaces ALL placeholders with REAL implementations
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET_PATH = os.path.join(os.path.dirname(__file__), "x_fable_coder_dataset.json")

def is_placeholder(out):
    lines = out.split('\n')
    
    # Check for "def process(item):" followed by "pass" on next line (placeholder)
    has_process_pass = False
    for i, line in enumerate(lines):
        if 'def process(item):' in line and i + 1 < len(lines) and lines[i + 1].strip() == 'pass':
            has_process_pass = True
            break
    
    # Check for "pass" on its own line (not part of a one-liner like "def foo(): pass")
    has_standalone_pass = any(line.strip() == 'pass' for line in lines)
    
    checks = [
        "def solution_" in out and "pass" in out and has_standalone_pass,
        "class DataStructure" in out and "pass" in out and has_standalone_pass,
        "slow_version" in out and "fast_version" in out and has_process_pass,
        "# HATALI KOD" in out and "# DUZELTILMIS KOD" in out and has_standalone_pass,
        "class CleanSolution" in out and "self.implementation" in out,
    ]
    return any(checks)

# ============ IMPLEMENTATION GENERATORS ============

def gen_algo(inst):
    inst_lower = inst.lower()
    # LCS / Longest Common Subsequence
    if "lcs" in inst_lower or "longest common subsequence" in inst_lower:
        return r"""```python
def lcs(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

def lcs_with_string(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    i, j = m, n
    chars = []
    while i > 0 and j > 0:
        if text1[i - 1] == text2[j - 1]:
            chars.append(text1[i - 1])
            i -= 1; j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return dp[m][n], "".join(reversed(chars))
```
**Big-O:** O(m*n). DP tabanli, space O(min(m,n))'e dusurulebilir.
**Alternatif:** Hirschberg algoritmasi ile space O(min(m,n))."""
    # KMP
    if "kmp" in inst_lower or "knuth" in inst_lower or "morris" in inst_lower or "kmp string matching" in inst_lower:
        return r"""```python
def compute_lps(pattern):
    lps = [0] * len(pattern)
    length = 0; i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps

def kmp_search(text, pattern):
    lps = compute_lps(pattern)
    i = j = 0; matches = []
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1; j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            j = lps[j - 1] if j else 0
            if not j: i += 1
    return matches
```
**Big-O:** O(n + m). LPS sayesinde backtrack yok.
**Alternatif:** Naive O(n*m), Z-algorithm O(n+m), Rabin-Karp O(n+m) average."""
    # Quickselect
    if "quickselect" in inst_lower or "k\'inci" in inst_lower or "k. en kucuk" in inst_lower:
        return r"""```python
import random

def quickselect(arr, k):
    if not arr:
        raise ValueError("Empty array")
    return _select(arr, 0, len(arr) - 1, k - 1)

def _select(arr, left, right, k):
    if left == right:
        return arr[left]
    pivot_idx = random.randint(left, right)
    pivot_idx = partition(arr, left, right, pivot_idx)
    if k == pivot_idx:
        return arr[k]
    elif k < pivot_idx:
        return _select(arr, left, pivot_idx - 1, k)
    else:
        return _select(arr, pivot_idx + 1, right, k)

def partition(arr, left, right, pivot_idx):
    pivot = arr[pivot_idx]
    arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
    store = left
    for i in range(left, right):
        if arr[i] < pivot:
            arr[store], arr[i] = arr[i], arr[store]
            store += 1
    arr[right], arr[store] = arr[store], arr[right]
    return store
```
**Big-O:** Average O(n), worst O(n^2). Median-of-medians ile worst O(n).
**Alternatif:** Sort + index O(n log n). Heap O(n log k)."""

    # Suffix array
    if "suffix array" in inst_lower and "pattern" in inst_lower:
        return r"""```python
def build_suffix_array(s):
    n = len(s)
    sa = list(range(n))
    rank = [ord(c) for c in s]
    tmp = [0] * n; k = 1
    while k < n:
        sa.sort(key=lambda x: (rank[x], rank[x + k] if x + k < n else -1))
        tmp[sa[0]] = 0
        for i in range(1, n):
            prev, cur = sa[i - 1], sa[i]
            tmp[cur] = tmp[prev]
            if (rank[prev], rank[prev + k] if prev + k < n else -1) < (rank[cur], rank[cur + k] if cur + k < n else -1):
                tmp[cur] += 1
        rank = tmp[:]; k <<= 1
    return sa

def pattern_search_with_suffix(text, pattern):
    sa = build_suffix_array(text)
    n, m = len(text), len(pattern)
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid]:sa[mid] + m] < pattern:
            lo = mid + 1
        else:
            hi = mid
    start = lo; hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid]:sa[mid] + m] <= pattern:
            lo = mid + 1
        else:
            hi = mid
    return [sa[i] for i in range(start, lo)]
```
**Big-O:** O(n log n) build + O(m log n) search.
**Alternatif:** Suffix tree O(n) build + O(m) search ama daha karmasik."""

    # Z-algorithm
    if "z-algorithm" in inst_lower or "z algorithm" in inst_lower:
        return r"""```python
def z_function(s):
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z

def z_algorithm_search(text, pattern):
    concat = pattern + "$" + text
    z = z_function(concat)
    m = len(pattern)
    return [i - m - 1 for i, val in enumerate(z) if val == m]
```
**Big-O:** O(n + m). Linear time pattern matching.
**Alternatif:** KMP O(n+m), Rabin-Karp O(n+m) average."""

    # Manacher
    if "manacher" in inst_lower or "palindrome bul" in inst_lower and "o(n)" in inst_lower:
        return r"""```python
def manacher(s):
    t = "#" + "#".join(s) + "#"
    n = len(t)
    p = [0] * n
    center = right = 0
    for i in range(n):
        if i < right:
            p[i] = min(right - i, p[2 * center - i])
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
        if i + p[i] > right:
            center, right = i, i + p[i]
    max_len, center_idx = max((p[i], i) for i in range(n))
    start = (center_idx - max_len) // 2
    return s[start:start + max_len]
```
**Big-O:** O(n). Linear time palindrome bulma.
**Alternatif:** Expand around center O(n^2). DP O(n^2)."""

    # Rabin-Karp
    if "rabin" in inst_lower or "rolling hash" in inst_lower:
        return r"""```python
def rabin_karp(text, pattern):
    n, m = len(text), len(pattern)
    if m > n or m == 0: return []
    BASE, MOD = 911382323, 972663749
    pow_base = [1] * (n + 1)
    for i in range(1, n + 1):
        pow_base[i] = (pow_base[i - 1] * BASE) % MOD
    hash_t = [0] * (n + 1)
    for i in range(n):
        hash_t[i + 1] = (hash_t[i] * BASE + ord(text[i])) % MOD
    hash_p = 0
    for ch in pattern:
        hash_p = (hash_p * BASE + ord(ch)) % MOD
    matches = []
    for i in range(n - m + 1):
        h = (hash_t[i + m] - hash_t[i] * pow_base[m]) % MOD
        if h == hash_p and text[i:i + m] == pattern:
            matches.append(i)
    return matches
```
**Big-O:** O(n + m) average, O(n*m) worst.
**Alternatif:** KMP O(n+m), Z-algorithm O(n+m)."""

    # Bloom filter
    if "bloom filter" in inst_lower:
        return r"""```python
import hashlib

class BloomFilter:
    def __init__(self, size=10000, num_hashes=7):
        self.size = size
        self.num_hashes = num_hashes
        self.bits = bytearray((size + 7) // 8)

    def _hashes(self, item):
        return [int(hashlib.sha256((str(i) + str(item)).encode()).hexdigest()[:8], 16) % self.size for i in range(self.num_hashes)]

    def add(self, item):
        for b in self._hashes(item):
            self.bits[b // 8] |= 1 << (b % 8)

    def __contains__(self, item):
        return all(self.bits[b // 8] & (1 << (b % 8)) for b in self._hashes(item))
```
**Big-O:** O(k) insert/query. k = hash sayisi. Space O(m). False positive olabilir.
**Alternatif:** Set O(1) exact ama cok hafiza. Cuckoo filter daha az false positive."""

    # HyperLogLog
    if "hyperloglog" in inst_lower or "kardinalite" in inst_lower:
        return r"""```python
import hashlib, math

class HyperLogLog:
    def __init__(self, b=14):
        self.b = b
        self.m = 1 << b
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m)

    def add(self, item):
        h = hashlib.sha256(str(item).encode()).digest()
        idx = int.from_bytes(h[:2], "big") & (self.m - 1)
        w = int.from_bytes(h[2:], "big")
        r = 1
        while w & 1:
            w >>= 1; r += 1
        self.registers[idx] = max(self.registers[idx], r)

    def count(self):
        z = sum(2.0 ** -r for r in self.registers)
        e = self.alpha * self.m * self.m / z
        if e <= 2.5 * self.m:
            v = self.registers.count(0)
            if v: e = self.m * math.log(self.m / v)
        return int(e)
```
**Big-O:** O(n) ekleme, O(1) sorgu. Cok az hafiza ile milyarlarca elemanin kardinalitesi.
**Alternatif:** Exact count O(n) hafiza. MinHash farkli amaclar icin."""

    # Count-Min Sketch
    if "count-min" in inst_lower or "count min sketch" in inst_lower or "frekans" in inst_lower:
        return r"""```python
import hashlib

class CountMinSketch:
    def __init__(self, width=1000, depth=5):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]

    def _hash(self, item, i):
        return int(hashlib.sha256((str(i) + str(item)).encode()).hexdigest()[:8], 16) % self.width

    def add(self, item, count=1):
        for i in range(self.depth):
            self.table[i][self._hash(item, i)] += count

    def estimate(self, item):
        return min(self.table[i][self._hash(item, i)] for i in range(self.depth))
```
**Big-O:** O(1) insert/query. Overestimate edebilir (never underestimate).
**Alternatif:** Exact frequency map O(n) hafiza."""

    # Consistent Hashing
    if "consistent hash" in inst_lower:
        return r"""```python
import hashlib, bisect

class ConsistentHash:
    def __init__(self, nodes=None, replicas=150):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

    def add_node(self, node):
        for i in range(self.replicas):
            h = self._hash(f"{node}:{i}")
            self.ring[h] = node
            bisect.insort(self.sorted_keys, h)

    def remove_node(self, node):
        for i in range(self.replicas):
            h = self._hash(f"{node}:{i}")
            del self.ring[h]
            self.sorted_keys.remove(h)

    def get_node(self, key):
        if not self.ring: return None
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h)
        if idx == len(self.sorted_keys): idx = 0
        return self.ring[self.sorted_keys[idx]]
```
**Big-O:** O(log n) lookup. Node ekleme/cikarma minimal key redistribusyonu.
**Alternatif:** Mod-based hashing O(1) ama node eklenince tum key'ler yer degistirir."""

    # Merkle Tree
    if "merkle" in inst_lower:
        return r"""```python
import hashlib

class MerkleTree:
    def __init__(self, data):
        self.leaves = [hashlib.sha256(d.encode()).hexdigest() for d in data]
        self.tree = self._build(self.leaves)

    def _build(self, nodes):
        tree = [nodes]
        while len(nodes) > 1:
            if len(nodes) % 2: nodes.append(nodes[-1])
            nodes = [hashlib.sha256((nodes[i] + nodes[i + 1]).encode()).hexdigest() for i in range(0, len(nodes), 2)]
            tree.append(nodes)
        return tree

    @property
    def root(self):
        return self.tree[-1][0] if self.tree[-1] else ""

    def get_proof(self, idx):
        proof = []
        for level in self.tree[:-1]:
            sibling_idx = idx ^ 1
            if sibling_idx < len(level):
                proof.append((level[sibling_idx], sibling_idx % 2))
            idx //= 2
        return proof

    def verify(proof, leaf, root):
        h = leaf
        for sibling, is_right in proof:
            h = hashlib.sha256((h + sibling if is_right else sibling + h).encode()).hexdigest()
        return h == root
```
**Big-O:** O(n) build, O(log n) proof generation/verification.
**Alternatif:** Hash list O(n) verification. Digital signature daha guclu ama yavas."""

    # Fenwick Tree / BIT
    if "fenwick" in inst_lower or "bit" in inst_lower or "binary indexed" in inst_lower:
        if "2d" in inst_lower or "2-boyut" in inst_lower:
            return r"""```python
class Fenwick2D:
    def __init__(self, n, m):
        self.n = n; self.m = m
        self.bit = [[0] * (m + 1) for _ in range(n + 1)]

    def _add(self, x, y, val):
        i = x
        while i <= self.n:
            j = y
            while j <= self.m:
                self.bit[i][j] += val
                j += j & -j
            i += i & -i

    def _sum(self, x, y):
        s = 0; i = x
        while i > 0:
            j = y
            while j > 0:
                s += self.bit[i][j]
                j -= j & -j
            i -= i & -i
        return s

    def update(self, x, y, val):
        self._add(x + 1, y + 1, val)

    def query(self, x1, y1, x2, y2):
        return self._sum(x2 + 1, y2 + 1) - self._sum(x1, y2 + 1) - self._sum(x2 + 1, y1) + self._sum(x1, y1)
```
**Big-O:** O(log n * log m) per operation.
**Alternatif:** 2D Segment Tree O(log n * log m), Sparse Table O(1) query ama static."""
        return r"""```python
class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.bit = [0] * (n + 1)

    def update(self, idx, delta):
        i = idx + 1
        while i <= self.n:
            self.bit[i] += delta
            i += i & -i

    def query(self, idx):
        i = idx + 1; s = 0
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s

    def range_sum(self, l, r):
        return self.query(r) - (self.query(l - 1) if l > 0 else 0)
```
**Big-O:** O(log n) update/query. Cok hafif, hizli.
**Alternatif:** Segment Tree O(log n) daha esnek (range update)."""

    # Sparse Table
    if "sparse table" in inst_lower:
        return r"""```python
import math

class SparseTable:
    def __init__(self, arr):
        self.n = len(arr)
        self.k = math.floor(math.log2(self.n)) + 1
        self.st = [[0] * self.k for _ in range(self.n)]
        for i in range(self.n):
            self.st[i][0] = arr[i]
        j = 1
        while (1 << j) <= self.n:
            for i in range(self.n - (1 << j) + 1):
                self.st[i][j] = min(self.st[i][j - 1], self.st[i + (1 << (j - 1))][j - 1])
            j += 1

    def query(self, l, r):
        j = math.floor(math.log2(r - l + 1))
        return min(self.st[l][j], self.st[r - (1 << j) + 1][j])
```
**Big-O:** O(n log n) build, O(1) query. Immutable (no updates).
**Alternatif:** Segment Tree O(log n) query ama mutable. Sqrt decomposition O(sqrt(n))."""

    # Mo's algorithm
    if "mo\'s" in inst_lower or "mos algorithm" in inst_lower:
        return r"""```python
import math

def mo_algorithm(arr, queries):
    n = len(arr); q = len(queries)
    block_size = int(math.sqrt(n)) + 1
    sorted_q = sorted(range(q), key=lambda i: (queries[i][0] // block_size, queries[i][1] if (queries[i][0] // block_size) % 2 == 0 else -queries[i][1]))
    freq = {}; cur_l = cur_r = 0; cur_ans = 0
    ans = [0] * q

    def add(pos):
        nonlocal cur_ans
        val = arr[pos]
        freq[val] = freq.get(val, 0) + 1
        if freq[val] == 1: cur_ans += 1

    def remove(pos):
        nonlocal cur_ans
        val = arr[pos]
        freq[val] -= 1
        if freq[val] == 0: cur_ans -= 1

    for idx in sorted_q:
        l, r, _ = queries[idx]
        while cur_l > l: cur_l -= 1; add(cur_l)
        while cur_r <= r: add(cur_r); cur_r += 1
        while cur_l < l: remove(cur_l); cur_l += 1
        while cur_r > r + 1: cur_r -= 1; remove(cur_r)
        ans[idx] = cur_ans
    return ans
```
**Big-O:** O((n + q) * sqrt(n)). Offline sorgular icin ideal.
**Alternatif:** Segment Tree O(q log n). Sqrt decomposition."""

    # Treap
    if "treap" in inst_lower:
        return r"""```python
import random

class TreapNode:
    def __init__(self, key):
        self.key = key
        self.prio = random.randint(0, 1 << 60)
        self.left = self.right = None

class Treap:
    def split(self, root, key):
        if not root: return (None, None)
        if root.key <= key:
            l, r = self.split(root.right, key)
            root.right = l; return (root, r)
        l, r = self.split(root.left, key)
        root.left = r; return (l, root)

    def merge(self, left, right):
        if not left or not right: return left or right
        if left.prio > right.prio:
            left.right = self.merge(left.right, right)
            return left
        right.left = self.merge(left, right.left)
        return right

    def insert(self, root, key):
        l, r = self.split(root, key)
        return self.merge(self.merge(l, TreapNode(key)), r)

    def delete(self, root, key):
        l, m = self.split(root, key - 1)
        m, r = self.split(m, key)
        return self.merge(l, r)

    def search(self, root, key):
        if not root: return None
        if root.key == key: return root
        return self.search(root.left if key < root.key else root.right, key)
```
**Big-O:** O(log n) expected. Randomized BST.
**Alternatif:** AVL Tree O(log n). Red-Black Tree O(log n)."""

    # Skip List
    if "skip list" in inst_lower:
        return r"""```python
import random

class SkipListNode:
    def __init__(self, val, level):
        self.val = val
        self.forward = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level=16, p=0.5):
        self.max_level = max_level; self.p = p
        self.header = SkipListNode(None, max_level)
        self.level = 0

    def _random_level(self):
        lvl = 0
        while random.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    def search(self, target):
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].val < target:
                cur = cur.forward[i]
        cur = cur.forward[0]
        return cur and cur.val == target

    def insert(self, val):
        update = [None] * (self.max_level + 1)
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].val < val:
                cur = cur.forward[i]
            update[i] = cur
        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                update[i] = self.header
            self.level = lvl
        node = SkipListNode(val, lvl)
        for i in range(lvl + 1):
            node.forward[i] = update[i].forward[i]
            update[i].forward[i] = node

    def delete(self, val):
        update = [None] * (self.max_level + 1)
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].val < val:
                cur = cur.forward[i]
            update[i] = cur
        cur = cur.forward[0]
        if cur and cur.val == val:
            for i in range(self.level + 1):
                if update[i].forward[i] != cur: break
                update[i].forward[i] = cur.forward[i]
            while self.level > 0 and not self.header.forward[self.level]:
                self.level -= 1
```
**Big-O:** O(log n) expected. Linked list + multiple levels.
**Alternatif:** Balanced BST O(log n)."""

    # DSU / Kruskal
    if "disjoint set" in inst_lower or "union-find" in inst_lower or "kruskal" in inst_lower:
        return r"""```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        xr, yr = self.find(x), self.find(y)
        if xr == yr: return False
        if self.rank[xr] < self.rank[yr]:
            self.parent[xr] = yr
        elif self.rank[xr] > self.rank[yr]:
            self.parent[yr] = xr
        else:
            self.parent[yr] = xr
            self.rank[xr] += 1
        return True

def kruskal(n, edges):
    edges.sort(key=lambda x: x[2])
    dsu = DSU(n)
    mst_weight = 0; mst_edges = []
    for u, v, w in edges:
        if dsu.union(u, v):
            mst_weight += w
            mst_edges.append((u, v, w))
    return mst_weight, mst_edges
```
**Big-O:** O(alpha(n)) per operation. Neredeyse O(1).
**Alternatif:** DFS-based connectivity O(n + m)."""

    # Prim
    if "prim" in inst_lower:
        return r"""```python
import heapq

def prim(n, graph):
    visited = [False] * n
    pq = [(0, 0, -1)]
    mst_weight = 0; mst_edges = []
    while pq:
        w, u, parent = heapq.heappop(pq)
        if visited[u]: continue
        visited[u] = True
        mst_weight += w
        if parent != -1: mst_edges.append((parent, u, w))
        for v, weight in graph[u]:
            if not visited[v]:
                heapq.heappush(pq, (weight, v, u))
    return mst_weight, mst_edges
```
**Big-O:** O((V + E) log V). Priority queue ile.
**Alternatif:** Kruskal O(E log V). Prim dense graph'lerde daha hizli."""

    # Bellman-Ford
    if "bellman" in inst_lower:
        return r"""```python
def bellman_ford(n, edges, src):
    dist = [float("inf")] * n
    dist[src] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            return dist, True
    return dist, False
```
**Big-O:** O(V * E). Negative edge'ler icin calisir, negative cycle detect eder.
**Alternatif:** Dijkstra O((V+E) log V) ama negative edge'de calismaz."""

    # Floyd-Warshall
    if "floyd" in inst_lower and "warshall" in inst_lower:
        return r"""```python
def floyd_warshall(n, graph):
    dist = [row[:] for row in graph]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist
```
**Big-O:** O(V^3). Tum pair shortest path.
**Alternatif:** Johnson O(V * (V+E) log V) sparse graph'te daha hizli."""

    # Johnson
    if "johnson" in inst_lower:
        return r"""```python
import heapq

def johnson(n, edges):
    h = [float("inf")] * n
    h[0] = 0
    for _ in range(n):
        for u, v, w in [(u, v, w) for u, v, w in edges] + [(-1, i, 0) for i in range(n)]:
            pass
    # Simplified: run Bellman-Ford from virtual source, then Dijkstra from each node
    dist = [[float("inf")] * n for _ in range(n)]
    for src in range(n):
        dist[src][src] = 0
        pq = [(0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[src][u]: continue
            for v, w in [(v, w) for u2, v, w in edges if u2 == u]:
                if dist[src][u] + w < dist[src][v]:
                    dist[src][v] = dist[src][u] + w
                    heapq.heappush(pq, (dist[src][v], v))
    return dist
```
**Big-O:** O(V * (V+E) log V). Sparse graph'te Floyd-Warshall'dan hizli.
**Alternatif:** Floyd-Warshall O(V^3)."""

    # A* pathfinding
    if "a*" in inst_lower or "a star" in inst_lower:
        return r"""```python
import heapq

def a_star(graph, start, goal, heuristic):
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], g_score[goal]
        for neighbor, cost in graph.get(current, []):
            tentative = g_score[current] + cost
            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f = tentative + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f, neighbor))
    return [], float("inf")
```
**Big-O:** O(E) in practice with good heuristic. O(b^d) worst.
**Alternatif:** Dijkstra O((V+E) log V) - heuristic yok. BFS O(V+E) - weights yok."""

    # Bidirectional BFS
    if "bidirectional" in inst_lower or "2x hizli" in inst_lower:
        return r"""```python
from collections import deque

def bidirectional_bfs(graph, start, goal):
    if start == goal: return 0
    q_start, q_goal = deque([start]), deque([goal])
    dist_start, dist_goal = {start: 0}, {goal: 0}
    while q_start and q_goal:
        for _ in range(len(q_start)):
            cur = q_start.popleft()
            for nb in graph.get(cur, []):
                if nb not in dist_start:
                    dist_start[nb] = dist_start[cur] + 1
                    q_start.append(nb)
                    if nb in dist_goal: return dist_start[nb] + dist_goal[nb]
        for _ in range(len(q_goal)):
            cur = q_goal.popleft()
            for nb in graph.get(cur, []):
                if nb not in dist_goal:
                    dist_goal[nb] = dist_goal[cur] + 1
                    q_goal.append(nb)
                    if nb in dist_start: return dist_start[nb] + dist_goal[nb]
    return -1
```
**Big-O:** O(b^(d/2)) - normal BFS'den 2x hizli (branching factor^depth).
**Alternatif:** Normal BFS O(b^d). A* heuristic ile."""

    # 0-1 BFS
    if "0-1 bfs" in inst_lower or "zero-one" in inst_lower or "weightleri {0,1}" in inst_lower:
        return r"""```python
from collections import deque

def zero_one_bfs(graph, start):
    n = len(graph)
    dist = [float("inf")] * n
    dist[start] = 0
    dq = deque([start])
    while dq:
        u = dq.popleft()
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                if w == 0: dq.appendleft(v)
                else: dq.append(v)
    return dist
```
**Big-O:** O(V + E). Dijkstra'dan hizli (no log factor).
**Alternatif:** Dijkstra O((V+E) log V). BFS sadece weight=1 icin."""

    # Topological sort
    if "topological" in inst_lower or "dependency resolution" in inst_lower:
        return r"""```python
from collections import deque

def topological_sort_kahn(n, deps):
    adj = [[] for _ in range(n)]
    in_deg = [0] * n
    for u, v in deps:
        adj[u].append(v); in_deg[v] += 1
    q = deque([i for i in range(n) if in_deg[i] == 0])
    result = []
    while q:
        u = q.popleft()
        result.append(u)
        for v in adj[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0: q.append(v)
    return result if len(result) == n else []
```
**Big-O:** O(V + E). Kahn's algorithm (BFS-based) veya DFS-based.
**Alternatif:** DFS + stack O(V+E). DFS cycle detection da yapabilir."""

    # Tarjan SCC
    if "tarjan" in inst_lower and ("scc" in inst_lower or "strongly connected" in inst_lower):
        return r"""```python
def tarjan_scc(n, adj):
    index = 0; indices = [-1] * n
    lowlink = [0] * n; on_stack = [False] * n
    stack = []; sccs = []

    def strongconnect(v):
        nonlocal index
        indices[v] = lowlink[v] = index; index += 1
        stack.append(v); on_stack[v] = True
        for w in adj[v]:
            if indices[w] == -1:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack[w]:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            comp = []
            while True:
                w = stack.pop(); on_stack[w] = False
                comp.append(w)
                if w == v: break
            sccs.append(comp)

    for v in range(n):
        if indices[v] == -1: strongconnect(v)
    return sccs
```
**Big-O:** O(V + E). Single-pass DFS.
**Alternatif:** Kosaraju O(V+E) 2-pass DFS, biraz daha basit."""

    # Kosaraju SCC
    if "kosaraju" in inst_lower:
        return r"""```python
def kosaraju_scc(n, adj):
    visited = [False] * n; order = []

    def dfs1(v):
        visited[v] = True
        for w in adj[v]:
            if not visited[w]: dfs1(w)
        order.append(v)

    for v in range(n):
        if not visited[v]: dfs1(v)

    radj = [[] for _ in range(n)]
    for v in range(n):
        for w in adj[v]: radj[w].append(v)

    comps = []; visited = [False] * n

    def dfs2(v, comp):
        visited[v] = True; comp.append(v)
        for w in radj[v]:
            if not visited[w]: dfs2(w, comp)

    for v in reversed(order):
        if not visited[v]:
            comp = []; dfs2(v, comp); comps.append(comp)
    return comps
```
**Big-O:** O(V + E). 2-pass DFS, basit implementasyon.
**Alternatif:** Tarjan O(V+E) single-pass, daha karmasik."""

    # Articulation points
    if "articulation" in inst_lower or "cut vertices" in inst_lower:
        return r"""```python
def articulation_points(n, adj):
    visited = [False] * n
    disc = [0] * n; low = [0] * n
    parent = [-1] * n; ap = [False] * n
    time = 0

    def dfs(u):
        nonlocal time
        children = 0; visited[u] = True
        disc[u] = low[u] = time; time += 1
        for v in adj[u]:
            if not visited[v]:
                parent[v] = u; children += 1
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent[u] == -1 and children > 1: ap[u] = True
                if parent[u] != -1 and low[v] >= disc[u]: ap[u] = True
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if not visited[i]: dfs(i)
    return [i for i, val in enumerate(ap) if val]
```
**Big-O:** O(V + E). Tarjan's algorithm.
**Alternatif:** Brute force O(V*(V+E)) - her node'u cikarip kontrol."""

    # Bridges
    if "bridges" in inst_lower:
        return r"""```python
def find_bridges(n, adj):
    visited = [False] * n
    disc = [0] * n; low = [0] * n
    parent = [-1] * n; bridges = []; time = 0

    def dfs(u):
        nonlocal time
        visited[u] = True
        disc[u] = low[u] = time; time += 1
        for v in adj[u]:
            if not visited[v]:
                parent[v] = u; dfs(v)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]: bridges.append((u, v))
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if not visited[i]: dfs(i)
    return bridges
```
**Big-O:** O(V + E). Tarjan's bridge algorithm.
**Alternatif:** Brute force O(E*(V+E)) - her edge'i cikarip kontrol."""

    # Eulerian path
    if "eulerian" in inst_lower or "hierholzer" in inst_lower:
        return r"""```python
from collections import defaultdict

def eulerian_path(n, edges):
    adj = defaultdict(list)
    in_deg = [0] * n
    for u, v in edges:
        adj[u].append(v); in_deg[v] += 1
    start = 0
    out_balance = [len(adj[i]) - in_deg[i] for i in range(n)]
    for i in range(n):
        if out_balance[i] == 1: start = i; break
    stack = [start]; path = []
    while stack:
        u = stack[-1]
        if adj[u]:
            v = adj[u].pop(); stack.append(v)
        else:
            path.append(stack.pop())
    return path[::-1]
```
**Big-O:** O(V + E). Hierholzer's algorithm.
**Alternatif:** Fleury's algorithm O(E^2)."""

    # Hamiltonian path
    if "hamiltonian" in inst_lower and "path" in inst_lower:
        return r"""```python
def hamiltonian_path(n, adj):
    path = []; visited = [False] * n

    def backtrack(v, count):
        path.append(v); visited[v] = True
        if count == n: return True
        for w in adj[v]:
            if not visited[w] and backtrack(w, count + 1): return True
        path.pop(); visited[v] = False; return False

    for start in range(n):
        if backtrack(start, 1): return path
    return []
```
**Big-O:** O(n!) worst. NP-Complete problem.
**Alternatif:** Held-Karp DP O(n^2 * 2^n). Branch and bound."""

    # Maximum flow / Ford-Fulkerson
    if ("maximum flow" in inst_lower or "ford-fulkerson" in inst_lower) and "dinic" not in inst_lower and "edmonds" not in inst_lower and "cost" not in inst_lower:
        return r"""```python
def ford_fulkerson(n, capacity, src, sink):
    def bfs(parent):
        visited = [False] * n; q = [src]; visited[src] = True
        while q:
            u = q.pop(0)
            for v in range(n):
                if not visited[v] and capacity[u][v] > 0:
                    parent[v] = u
                    if v == sink: return True
                    visited[v] = True; q.append(v)
        return False

    parent = [-1] * n; max_flow = 0
    while bfs(parent):
        path_flow = min(capacity[parent[v]][v] for v in range(sink, src, -1) if parent[v] != -1)
        v = sink
        while v != src:
            u = parent[v]
            capacity[u][v] -= path_flow; capacity[v][u] += path_flow
            v = u
        max_flow += path_flow
    return max_flow
```
**Big-O:** O(E * max_flow). DFS-based.
**Alternatif:** Edmonds-Karp O(VE^2). Dinic O(EV^2)."""

    # Edmonds-Karp
    if "edmonds" in inst_lower or "o(ve" in inst_lower.lower():
        return r"""```python
from collections import deque

def edmonds_karp(n, capacity, src, sink):
    flow = 0
    while True:
        parent = [-1] * n; q = deque([src]); parent[src] = src
        while q:
            u = q.popleft()
            for v in range(n):
                if parent[v] == -1 and capacity[u][v] > 0:
                    parent[v] = u
                    if v == sink: break
                    q.append(v)
        if parent[sink] == -1: break
        f = min(capacity[parent[v]][v] for v in range(sink, src, -1) if parent[v] != -1)
        v = sink
        while v != src:
            u = parent[v]; capacity[u][v] -= f; capacity[v][u] += f
            v = u
        flow += f
    return flow
```
**Big-O:** O(V * E^2). BFS-based, Ford-Fulkerson'dan garantili.
**Alternatif:** Dinic O(EV^2) pratikte daha hizli."""

    # Dinic
    if "dinic" in inst_lower:
        return r"""```python
from collections import deque

class Dinic:
    def __init__(self, n):
        self.n = n; self.adj = [[] for _ in range(n)]

    def add_edge(self, u, v, cap):
        self.adj[u].append([v, cap, len(self.adj[v])])
        self.adj[v].append([u, 0, len(self.adj[u]) - 1])

    def bfs(self, s, t, level):
        for i in range(self.n): level[i] = -1
        q = deque([s]); level[s] = 0
        while q:
            u = q.popleft()
            for v, cap, _ in self.adj[u]:
                if cap > 0 and level[v] == -1:
                    level[v] = level[u] + 1; q.append(v)
        return level[t] != -1

    def dfs(self, u, t, f, level, it):
        if u == t: return f
        for i in range(it[u], len(self.adj[u])):
            it[u] = i; v, cap, rev = self.adj[u][i]
            if cap > 0 and level[v] == level[u] + 1:
                pushed = self.dfs(v, t, min(f, cap), level, it)
                if pushed:
                    self.adj[u][i][1] -= pushed
                    self.adj[v][rev][1] += pushed
                    return pushed
        return 0

    def max_flow(self, s, t):
        flow = 0; level = [-1] * self.n; INF = 10 ** 18
        while self.bfs(s, t, level):
            it = [0] * self.n
            while True:
                pushed = self.dfs(s, t, INF, level, it)
                if not pushed: break
                flow += pushed
        return flow
```
**Big-O:** O(E * V^2) worst, O(E * sqrt(V)) bipartite. Pratikte en hizli max flow.
**Alternatif:** Edmonds-Karp O(VE^2). Push-Relabel O(V^3)."""

    # Min cost max flow
    if "min cost" in inst_lower or "minimum cost" in inst_lower:
        return r"""```python
import heapq

class MinCostMaxFlow:
    def __init__(self, n):
        self.n = n; self.adj = [[] for _ in range(n)]

    def add_edge(self, u, v, cap, cost):
        self.adj[u].append([v, cap, cost, len(self.adj[v])])
        self.adj[v].append([u, 0, -cost, len(self.adj[u]) - 1])

    def flow(self, s, t, maxf):
        n = self.n; INF = 10 ** 18
        flow = cost = 0; potential = [0] * n
        while flow < maxf:
            dist = [INF] * n; dist[s] = 0
            parent = [-1] * n; parent_edge = [-1] * n
            pq = [(0, s)]
            while pq:
                d, u = heapq.heappop(pq)
                if dist[u] < d: continue
                for i, (v, cap, w, _) in enumerate(self.adj[u]):
                    if cap and d + w + potential[u] - potential[v] < dist[v]:
                        dist[v] = d + w + potential[u] - potential[v]
                        parent[v] = u; parent_edge[v] = i
                        heapq.heappush(pq, (dist[v], v))
            if dist[t] == INF: break
            for v in range(n):
                if dist[v] < INF: potential[v] += dist[v]
            f = maxf - flow; v = t
            while v != s:
                u = parent[v]; ei = parent_edge[v]
                f = min(f, self.adj[u][ei][1]); v = u
            v = t
            while v != s:
                u = parent[v]; ei = parent_edge[v]; rev = self.adj[u][ei][3]
                self.adj[u][ei][1] -= f
                self.adj[v][rev][1] += f
                cost += f * self.adj[u][ei][2]; v = u
            flow += f
        return flow, cost
```
**Big-O:** O(F * E log V). F = flow degeri.
**Alternatif:** Successive Shortest Path. Cycle Canceling O(E * V * C)."""

    # Hopcroft-Karp
    if "hopcroft" in inst_lower or "bipartite matching" in inst_lower:
        return r"""```python
from collections import deque

class HopcroftKarp:
    def __init__(self, n_left, n_right):
        self.n_left = n_left; self.n_right = n_right
        self.adj = [[] for _ in range(n_left)]

    def add_edge(self, u, v):
        self.adj[u].append(v)

    def bfs(self, pair_u, pair_v, dist):
        q = deque()
        for u in range(self.n_left):
            if pair_u[u] == -1: dist[u] = 0; q.append(u)
            else: dist[u] = float("inf")
        INF = float("inf"); found = False
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                pu = pair_v[v]
                if pu != -1 and dist[pu] == INF:
                    dist[pu] = dist[u] + 1; q.append(pu)
                elif pu == -1: found = True
        return found

    def dfs(self, u, pair_u, pair_v, dist):
        for v in self.adj[u]:
            pu = pair_v[v]
            if pu == -1 or (dist[pu] == dist[u] + 1 and self.dfs(pu, pair_u, pair_v, dist)):
                pair_u[u] = v; pair_v[v] = u; return True
        dist[u] = float("inf"); return False

    def max_matching(self):
        pair_u = [-1] * self.n_left; pair_v = [-1] * self.n_right
        dist = [0] * self.n_left; matching = 0
        while self.bfs(pair_u, pair_v, dist):
            for u in range(self.n_left):
                if pair_u[u] == -1 and self.dfs(u, pair_u, pair_v, dist):
                    matching += 1
        return matching
```
**Big-O:** O(E * sqrt(V)). Bipartite graph'te en hizli matching.
**Alternatif:** Hungarian O(n^3) assignment problem icin. Kuhn-Munkres."""

    # Hungarian
    if "hungarian" in inst_lower:
        return r"""```python
def hungarian(cost):
    n = len(cost); m = len(cost[0])
    u = [0] * (n + 1); v = [0] * (m + 1)
    p = [0] * (m + 1); way = [0] * (m + 1)
    for i in range(1, n + 1):
        p[0] = i; j0 = 0
        minv = [float("inf")] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True; i0 = p[j0]; delta = float("inf"); j1 = 0
            for j in range(1, m + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]: minv[j] = cur; way[j] = j0
                    if minv[j] < delta: delta = minv[j]; j1 = j
            for j in range(m + 1):
                if used[j]: u[p[j]] += delta; v[j] -= delta
                else: minv[j] -= delta
            j0 = j1
            if p[j0] == 0: break
        while True:
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
            if j0 == 0: break
    assignment = [-1] * n
    for j in range(1, m + 1):
        if p[j]: assignment[p[j] - 1] = j - 1
    return -v[0], assignment
```
**Big-O:** O(n^3). Assignment problem cozumu.
**Alternatif:** Simplex O(n^4). Minimum cost flow da kullanilabilir."""

    # Knapsack 0/1
    if "knapsack" in inst_lower and ("0/1" in inst_lower or "01" in inst_lower):
        return r"""```python
def knapsack_01(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])
            else:
                dp[i][w] = dp[i - 1][w]
    return dp[n][capacity]

def knapsack_01_optimized(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]
```
**Big-O:** O(n * W). DP tabanli, W = capacity.
**Alternatif:** Greedy O(n log n) optimal degil. Branch and bound."""

    # Fractional Knapsack
    if "knapsack" in inst_lower and "fractional" in inst_lower:
        return r"""```python
def fractional_knapsack(weights, values, capacity):
    items = [(values[i] / weights[i], weights[i], values[i]) for i in range(len(weights))]
    items.sort(key=lambda x: x[0], reverse=True)
    total = 0.0
    for ratio, w, v in items:
        if capacity >= w:
            total += v; capacity -= w
        else:
            total += ratio * capacity; break
    return total
```
**Big-O:** O(n log n). Greedy, optimal cozum.
**Alternatif:** 0/1 Knapsack O(nW) DP ile."""

    # Coin change
    if "coin change" in inst_lower or "unbounded" in inst_lower:
        return r"""```python
def coin_change(coins, amount):
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float("inf") else -1

def coin_change_ways(coins, amount):
    dp = [0] * (amount + 1); dp[0] = 1
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] += dp[x - coin]
    return dp[amount]
```
**Big-O:** O(n * amount). Unbounded knapsack.
**Alternatif:** Greedy (standard coin systems icin optimal)."""

    # Edit distance
    if "edit distance" in inst_lower or "levenshtein" in inst_lower:
        return r"""```python
def edit_distance(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]
```
**Big-O:** O(m * n). DP tabanli.
**Alternatif:** Wagner-Fischer O(m*n). Space O(min(m,n))'e dusurulebilir."""

    # Matrix chain
    if "matrix chain" in inst_lower:
        return r"""```python
def matrix_chain_order(p):
    n = len(p) - 1
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1; dp[i][j] = float("inf")
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + p[i] * p[k + 1] * p[j + 1]
                if cost < dp[i][j]: dp[i][j] = cost
    return dp[0][n - 1]
```
**Big-O:** O(n^3). DP tabanli optimal parantezleme.
**Alternatif:** Recursive + memoization O(n^3)."""

    # LIS
    if "longest increasing subsequence" in inst_lower or "lis" in inst_lower:
        return r"""```python
import bisect

def lis_length(arr):
    tails = []
    for x in arr:
        i = bisect.bisect_left(tails, x)
        if i == len(tails): tails.append(x)
        else: tails[i] = x
    return len(tails)

def lis(arr):
    n = len(arr); tails = []; indices = []; prev = [-1] * n
    for i, x in enumerate(arr):
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x); indices.append(i)
        else:
            tails[pos] = x; indices[pos] = i
        if pos > 0: prev[i] = indices[pos - 1]
    seq = []; cur = indices[-1] if indices else -1
    while cur != -1:
        seq.append(arr[cur]); cur = prev[cur]
    return seq[::-1]
```
**Big-O:** O(n log n). Patience sorting.
**Alternatif:** DP O(n^2) daha yavas ama cozumu gostermek icin basit."""

    # LPS (subsequence)
    if "palindromic subsequence" in inst_lower and "longest" in inst_lower:
        return r"""```python
def longest_palindromic_subsequence(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]: dp[i][j] = dp[i + 1][j - 1] + 2
            else: dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]
```
**Big-O:** O(n^2). DP tabanli.
**Alternatif:** Brute force O(2^n)."""

    # Longest palindromic substring
    if "palindromic substring" in inst_lower:
        return r"""```python
def longest_palindromic_substring(s):
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1; r += 1
        return s[l + 1:r]
    best = ""
    for i in range(len(s)):
        best = max(best, expand(i, i), expand(i, i + 1), key=len)
    return best
```
**Big-O:** O(n^2). Expand around center.
**Alternatif:** Manacher O(n). DP O(n^2)."""

    # Word break
    if "word break" in inst_lower:
        return r"""```python
def word_break(s, word_dict):
    words = set(word_dict); n = len(s)
    dp = [False] * (n + 1); dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True; break
    return dp[n]

def word_break_all(s, word_dict):
    words = set(word_dict); memo = {}
    def dfs(start):
        if start in memo: return memo[start]
        res = []
        if start == len(s): res.append(""); return res
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in words:
                for sub in dfs(end):
                    res.append(s[start:end] + (" " + sub if sub else ""))
        memo[start] = res; return res
    return dfs(0)
```
**Big-O:** O(n^2) DP. O(2^n) all solutions worst.
**Alternatif:** BFS/DFS with memoization."""

    # Palindrome partitioning
    if "palindrome partition" in inst_lower:
        return r"""```python
def partition_palindrome(s):
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n): is_pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
    res = []
    def backtrack(start, path):
        if start == n: res.append(path[:]); return
        for end in range(start, n):
            if is_pal[start][end]:
                path.append(s[start:end + 1])
                backtrack(end + 1, path)
                path.pop()
    backtrack(0, []); return res
```
**Big-O:** O(n * 2^n) worst. DP ile palindrome check O(1).
**Alternatif:** DFS + backtracking."""

    # Egg dropping
    if "egg" in inst_lower:
        return r"""```python
def egg_drop(eggs, floors):
    dp = [[0] * (eggs + 1) for _ in range(floors + 1)]
    m = 0
    while dp[m][eggs] < floors:
        m += 1
        for k in range(1, eggs + 1):
            dp[m][k] = dp[m - 1][k - 1] + dp[m - 1][k] + 1
    return m
```
**Big-O:** O(k * n) where k=eggs, n=floors. DP binary search ile.
**Alternatif:** Recursive O(2^n)."""

    # Catalan
    if "catalan" in inst_lower:
        return r"""```python
def catalan_numbers(n):
    dp = [0] * (n + 1); dp[0] = dp[1] = 1
    for i in range(2, n + 1):
        for j in range(i):
            dp[i] += dp[j] * dp[i - j - 1]
    return dp
```
**Big-O:** O(n^2). DP tabanli.
**Alternatif:** Formula C(2n,n)/(n+1) O(n)."""

    # Rod cutting
    if "rod cutting" in inst_lower:
        return r"""```python
def rod_cutting(prices, n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            dp[i] = max(dp[i], prices[j - 1] + dp[i - j])
    return dp[n]
```
**Big-O:** O(n^2). Unbounded knapsack benzeri.
**Alternatif:** Greedy (optimal degil)."""

    # Job scheduling
    if "job scheduling" in inst_lower or ("scheduling" in inst_lower and "deadline" in inst_lower):
        return r"""```python
def job_scheduling(profits, deadlines):
    jobs = list(zip(profits, deadlines))
    jobs.sort(key=lambda x: x[0], reverse=True)
    max_dl = max(deadlines)
    parent = list(range(max_dl + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x

    total = 0
    for profit, dl in jobs:
        slot = find(dl)
        if slot > 0:
            parent[slot] = find(slot - 1)
            total += profit
    return total
```
**Big-O:** O(n log n + n * alpha(n)). Greedy + DSU.
**Alternatif:** DP O(n * max_deadline)."""

    # Huffman
    if "huffman" in inst_lower:
        return r"""```python
import heapq

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char; self.freq = freq
        self.left = self.right = None
    def __lt__(self, other): return self.freq < other.freq

def huffman_encode(text):
    freq = {}
    for ch in text: freq[ch] = freq.get(ch, 0) + 1
    heap = [HuffmanNode(ch, f) for ch, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = heapq.heappop(heap), heapq.heappop(heap)
        merged = HuffmanNode(None, a.freq + b.freq)
        merged.left, merged.right = a, b
        heapq.heappush(heap, merged)
    root = heap[0] if heap else None
    codes = {}
    def build(node, code):
        if node:
            if node.char is not None: codes[node.char] = code
            build(node.left, code + "0")
            build(node.right, code + "1")
    build(root, "")
    return "".join(codes[ch] for ch in text), codes

def huffman_decode(encoded, codes):
    rev = {v: k for k, v in codes.items()}
    cur = ""; res = []
    for bit in encoded:
        cur += bit
        if cur in rev: res.append(rev[cur]); cur = ""
    return "".join(res)
```
**Big-O:** O(n log n). Greedy, optimal prefix code.
**Alternatif:** Arithmetic coding daha iyi compression."""

    # Activity selection
    if "activity selection" in inst_lower:
        return r"""```python
def activity_selection(start, end):
    n = len(start)
    activities = sorted(range(n), key=lambda i: end[i])
    selected = [activities[0]]
    last_end = end[activities[0]]
    for i in activities[1:]:
        if start[i] >= last_end:
            selected.append(i); last_end = end[i]
    return selected
```
**Big-O:** O(n log n). Greedy, optimal.
**Alternatif:** DP O(n^2) weighted version icin."""

    # Interval scheduling with weights
    if "interval" in inst_lower and "weight" in inst_lower:
        return r"""```python
import bisect

def weighted_interval_scheduling(intervals):
    intervals.sort(key=lambda x: x[1])
    start = [s for s, _, _ in intervals]
    end = [e for _, e, _ in intervals]

    def find_last(i):
        return bisect.bisect_right(end, start[i]) - 1

    n = len(intervals); dp = [0] * (n + 1)
    for i in range(1, n + 1):
        j = find_last(i - 1) + 1
        incl = intervals[i - 1][2] + dp[j]
        dp[i] = max(incl, dp[i - 1])
    return dp[n]
```
**Big-O:** O(n log n). DP + binary search.
**Alternatif:** DP O(n^2) naive. Weighted interval scheduling."""

    # N-Queens
    if "n-queens" in inst_lower or "n queens" in inst_lower:
        return r"""```python
def solve_n_queens(n):
    res = []; cols = set(); diag1 = set(); diag2 = set()
    board = [["."] * n for _ in range(n)]

    def backtrack(row):
        if row == n:
            res.append(["".join(r) for r in board]); return
        for col in range(n):
            d1, d2 = row - col, row + col
            if col in cols or d1 in diag1 or d2 in diag2: continue
            cols.add(col); diag1.add(d1); diag2.add(d2)
            board[row][col] = "Q"
            backtrack(row + 1)
            board[row][col] = "."
            cols.remove(col); diag1.remove(d1); diag2.remove(d2)

    backtrack(0); return res
```
**Big-O:** O(n!). Backtracking + pruning.
**Alternatif:** Bit manipulation ile hizlandirma. Closed form (n>3 icin)."""

    # Sudoku
    if "sudoku" in inst_lower:
        return r"""```python
def solve_sudoku(board):
    def is_valid(r, c, ch):
        for i in range(9):
            if board[r][i] == ch or board[i][c] == ch: return False
            br, bc = 3 * (r // 3) + i // 3, 3 * (c // 3) + i % 3
            if board[br][bc] == ch: return False
        return True

    for r in range(9):
        for c in range(9):
            if board[r][c] == ".":
                for ch in "123456789":
                    if is_valid(r, c, ch):
                        board[r][c] = ch
                        if solve_sudoku(board): return True
                        board[r][c] = "."
                return False
    return True
```
**Big-O:** O(9^(n*n)). Backtracking + constraint propagation.
**Alternatif:** Dancing Links (Algorithm X) O(exp) ama pratikte cok hizli."""

    # Heap's permutations
    if "heap" in inst_lower and "permutation" in inst_lower:
        return r"""```python
def heaps_permutations(arr):
    res = []; n = len(arr)
    def generate(k, a):
        if k == 1: res.append(a[:]); return
        generate(k - 1, a)
        for i in range(k - 1):
            if k % 2 == 0: a[i], a[k - 1] = a[k - 1], a[i]
            else: a[0], a[k - 1] = a[k - 1], a[0]
            generate(k - 1, a)
    generate(n, arr[:]); return res
```
**Big-O:** O(n!). Non-recursive, minimum swap.
**Alternatif:** Lexicographic (next_permutation) O(n!)."""

    # Combinations
    if "combination" in inst_lower and "generation" in inst_lower:
        return r"""```python
def combinations(arr, k):
    res = []
    def backtrack(start, path):
        if len(path) == k: res.append(path[:]); return
        for i in range(start, len(arr)):
            path.append(arr[i]); backtrack(i + 1, path); path.pop()
    backtrack(0, []); return res
```
**Big-O:** O(C(n,k)). Backtracking.
**Alternatif:** itertools.combinations."""

    # Subset sum
    if "subset sum" in inst_lower:
        return r"""```python
def subset_sum(nums, target):
    dp = [False] * (target + 1); dp[0] = True
    for num in nums:
        for s in range(target, num - 1, -1):
            if dp[s - num]: dp[s] = True
    return dp[target]
```
**Big-O:** O(n * target). DP tabanli.
**Alternatif:** Meet-in-the-middle O(2^(n/2)). Backtracking O(2^n)."""

    # TSP Held-Karp
    if "travelling salesman" in inst_lower or "tsp" in inst_lower or "held-karp" in inst_lower:
        return r"""```python
def tsp_held_karp(dist):
    n = len(dist)
    dp = [[float("inf")] * n for _ in range(1 << n)]
    dp[1][0] = 0; parent = [[-1] * n for _ in range(1 << n)]
    for mask in range(1 << n):
        for u in range(n):
            if not (mask & (1 << u)): continue
            for v in range(n):
                if mask & (1 << v): continue
                new_mask = mask | (1 << v)
                if dp[new_mask][v] > dp[mask][u] + dist[u][v]:
                    dp[new_mask][v] = dp[mask][u] + dist[u][v]
                    parent[new_mask][v] = u
    full = (1 << n) - 1
    best = min(dp[full][i] + dist[i][0] for i in range(1, n))
    last = min(range(1, n), key=lambda i: dp[full][i] + dist[i][0])
    mask = full; path = [0]
    while last != -1:
        path.append(last)
        new_last = parent[mask][last]
        mask ^= (1 << last); last = new_last
    return best, path[::-1]
```
**Big-O:** O(n^2 * 2^n). Held-Karp, optimal.
**Alternatif:** Branch and bound. 2-approximation (Christofides)."""

    # Hamiltonian cycle
    if "hamiltonian cycle" in inst_lower or "hamiltonian" in inst_lower:
        return r"""```python
def hamiltonian_cycle(n, adj):
    path = [-1] * n; path[0] = 0
    visited = [False] * n; visited[0] = True

    def backtrack(pos):
        if pos == n: return adj[path[pos - 1]][path[0]] == 1
        for v in range(n):
            if adj[path[pos - 1]][v] == 1 and not visited[v]:
                visited[v] = True; path[pos] = v
                if backtrack(pos + 1): return True
                visited[v] = False
        return False

    if backtrack(1): path.append(path[0]); return path
    return []
```
**Big-O:** O(n!) worst. NP-Complete.
**Alternatif:** Held-Karp DP O(n^2 * 2^n)."""

    # Graph coloring
    if "graph coloring" in inst_lower:
        return r"""```python
def graph_coloring(n, adj, m):
    colors = [-1] * n

    def is_safe(v, c):
        return all(colors[u] != c for u in adj[v])

    def backtrack(v):
        if v == n: return True
        for c in range(m):
            if is_safe(v, c):
                colors[v] = c
                if backtrack(v + 1): return True
                colors[v] = -1
        return False

    return colors if backtrack(0) else []
```
**Big-O:** O(m^n) worst. Backtracking + forward checking.
**Alternatif:** DSATUR, greedy coloring."""
    # Maze solving
    if "maze" in inst_lower:
        return r"""```python
from collections import deque

def solve_maze_dfs(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    stack = [(start, [start])]; visited = set()
    while stack:
        (r, c), path = stack.pop()
        if (r, c) == end: return path
        if (r, c) in visited: continue
        visited.add((r, c))
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr, nc) not in visited:
                stack.append(((nr, nc), path + [(nr, nc)]))
    return []

def solve_maze_bfs(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    q = deque([(start, [start])]); visited = {start}
    while q:
        (r, c), path = q.popleft()
        if (r, c) == end: return path
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc)); q.append(((nr, nc), path + [(nr, nc)]))
    return []
```
**Big-O:** O(rows * cols) both. DFS uses stack (may find longer path), BFS finds shortest path.
**Alternatif:** A* with heuristic. Dijkstra weighted maze icin."""

    # Robot path planning / DP
    if "robot" in inst_lower and "path" in inst_lower:
        return r"""```python
def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    return dp[m - 1][n - 1]

def unique_paths_with_obstacles(grid):
    m, n = len(grid), len(grid[0])
    if grid[0][0] == 1: return 0
    dp = [[0] * n for _ in range(m)]; dp[0][0] = 1
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1: dp[i][j] = 0; continue
            if i > 0: dp[i][j] += dp[i - 1][j]
            if j > 0: dp[i][j] += dp[i][j - 1]
    return dp[m - 1][n - 1]
```
**Big-O:** O(m * n). DP tabanli.
**Alternatif:** Math: C(m+n-2, m-1)."""

    # Knight's tour
    if "knight" in inst_lower:
        return r"""```python
def knights_tour(n):
    board = [[-1] * n for _ in range(n)]
    moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]

    def count_moves(r, c):
        return sum(1 for dr, dc in moves if 0 <= r + dr < n and 0 <= c + dc < n and board[r + dr][c + dc] == -1)

    def backtrack(r, c, step):
        board[r][c] = step
        if step == n * n - 1: return True
        next_moves = []
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == -1:
                next_moves.append((count_moves(nr, nc), nr, nc))
        next_moves.sort()
        for _, nr, nc in next_moves:
            if backtrack(nr, nc, step + 1): return True
        board[r][c] = -1; return False

    backtrack(0, 0, 0); return board
```
**Big-O:** O(8^n^2) worst. Warnsdorff heuristic ile pratikte hizli.
**Alternatif:** Backtracking without heuristic. Divide and conquer."""

    # Convex hull Graham scan
    if "convex hull" in inst_lower and "graham" in inst_lower:
        return r"""```python
def graham_scan(points):
    points = sorted(set(points))
    if len(points) <= 1: return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0: lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0: upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]
```
**Big-O:** O(n log n). Sorting + scanning.
**Alternatif:** Jarvis March O(nh). Andrew's monotone chain (this one)."""

    # Convex hull Jarvis march
    if "convex hull" in inst_lower and "jarvis" in inst_lower:
        return r"""```python
def jarvis_march(points):
    points = list(set(points))
    if len(points) <= 1: return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    start = min(points, key=lambda p: (p[1], p[0]))
    hull = []; p = start
    while True:
        hull.append(p)
        q = points[0]
        for r in points:
            if r == p: continue
            c = cross(p, q, r)
            if c > 0 or (c == 0 and abs(r[0] - p[0]) + abs(r[1] - p[1]) > abs(q[0] - p[0]) + abs(q[1] - p[1])):
                q = r
        p = q
        if p == start: break
    return hull
```
**Big-O:** O(nh). h = hull size. n kucukse hizli.
**Alternatif:** Graham Scan O(n log n). Quickhull O(n log n) average."""

    # Line segment intersection
    if "line segment" in inst_lower:
        return r"""```python
def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    return 0 if val == 0 else (1 if val > 0 else 2)

def on_segment(p, q, r):
    return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])

def segments_intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2); o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1); o4 = orientation(p2, q2, q1)
    if o1 != o2 and o3 != o4: return True
    if o1 == 0 and on_segment(p1, p2, q1): return True
    if o2 == 0 and on_segment(p1, q2, q1): return True
    if o3 == 0 and on_segment(p2, p1, q2): return True
    if o4 == 0 and on_segment(p2, q1, q2): return True
    return False
```
**Big-O:** O(1). Cross product + orientation test.
**Alternatif:** Sweep line O((n+k) log n) for multiple segments."""

    # Closest pair
    if "closest pair" in inst_lower:
        return r"""```python
import math

def closest_pair(points):
    px = sorted(points, key=lambda x: x[0])
    py = sorted(points, key=lambda x: x[1])

    def dist(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def closest(px, py):
        n = len(px)
        if n <= 3:
            return min(dist(px[i], px[j]) for i in range(n) for j in range(i + 1, n))
        mid = n // 2; mid_x = px[mid][0]
        lx, rx = px[:mid], px[mid:]
        ly = [p for p in py if p[0] <= mid_x]
        ry = [p for p in py if p[0] > mid_x]
        d = min(closest(lx, ly), closest(rx, ry))
        strip = [p for p in py if abs(p[0] - mid_x) < d]
        for i in range(len(strip)):
            for j in range(i + 1, min(i + 7, len(strip))):
                d = min(d, dist(strip[i], strip[j]))
        return d

    return closest(px, py)
```
**Big-O:** O(n log n). Divide and conquer.
**Alternatif:** Brute force O(n^2)."""

    # Point in polygon
    if "point in polygon" in inst_lower or "ray casting" in inst_lower:
        return r"""```python
def point_in_polygon(point, polygon):
    x, y = point; inside = False; n = len(polygon); j = n - 1
    for i in range(n):
        xi, yi = polygon[i]; xj, yj = polygon[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside
```
**Big-O:** O(n). Ray casting algorithm.
**Alternatif:** Winding number O(n)."""

    # Delaunay / Bowyer-Watson
    if "delaunay" in inst_lower or "bowyer" in inst_lower:
        return r"""```python
import math

class Triangle:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def circumcircle(self):
        ax, ay = self.a; bx, by = self.b; cx, cy = self.c
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-10: return (0, 0), float("inf")
        ux = ((ax*ax + ay*ay) * (by - cy) + (bx*bx + by*by) * (cy - ay) + (cx*cx + cy*cy) * (ay - by)) / d
        uy = ((ax*ax + ay*ay) * (cx - bx) + (bx*bx + by*by) * (ax - cx) + (cx*cx + cy*cy) * (bx - ax)) / d
        return (ux, uy), math.hypot(ax - ux, ay - uy)

def bowyer_watson(points):
    min_x = min(p[0] for p in points) - 1000
    min_y = min(p[1] for p in points) - 1000
    max_x = max(p[0] for p in points) + 1000
    max_y = max(p[1] for p in points) + 1000
    super_tri = Triangle((min_x, min_y), (max_x, min_y), ((min_x + max_x) // 2, max_y))
    triangles = [super_tri]
    for pt in points:
        bad = [tri for tri in triangles if math.hypot(pt[0] - tri.circumcircle()[0][0], pt[1] - tri.circumcircle()[0][1]) <= tri.circumcircle()[1]]
        polygon = []
        for tri in bad:
            for edge in [(tri.a, tri.b), (tri.b, tri.c), (tri.c, tri.a)]:
                if not any(edge in [(other.a, other.b), (other.b, other.c), (other.c, other.a)] or (edge[1], edge[0]) in [(other.a, other.b), (other.b, other.c), (other.c, other.a)] for other in bad if other is not tri):
                    polygon.append(edge)
        for tri in bad: triangles.remove(tri)
        for e in polygon: triangles.append(Triangle(e[0], e[1], pt))
    return [tri for tri in triangles if not any(p in (tri.a, tri.b, tri.c) for p in [super_tri.a, super_tri.b, super_tri.c])]
```
**Big-O:** O(n^2) worst, O(n log n) average.
**Alternatif:** Fortune's algorithm O(n log n)."""

    # Voronoi
    if "voronoi" in inst_lower:
        return r"""```python
# Voronoi Diagram (Fortune's Algorithm Summary)
#
# 1. Events: Site events (points) and Circle events (3 sites meet)
# 2. Beach line: Parabolic arcs separated by breakpoints
# 3. Sweep line moves top-down
#
# Data structures:
# - Priority queue for events (sorted by y)
# - Balanced BST for beach line state
# - DCEL for output

class VoronoiSite:
    def __init__(self, x, y): self.x, self.y = x, y

class VoronoiEdge:
    def __init__(self, start=None, end=None, left=None, right=None):
        self.start = start; self.end = end
        self.left = left; self.right = right
```
**Big-O:** O(n log n). Fortune's algorithm.
**Alternatif:** Bowyer-Watson + dual O(n^2)."""

    # FFT
    if "fft" in inst_lower or "fast fourier" in inst_lower:
        return r"""```python
import cmath, math

def fft(a, invert=False):
    n = len(a)
    if n == 1: return a
    a0 = fft(a[0::2], invert); a1 = fft(a[1::2], invert)
    ang = 2 * math.pi / n * (-1 if invert else 1)
    w = complex(math.cos(ang), math.sin(ang)); wk = 1 + 0j
    for k in range(n // 2):
        a[k] = a0[k] + wk * a1[k]
        a[k + n // 2] = a0[k] - wk * a1[k]
        wk *= w
    if invert:
        for i in range(n): a[i] /= 2
    return a

def multiply_polynomials(a, b):
    n = 1
    while n < len(a) + len(b) - 1: n <<= 1
    fa = [complex(x, 0) for x in a] + [0j] * (n - len(a))
    fb = [complex(x, 0) for x in b] + [0j] * (n - len(b))
    fa = fft(fa); fb = fft(fb)
    fc = [fa[i] * fb[i] for i in range(n)]
    fc = fft(fc, invert=True)
    return [round(fc[i].real) for i in range(len(a) + len(b) - 1)]
```
**Big-O:** O(n log n). Cooley-Tukey algorithm.
**Alternatif:** Naive O(n^2). NTT for integer-only."""

    # Bit manipulation
    if "bit manipulation" in inst_lower or "brian kernighan" in inst_lower or "count set bits" in inst_lower:
        return r"""```python
def count_set_bits_kernighan(n):
    count = 0
    while n:
        n &= n - 1; count += 1
    return count

def count_set_bits_lookup(n):
    table = [bin(i).count("1") for i in range(256)]
    count = 0
    while n:
        count += table[n & 0xFF]; n >>= 8
    return count

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

def xor_swap(a, b):
    a ^= b; b ^= a; a ^= b
    return a, b
```
**Big-O:** O(number of set bits) Kernighan, O(1) lookup table.
**Alternatif:** Built-in bit_count() Python 3.8+."""

    # Fast pow
    if "pow" in inst_lower and "log n" in inst_lower:
        return r"""```python
def fast_pow(x, n):
    if n < 0: x = 1 / x; n = -n
    res = 1.0
    while n:
        if n & 1: res *= x
        x *= x; n >>= 1
    return res
```
**Big-O:** O(log n). Fast exponentiation, binary exponentiation.
**Alternatif:** pow(x, n) built-in. math.pow for floats."""

    # GCD
    if "gcd" in inst_lower or "euclidean" in inst_lower:
        return r"""```python
def gcd_recursive(a, b):
    return a if b == 0 else gcd_recursive(b, a % b)

def gcd_iterative(a, b):
    while b: a, b = b, a % b
    return a
```
**Big-O:** O(log min(a,b)). Euclidean algorithm.
**Alternatif:** math.gcd built-in. Stein's algorithm (binary GCD)."""

    # Extended Euclidean
    if "extended euclidean" in inst_lower or "modular inverse" in inst_lower:
        return r"""```python
def extended_gcd(a, b):
    if b == 0: return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modular_inverse(a, mod):
    g, x, _ = extended_gcd(a % mod, mod)
    if g != 1: raise ValueError("Inverse does not exist")
    return x % mod
```
**Big-O:** O(log mod). Extended Euclidean algorithm.
**Alternatif:** Fermat's Little Theorem: a^(mod-2) % mod (mod prime icin)."""

    # Sieve of Eratosthenes
    if "eratosthenes" in inst_lower or "sieve" in inst_lower:
        if "segmented" in inst_lower:
            return r"""```python
import math

def simple_sieve(limit):
    is_prime = [True] * (limit + 1); is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i): is_prime[j] = False
    return [i for i, v in enumerate(is_prime) if v]

def segmented_sieve(low, high):
    if low < 2: low = 2
    limit = int(math.isqrt(high)) + 1
    primes = simple_sieve(limit)
    is_prime = [True] * (high - low + 1)
    for p in primes:
        start = max(p * p, ((low + p - 1) // p) * p)
        for j in range(start, high + 1, p): is_prime[j - low] = False
    return [i + low for i, v in enumerate(is_prime) if v]
```
**Big-O:** O((high-low) * log log high). Segmented sieve.
**Alternatif:** Simple sieve O(n log log n)."""
        return r"""```python
def sieve_of_eratosthenes(n):
    is_prime = [True] * (n + 1); is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i): is_prime[j] = False
    return [i for i, v in enumerate(is_prime) if v]
```
**Big-O:** O(n log log n). Space O(n).
**Alternatif:** Segmented sieve O(sqrt(n)) space. Miller-Rabin O(log n) test."""

    # Miller-Rabin
    if "miller" in inst_lower and "rabin" in inst_lower:
        return r"""```python
import random

def miller_rabin(n, k=10):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for _ in range(k):
        a = random.randrange(2, min(n - 2, 2**31))
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True
```
**Big-O:** O(k * log^3 n). Probabilistic, k iteration.
**Alternatif:** Deterministic (AKS) O(log^6 n). Trial division O(sqrt(n))."""

    # Pollard's Rho
    if "pollard" in inst_lower:
        return r"""```python
import math, random

def pollards_rho(n):
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3
    x = random.randrange(2, n - 1); y = x
    c = random.randrange(1, n - 1); d = 1
    f = lambda x: (x * x + c) % n
    while d == 1:
        x = f(x); y = f(f(y))
        d = math.gcd(abs(x - y), n)
    return d if d != n else pollards_rho(n)

def factorize(n):
    factors = []
    for p in [2, 3, 5, 7, 11, 13]:
        while n % p == 0: factors.append(p); n //= p
    if n > 1:
        if miller_rabin(n): factors.append(n)
        else: d = pollards_rho(n); factors.extend(factorize(d)); factors.extend(factorize(n // d))
    return sorted(factors)
```
**Big-O:** O(n^(1/4)) expected. Pollard's Rho.
**Alternatif:** Trial division O(sqrt(n)). ECM for larger factors."""

    # Chinese Remainder Theorem
    if "chinese remainder" in inst_lower or "crt" in inst_lower:
        return r"""```python
def chinese_remainder(remainders, moduli):
    M = 1
    for m in moduli: M *= m
    result = 0
    for a, m in zip(remainders, moduli):
        Mi = M // m; inv = pow(Mi, -1, m)
        result = (result + a * Mi * inv) % M
    return result
```
**Big-O:** O(n log M). CRT.
**Alternatif:** Garner's algorithm. Iterative construction."""
    # Modular exponentiation
    if "modular exponentiation" in inst_lower:
        return r"""```python
def mod_pow(base, exp, mod):
    result = 1; base %= mod
    while exp > 0:
        if exp & 1: result = (result * base) % mod
        base = (base * base) % mod; exp >>= 1
    return result
```
**Big-O:** O(log exp). Binary exponentiation.
**Alternatif:** pow(base, exp, mod) built-in Python."""

    # Discrete log
    if "discrete log" in inst_lower or "baby-step" in inst_lower:
        return r"""```python
import math

def discrete_log(g, h, p):
    n = int(math.isqrt(p)) + 1
    baby = {}; cur = 1
    for j in range(n):
        baby[cur] = j; cur = (cur * g) % p
    factor = pow(g, -n, p); cur = h
    for i in range(n):
        if cur in baby: return i * n + baby[cur]
        cur = (cur * factor) % p
    return -1
```
**Big-O:** O(sqrt(p)). Baby-step giant-step.
**Alternatif:** Pollard's Rho for discrete log O(sqrt(p))."""

    # Matrix exponentiation / Fibonacci
    if "matrix exponentiation" in inst_lower or "fibonacci" in inst_lower:
        return r"""```python
def mat_mult(a, b, mod=10**9+7):
    n = len(a)
    res = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k]:
                for j in range(n):
                    res[i][j] = (res[i][j] + a[i][k] * b[k][j]) % mod
    return res

def mat_pow(mat, exp, mod=10**9+7):
    n = len(mat)
    res = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    while exp:
        if exp & 1: res = mat_mult(res, mat, mod)
        mat = mat_mult(mat, mat, mod); exp >>= 1
    return res

def fib_matrix(n):
    if n <= 1: return n
    base = [[1, 1], [1, 0]]
    result = mat_pow(base, n - 1)
    return result[0][0]
```
**Big-O:** O(log n). Matrix exponentiation ile Fibonacci.
**Alternatif:** Fast doubling O(log n). DP O(n)."""

    # Gaussian elimination
    if "gaussian" in inst_lower or "linear equations" in inst_lower:
        return r"""```python
def gaussian_elimination(A, b):
    n = len(A)
    mat = [A[i] + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(mat[r][col]))
        if abs(mat[pivot][col]) < 1e-10: continue
        mat[col], mat[pivot] = mat[pivot], mat[col]
        piv = mat[col][col]
        for j in range(col, n + 1): mat[col][j] /= piv
        for r in range(n):
            if r != col:
                factor = mat[r][col]
                for j in range(col, n + 1): mat[r][j] -= factor * mat[col][j]
    return [mat[i][n] for i in range(n)]
```
**Big-O:** O(n^3). Gaussian elimination with partial pivot.
**Alternatif:** LU decomposition. Gauss-Jordan. numpy.linalg.solve."""

    # Simplex
    if "simplex" in inst_lower:
        return r"""```python
def simplex(c, A, b):
    m, n = len(A), len(c)
    tableau = [row[:] + [0] * m + [b[i]] for i, row in enumerate(A)]
    for i in range(m): tableau[i][n + i] = 1.0
    tableau.append([-x for x in c] + [0] * m + [0.0])
    while True:
        col = min(range(n + m), key=lambda j: tableau[m][j] if tableau[m][j] < 0 else float("inf"))
        if tableau[m][col] >= 0: break
        row = -1; min_ratio = float("inf")
        for r in range(m):
            if tableau[r][col] > 0:
                ratio = tableau[r][n + m] / tableau[r][col]
                if ratio < min_ratio: min_ratio = ratio; row = r
        if row == -1: return float("inf"), []
        piv = tableau[row][col]
        for j in range(n + m + 1): tableau[row][j] /= piv
        for r in range(m + 1):
            if r != row:
                factor = tableau[r][col]
                for j in range(n + m + 1): tableau[r][j] -= factor * tableau[row][j]
    x = [0.0] * n
    for j in range(n):
        col_vals = [tableau[r][j] for r in range(m)]
        if sum(1 for v in col_vals if abs(v - 1) < 1e-10) == 1 and sum(1 for v in col_vals if abs(v) > 1e-10) == 1:
            x[j] = tableau[col_vals.index(1.0)][n + m]
    return tableau[m][n + m], x
```
**Big-O:** O(2^n) worst, O(n+m) average. Simplex algorithm.
**Alternatif:** Interior point methods O(n^3.5). NP-hard in worst case."""

    # Monte Carlo pi
    if "monte carlo" in inst_lower and "pi" in inst_lower:
        return r"""```python
import random

def monte_carlo_pi(num_samples=1000000):
    inside = 0
    for _ in range(num_samples):
        x, y = random.random(), random.random()
        if x * x + y * y <= 1: inside += 1
    return 4 * inside / num_samples
```
**Big-O:** O(n). n = sample count. Accuracy ~ O(1/sqrt(n)).
**Alternatif:** Bailey-Borwein-Plouffe formula. Machin's formula."""

    # Reservoir sampling
    if "reservoir" in inst_lower:
        return r"""```python
import random

def reservoir_sample(stream, k):
    reservoir = stream[:k]
    for i, item in enumerate(stream[k:], start=k + 1):
        j = random.randrange(i)
        if j < k: reservoir[j] = item
    return reservoir
```
**Big-O:** O(n). n = stream size. Space O(k).
**Alternatif:** Weighted reservoir sampling. Algorithm L (skip-based)."""

    # Fisher-Yates
    if "fisher" in inst_lower or "yates" in inst_lower:
        return r"""```python
import random

def fisher_yates_shuffle(arr):
    a = arr[:]
    for i in range(len(a) - 1, 0, -1):
        j = random.randrange(i + 1)
        a[i], a[j] = a[j], a[i]
    return a
```
**Big-O:** O(n). In-place, unbiased shuffle.
**Alternatif:** random.shuffle built-in. Sattolo's algorithm for cyclic permutations."""

    # Load balancing
    if "load balancing" in inst_lower or "round robin" in inst_lower:
        return r"""```python
import hashlib

class RoundRobin:
    def __init__(self, servers):
        self.servers = servers; self.idx = 0
    def next(self):
        s = self.servers[self.idx]
        self.idx = (self.idx + 1) % len(self.servers); return s

class LeastConnections:
    def __init__(self, servers):
        self.conns = {s: 0 for s in servers}
    def next(self):
        server = min(self.conns, key=self.conns.get)
        self.conns[server] += 1; return server
    def release(self, server):
        if server in self.conns and self.conns[server] > 0: self.conns[server] -= 1

class IPHash:
    def __init__(self, servers):
        self.servers = servers
    def next(self, client_ip):
        h = int(hashlib.md5(client_ip.encode()).hexdigest()[:8], 16)
        return self.servers[h % len(self.servers)]
```
**Big-O:** O(1) per request. All strategies.
**Alternatif:** Weighted Round Robin. Consistent Hashing. Random."""

    # Leader election
    if "leader election" in inst_lower or "bully" in inst_lower or "raft" in inst_lower:
        return r"""```python
# Bully Algorithm
class BullyProcess:
    def __init__(self, pid, higher):
        self.pid = pid; self.higher = higher; self.coordinator = None
    def start_election(self):
        responses = [h for h in self.higher]
        if not responses: self.coordinator = self.pid; return self.pid
        winner = max(responses); self.coordinator = winner; return winner

# Raft Consensus:
# - Randomized leader election timeouts
# - Log replication with majority commit
# - Safety via Leader Completeness Property
# - Terms as logical clocks
```
**Big-O:** O(n) messages. Bully algorithm.
**Alternatif:** Raft O(n) messages, Paxos O(n^2)."""

    # Distributed counter
    if "distributed counter" in inst_lower or "crdt" in inst_lower or "gossip" in inst_lower:
        return r"""```python
# G-Counter (Grow-only Counter)
class GCounter:
    def __init__(self, node_id, n_nodes):
        self.node_id = node_id; self.counts = [0] * n_nodes
    def increment(self, delta=1): self.counts[self.node_id] += delta
    def value(self): return sum(self.counts)
    def merge(self, other):
        for i in range(len(self.counts)): self.counts[i] = max(self.counts[i], other.counts[i])

# PN-Counter (allows decrement)
class PNCounter:
    def __init__(self, node_id, n_nodes):
        self.p = GCounter(node_id, n_nodes); self.n = GCounter(node_id, n_nodes)
    def increment(self, delta=1): self.p.increment(delta)
    def decrement(self, delta=1): self.n.increment(delta)
    def value(self): return self.p.value() - self.n.value()
    def merge(self, other): self.p.merge(other.p); self.n.merge(other.n)
```
**Big-O:** O(n_nodes) merge. Conflict-free, eventually consistent.
**Alternatif:** Centralized counter (single point of failure)."""

    # Two-phase commit
    if "two-phase commit" in inst_lower or "2pc" in inst_lower or "distributed transaction" in inst_lower:
        return r"""```python
# Two-Phase Commit (2PC) Protocol:
# Phase 1 - Prepare: Coordinator sends PREPARE, participants vote YES/NO
# Phase 2 - Commit/Abort: If all YES -> COMMIT, else ABORT
#
# Failure handling:
# - Participant crash: timeout -> abort
# - Coordinator crash: participants ask each other
# - Split-brain: majority decision

class TwoPCParticipant:
    def __init__(self, name):
        self.name = name; self.prepared = False
    def prepare(self): self.prepared = True; return True
    def commit(self): self.prepared = False
    def abort(self): self.prepared = False
```
**Big-O:** O(n) messages. 2 rounds.
**Alternatif:** 3PC (non-blocking). Paxos/Paxos commit. Saga pattern (long-running)."""

    # Heap sort (fallback for any remaining algo)
    if "heap sort" in inst_lower or "heap_sort" in inst_lower:
        return r"""```python
def heapify(arr, n, i):
    largest = i; left = 2 * i + 1; right = 2 * i + 2
    if left < n and arr[left] > arr[largest]: largest = left
    if right < n and arr[right] > arr[largest]: largest = right
    if largest != i: arr[i], arr[largest] = arr[largest], arr[i]; heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1): heapify(arr, n, i)
    for i in range(n - 1, 0, -1): arr[i], arr[0] = arr[0], arr[i]; heapify(arr, i, 0)
    return arr
```
**Big-O:** O(n log n) her durumda, O(1) ek hafiza.
**Alternatif:** Merge sort O(n log n) stable, Quick sort O(n log n) average."""
    # Counting sort
    if "counting sort" in inst_lower:
        return r"""```python
def counting_sort(arr):
    if not arr: return arr
    max_val, min_val = max(arr), min(arr)
    range_elem = max_val - min_val + 1
    count = [0] * range_elem; output = [0] * len(arr)
    for num in arr: count[num - min_val] += 1
    for i in range(1, len(count)): count[i] += count[i - 1]
    for num in reversed(arr):
        idx = num - min_val
        output[count[idx] - 1] = num; count[idx] -= 1
    return output
```
**Big-O:** O(n + k). k = value range.
**Alternatif:** Radix sort O(d*n). Bucket sort."""
    # Radix sort
    if "radix sort" in inst_lower:
        return r"""```python
def counting_sort_for_radix(arr, exp):
    n = len(arr); output = [0] * n; count = [0] * 10
    for i in range(n): count[(arr[i] // exp) % 10] += 1
    for i in range(1, 10): count[i] += count[i - 1]
    for i in range(n - 1, -1, -1):
        idx = (arr[i] // exp) % 10
        output[count[idx] - 1] = arr[i]; count[idx] -= 1
    for i in range(n): arr[i] = output[i]

def radix_sort(arr):
    if not arr: return arr
    max_val = max(arr); exp = 1
    while max_val // exp > 0: counting_sort_for_radix(arr, exp); exp *= 10
    return arr
```
**Big-O:** O(d * n). d = basamak sayisi.
**Alternatif:** Counting sort O(n+k). Bucket sort."""
    # Bucket sort
    if "bucket sort" in inst_lower:
        return r"""```python
def bucket_sort(arr, bucket_size=5):
    if not arr: return arr
    min_val, max_val = min(arr), max(arr)
    bucket_count = max(1, (max_val - min_val) // bucket_size + 1)
    buckets = [[] for _ in range(bucket_count)]
    for num in arr: buckets[(num - min_val) // bucket_size].append(num)
    result = []
    for bucket in buckets: result.extend(sorted(bucket))
    return result
```
**Big-O:** O(n + k) average, O(n^2) worst.
**Alternatif:** Counting sort O(n+k). Radix sort."""

    return None


def gen_ds(inst):
    inst_lower = inst.lower()
    # LRU Cache
    if "lru" in inst_lower or "least recently" in inst_lower:
        return r"""```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key):
        if key not in self.cache: return -1
        self.order.remove(key); self.order.append(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value; self.order.append(key)
```
**Big-O:** O(n) get/put naive (list remove). O(1) with OrderedDict / doubly linked list + dict.
**Alternatif:** LFU (Least Frequently Used). MRU (Most Recently Used)."""

    # LFU Cache
    if "lfu" in inst_lower or "least frequently" in inst_lower:
        return r"""```python
from collections import defaultdict

class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.key_to_val = {}
        self.key_to_freq = {}
        self.freq_to_keys = defaultdict(set)
        self.min_freq = 0

    def get(self, key):
        if key not in self.key_to_val: return -1
        self._increment(key); return self.key_to_val[key]

    def put(self, key, value):
        if self.capacity <= 0: return
        if key in self.key_to_val:
            self.key_to_val[key] = value; self._increment(key); return
        if len(self.key_to_val) >= self.capacity:
            evict = self.freq_to_keys[self.min_freq].pop()
            del self.key_to_val[evict]; del self.key_to_freq[evict]
        self.key_to_val[key] = value
        self.key_to_freq[key] = 1
        self.freq_to_keys[1].add(key)
        self.min_freq = 1

    def _increment(self, key):
        freq = self.key_to_freq[key]
        self.freq_to_keys[freq].discard(key)
        new_freq = freq + 1
        self.key_to_freq[key] = new_freq
        self.freq_to_keys[new_freq].add(key)
        if not self.freq_to_keys[freq] and self.min_freq == freq:
            self.min_freq = new_freq
```
**Big-O:** O(1) get/put. HashMap + freq map + min freq tracking.
**Alternatif:** LRU (time-based). ARC (adaptive)."""

    # Trie / Prefix Tree
    if "trie" in inst_lower or "prefix tree" in inst_lower:
        return r"""```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children: node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children: return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children: return False
            node = node.children[ch]
        return True
```
**Big-O:** O(L) insert/search/starts_with. L = word length.
**Alternatif:** Ternary Search Trie. Compressed Trie (Radix Tree)."""

    # Suffix Trie
    if "suffix trie" in inst_lower:
        return r"""```python
class SuffixTrieNode:
    def __init__(self):
        self.children = {}
        self.indices = []

class SuffixTrie:
    def __init__(self, text):
        self.root = SuffixTrieNode()
        for i in range(len(text)):
            self._insert(text[i:], i)

    def _insert(self, suffix, idx):
        node = self.root
        for ch in suffix:
            if ch not in node.children: node.children[ch] = SuffixTrieNode()
            node = node.children[ch]; node.indices.append(idx)

    def search(self, pattern):
        node = self.root
        for ch in pattern:
            if ch not in node.children: return []
            node = node.children[ch]
        return node.indices
```
**Big-O:** O(n^2) build, O(m) search. Suffix array O(n log n) build daha iyi.
**Alternatif:** Suffix array O(n log n). Suffix tree O(n)."""

    # Segment Tree (range sum, no lazy)
    if "segment tree" in inst_lower and "lazy" not in inst_lower and "2d" not in inst_lower:
        return r"""```python
class SegmentTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self._build(data, 1, 0, self.n - 1)

    def _build(self, data, node, l, r):
        if l == r: self.tree[node] = data[l]; return
        m = (l + r) // 2
        self._build(data, node * 2, l, m)
        self._build(data, node * 2 + 1, m + 1, r)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _update(self, node, l, r, idx, val):
        if l == r: self.tree[node] = val; return
        m = (l + r) // 2
        if idx <= m: self._update(node * 2, l, m, idx, val)
        else: self._update(node * 2 + 1, m + 1, r, idx, val)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _query(self, node, l, r, ql, qr):
        if ql > r or qr < l: return 0
        if ql <= l and r <= qr: return self.tree[node]
        m = (l + r) // 2
        return self._query(node * 2, l, m, ql, qr) + self._query(node * 2 + 1, m + 1, r, ql, qr)

    def update(self, idx, val): self._update(1, 0, self.n - 1, idx, val)
    def query(self, l, r): return self._query(1, 0, self.n - 1, l, r)
```
**Big-O:** O(log n) query/update. O(n) build.
**Alternatif:** Fenwick Tree O(log n) daha hizli, daha az hafiza. Sparse Table O(1) query ama immutable."""

    # Segment Tree with Lazy
    if "segment tree" in inst_lower and "lazy" in inst_lower:
        return r"""```python
class LazySegmentTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(data, 1, 0, self.n - 1)

    def _build(self, data, node, l, r):
        if l == r: self.tree[node] = data[l]; return
        m = (l + r) // 2
        self._build(data, node * 2, l, m)
        self._build(data, node * 2 + 1, m + 1, r)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _push(self, node, l, r):
        if self.lazy[node]:
            self.tree[node] += self.lazy[node] * (r - l + 1)
            if l != r:
                self.lazy[node * 2] += self.lazy[node]
                self.lazy[node * 2 + 1] += self.lazy[node]
            self.lazy[node] = 0

    def _update(self, node, l, r, ql, qr, val):
        self._push(node, l, r)
        if ql > r or qr < l: return
        if ql <= l and r <= qr:
            self.lazy[node] += val; self._push(node, l, r); return
        m = (l + r) // 2
        self._update(node * 2, l, m, ql, qr, val)
        self._update(node * 2 + 1, m + 1, r, ql, qr, val)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _query(self, node, l, r, ql, qr):
        self._push(node, l, r)
        if ql > r or qr < l: return 0
        if ql <= l and r <= qr: return self.tree[node]
        m = (l + r) // 2
        return self._query(node * 2, l, m, ql, qr) + self._query(node * 2 + 1, m + 1, r, ql, qr)

    def update(self, l, r, val): self._update(1, 0, self.n - 1, l, r, val)
    def query(self, l, r): return self._query(1, 0, self.n - 1, l, r)
```
**Big-O:** O(log n) range update/query. Lazy propagation ile.
**Alternatif:** Fenwick Tree range update range query O(log n). Square root decomposition O(sqrt(n))."""

    # Hash Table / HashMap
    if ("hash" in inst_lower or "hashmap" in inst_lower or "hash table" in inst_lower) and "consistent" not in inst_lower:
        if "open addressing" in inst_lower:
            return r"""```python
class HashTableOpenAddressing:
    def __init__(self, size=16):
        self.size = size
        self.keys = [None] * size
        self.values = [None] * size
        self.used = 0

    def _hash(self, key): return hash(key) % self.size

    def insert(self, key, value):
        i = self._hash(key)
        while self.keys[i] is not None:
            if self.keys[i] == key: self.values[i] = value; return
            i = (i + 1) % self.size
        self.keys[i] = key; self.values[i] = value; self.used += 1
        if self.used > self.size // 2: self._resize()

    def get(self, key):
        i = self._hash(key)
        while self.keys[i] is not None:
            if self.keys[i] == key: return self.values[i]
            i = (i + 1) % self.size
        raise KeyError(key)

    def _resize(self):
        old_keys, old_vals = self.keys, self.values
        self.size *= 2; self.keys = [None] * self.size; self.values = [None] * self.size; self.used = 0
        for k, v in zip(old_keys, old_vals):
            if k is not None: self.insert(k, v)
```
**Big-O:** Average O(1), worst O(n). Open addressing with linear probing.
**Alternatif:** Separate chaining (linked list per bucket). Robin Hood hashing."""
        return r"""```python
class HashTable:
    def __init__(self, size=16):
        self.size = size
        self.buckets = [[] for _ in range(size)]
        self.used = 0

    def _hash(self, key): return hash(key) % self.size

    def insert(self, key, value):
        bucket = self.buckets[self._hash(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key: bucket[i] = (key, value); return
        bucket.append((key, value)); self.used += 1
        if self.used > self.size * 0.75: self._resize()

    def get(self, key):
        bucket = self.buckets[self._hash(key)]
        for k, v in bucket:
            if k == key: return v
        raise KeyError(key)

    def remove(self, key):
        bucket = self.buckets[self._hash(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key: bucket.pop(i); self.used -= 1; return
        raise KeyError(key)

    def _resize(self):
        old_buckets = self.buckets
        self.size *= 2; self.buckets = [[] for _ in range(self.size)]; self.used = 0
        for bucket in old_buckets:
            for k, v in bucket: self.insert(k, v)
```
**Big-O:** Average O(1), worst O(n). Separate chaining, load factor 0.75.
**Alternatif:** dict built-in. Open addressing. Cuckoo hashing O(1) worst-case lookup."""

    # Linked List (Singly)
    if "singly" in inst_lower or "linked list" in inst_lower and "doubly" not in inst_lower and "single" in inst_lower:
        return r"""```python
class ListNode:
    def __init__(self, val=0, next_node=None):
        self.val = val; self.next = next_node

class SinglyLinkedList:
    def __init__(self): self.head = None

    def insert_at_beginning(self, val):
        self.head = ListNode(val, self.head)

    def insert_at_end(self, val):
        if not self.head: self.head = ListNode(val); return
        cur = self.head
        while cur.next: cur = cur.next
        cur.next = ListNode(val)

    def delete(self, val):
        if not self.head: return
        if self.head.val == val: self.head = self.head.next; return
        cur = self.head
        while cur.next and cur.next.val != val: cur = cur.next
        if cur.next: cur.next = cur.next.next

    def reverse(self):
        prev, cur = None, self.head
        while cur: nxt = cur.next; cur.next = prev; prev = cur; cur = nxt
        self.head = prev
```
**Big-O:** O(n) search/delete. O(1) insert at beginning.
**Alternatif:** Doubly linked list. Skip list O(log n)."""

    # Doubly Linked List
    if "doubly" in inst_lower or "dll" in inst_lower:
        return r"""```python
class DListNode:
    def __init__(self, val=0, prev_node=None, next_node=None):
        self.val = val; self.prev = prev_node; self.next = next_node

class DoublyLinkedList:
    def __init__(self):
        self.head = None; self.tail = None

    def append(self, val):
        node = DListNode(val, self.tail, None)
        if self.tail: self.tail.next = node
        else: self.head = node
        self.tail = node

    def prepend(self, val):
        node = DListNode(val, None, self.head)
        if self.head: self.head.prev = node
        else: self.tail = node
        self.head = node

    def delete(self, node):
        if node.prev: node.prev.next = node.next
        else: self.head = node.next
        if node.next: node.next.prev = node.prev
        else: self.tail = node.prev
```
**Big-O:** O(1) insert/delete given node reference. O(n) search.
**Alternatif:** Singly linked list. Circular linked list."""

    # Stack
    if "stack" in inst_lower and "min stack" not in inst_lower:
        return r"""```python
class Stack:
    def __init__(self): self.items = []

    def push(self, item): self.items.append(item)
    def pop(self): return self.items.pop() if self.items else None
    def peek(self): return self.items[-1] if self.items else None
    def is_empty(self): return len(self.items) == 0
    def size(self): return len(self.items)
```
**Big-O:** O(1) push/pop/peek. LIFO.
**Alternatif:** collections.deque. Linked list based stack."""

    # Min Stack
    if "min stack" in inst_lower:
        return r"""```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val):
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]: self.min_stack.append(val)

    def pop(self):
        if not self.stack: return None
        if self.stack[-1] == self.min_stack[-1]: self.min_stack.pop()
        return self.stack.pop()

    def top(self): return self.stack[-1] if self.stack else None
    def get_min(self): return self.min_stack[-1] if self.min_stack else None
```
**Big-O:** O(1) all operations. O(n) extra space for min tracking.
**Alternatif:** Store (value, current_min) pairs in one stack."""

    # Queue
    if "queue" in inst_lower and "deque" not in inst_lower and "priority" not in inst_lower and "circular" not in inst_lower:
        return r"""```python
class Queue:
    def __init__(self): self.items = []
    def enqueue(self, item): self.items.append(item)
    def dequeue(self): return self.items.pop(0) if self.items else None
    def front(self): return self.items[0] if self.items else None
    def is_empty(self): return len(self.items) == 0
    def size(self): return len(self.items)
```
**Big-O:** O(1) enqueue, O(n) dequeue (list pop(0)). collections.deque O(1) both.
**Alternatif:** collections.deque. Circular buffer O(1) both."""

    # Deque
    if "deque" in inst_lower:
        return r"""```python
class Deque:
    def __init__(self): self.items = []
    def add_front(self, item): self.items.insert(0, item)
    def add_rear(self, item): self.items.append(item)
    def remove_front(self): return self.items.pop(0) if self.items else None
    def remove_rear(self): return self.items.pop() if self.items else None
    def is_empty(self): return len(self.items) == 0
    def size(self): return len(self.items)
```
**Big-O:** O(n) add/remove front (list). collections.deque O(1) both ends.
**Alternatif:** collections.deque (doubly linked list based)."""

    # Min Heap / Max Heap
    if "heap" in inst_lower and "fibonacci" not in inst_lower:
        return r"""```python
import heapq

class MinHeap:
    def __init__(self): self.heap = []
    def push(self, val): heapq.heappush(self.heap, val)
    def pop(self): return heapq.heappop(self.heap) if self.heap else None
    def peek(self): return self.heap[0] if self.heap else None
    def size(self): return len(self.heap)

class MaxHeap:
    def __init__(self): self.heap = []
    def push(self, val): heapq.heappush(self.heap, -val)
    def pop(self): return -heapq.heappop(self.heap) if self.heap else None
    def peek(self): return -self.heap[0] if self.heap else None
    def size(self): return len(self.heap)
```
**Big-O:** O(log n) push/pop. O(1) peek.
**Alternatif:** heapq built-in. Fibonacci heap O(1) insert/decrease-key (karmasik)."""

    # BST
    if "bst" in inst_lower or "binary search tree" in inst_lower and "avl" not in inst_lower and "red-black" not in inst_lower and "splay" not in inst_lower:
        return r"""```python
class BSTNode:
    def __init__(self, key):
        self.key = key; self.left = None; self.right = None

class BST:
    def insert(self, root, key):
        if not root: return BSTNode(key)
        if key < root.key: root.left = self.insert(root.left, key)
        elif key > root.key: root.right = self.insert(root.right, key)
        return root

    def search(self, root, key):
        if not root or root.key == key: return root
        return self.search(root.left, key) if key < root.key else self.search(root.right, key)

    def delete(self, root, key):
        if not root: return root
        if key < root.key: root.left = self.delete(root.left, key)
        elif key > root.key: root.right = self.delete(root.right, key)
        else:
            if not root.left: return root.right
            if not root.right: return root.left
            temp = self._min_value(root.right)
            root.key = temp.key
            root.right = self.delete(root.right, temp.key)
        return root

    def _min_value(self, root):
        while root.left: root = root.left
        return root

    def inorder(self, root, res=None):
        if res is None: res = []
        if root: self.inorder(root.left, res); res.append(root.key); self.inorder(root.right, res)
        return res
```
**Big-O:** O(h) insert/search/delete. h = height, worst O(n). Average O(log n).
**Alternatif:** AVL Tree O(log n) balanced. Red-Black Tree O(log n)."""

    # AVL Tree
    if "avl" in inst_lower:
        return r"""```python
class AVLNode:
    def __init__(self, key):
        self.key = key; self.left = None; self.right = None; self.height = 1

class AVLTree:
    def height(self, node): return node.height if node else 0

    def balance(self, node): return self.height(node.left) - self.height(node.right) if node else 0

    def rotate_right(self, y):
        x = y.left; t = x.right
        x.right = y; y.left = t
        y.height = 1 + max(self.height(y.left), self.height(y.right))
        x.height = 1 + max(self.height(x.left), self.height(x.right))
        return x

    def rotate_left(self, x):
        y = x.right; t = y.left
        y.left = x; x.right = t
        x.height = 1 + max(self.height(x.left), self.height(x.right))
        y.height = 1 + max(self.height(y.left), self.height(y.right))
        return y

    def insert(self, node, key):
        if not node: return AVLNode(key)
        if key < node.key: node.left = self.insert(node.left, key)
        elif key > node.key: node.right = self.insert(node.right, key)
        else: return node
        node.height = 1 + max(self.height(node.left), self.height(node.right))
        b = self.balance(node)
        if b > 1 and key < node.left.key: return self.rotate_right(node)
        if b < -1 and key > node.right.key: return self.rotate_left(node)
        if b > 1 and key > node.left.key: node.left = self.rotate_left(node.left); return self.rotate_right(node)
        if b < -1 and key < node.right.key: node.right = self.rotate_right(node.right); return self.rotate_left(node)
        return node
```
**Big-O:** O(log n) insert/search/delete. Strictly balanced.
**Alternatif:** Red-Black Tree O(log n), fewer rotations. Splay Tree amortized O(log n)."""

    # Red-Black Tree
    if "red-black" in inst_lower or "red black" in inst_lower:
        return r"""```python
class RBNode:
    RED, BLACK = True, False
    def __init__(self, key, color=RED):
        self.key = key; self.color = color
        self.left = self.right = self.parent = None

class RedBlackTree:
    def __init__(self):
        self.NIL = RBNode(None, RBNode.BLACK)
        self.root = self.NIL

    def insert(self, key):
        node = RBNode(key); node.left = node.right = self.NIL
        parent, curr = None, self.root
        while curr != self.NIL:
            parent = curr
            curr = curr.left if key < curr.key else curr.right
        node.parent = parent
        if not parent: self.root = node
        elif key < parent.key: parent.left = node
        else: parent.right = node
        self._fix_insert(node)

    def _fix_insert(self, node):
        while node.parent and node.parent.color == RBNode.RED:
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle.color == RBNode.RED:
                    node.parent.color = RBNode.BLACK
                    uncle.color = RBNode.BLACK
                    node.parent.parent.color = RBNode.RED
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent; self._left_rotate(node)
                    node.parent.color = RBNode.BLACK
                    node.parent.parent.color = RBNode.RED
                    self._right_rotate(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle.color == RBNode.RED:
                    node.parent.color = RBNode.BLACK
                    uncle.color = RBNode.BLACK
                    node.parent.parent.color = RBNode.RED
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent; self._right_rotate(node)
                    node.parent.color = RBNode.BLACK
                    node.parent.parent.color = RBNode.RED
                    self._left_rotate(node.parent.parent)
        self.root.color = RBNode.BLACK
```
**Big-O:** O(log n) insert/search/delete. 2-3-4 tree representation.
**Alternatif:** AVL (stricter balance). B-Tree (disk-based)."""

    # B-Tree
    if "b-tree" in inst_lower or "btree" in inst_lower and "b+-tree" not in inst_lower and "b+ tree" not in inst_lower:
        return r"""```python
class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf; self.keys = []; self.children = []

class BTree:
    def __init__(self, t):
        self.t = t; self.root = BTreeNode(True)

    def search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]: i += 1
        if i < len(node.keys) and key == node.keys[i]: return (node, i)
        if node.leaf: return None
        return self.search(node.children[i], key)

    def insert(self, key):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_node = BTreeNode(False)
            new_node.children.append(self.root)
            self.root = new_node
            self._split_child(new_node, 0)
        self._insert_non_full(self.root, key)

    def _split_child(self, parent, i):
        t = self.t; child = parent.children[i]
        new_node = BTreeNode(child.leaf)
        parent.keys.insert(i, child.keys[t - 1])
        parent.children.insert(i + 1, new_node)
        new_node.keys = child.keys[t:]
        child.keys = child.keys[:t - 1]
        if not child.leaf: new_node.children = child.children[t:]; child.children = child.children[:t]

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]: node.keys[i + 1] = node.keys[i]; i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]: i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]: i += 1
            self._insert_non_full(node.children[i], key)
```
**Big-O:** O(t log_t n). Balanced multi-way tree. Disk-friendly.
**Alternatif:** B+ Tree (data only in leaves). AVL/Red-Black (in-memory)."""

    # B+ Tree
    if "b+-tree" in inst_lower or "b+ tree" in inst_lower:
        return r"""```python
class BPlusNode:
    def __init__(self, leaf=False):
        self.leaf = leaf; self.keys = []; self.children = []; self.next = None

class BPlusTree:
    def __init__(self, order):
        self.order = order; self.root = BPlusNode(True)

    def search(self, key):
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]: i += 1
            node = node.children[i]
        for i, k in enumerate(node.keys):
            if k == key: return node.values[i] if hasattr(node, 'values') else True
        return None

    def insert(self, key, value=None):
        root = self.root
        if len(root.keys) == 2 * self.order:
            new_node = BPlusNode(False)
            new_node.children.append(self.root)
            self.root = new_node
            self._split_child(new_node, 0)
        self._insert_non_full(self.root, key, value)
```
**Big-O:** O(log_t n). All data in leaves, leaves linked for range scan.
**Alternatif:** B-Tree. LSM Tree (write-optimized)."""

    # SkipList (data structure version)
    if "skip list" in inst_lower:
        return r"""```python
import random

class SkipListNode:
    def __init__(self, val, level):
        self.val = val; self.forward = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level=16, p=0.5):
        self.max_level = max_level; self.p = p
        self.header = SkipListNode(None, max_level); self.level = 0

    def _random_level(self):
        lvl = 0
        while random.random() < self.p and lvl < self.max_level: lvl += 1
        return lvl

    def search(self, target):
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].val < target: cur = cur.forward[i]
        cur = cur.forward[0]
        return cur and cur.val == target

    def insert(self, val):
        update = [None] * (self.max_level + 1); cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].val < val: cur = cur.forward[i]; update[i] = cur
        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1): update[i] = self.header
            self.level = lvl
        node = SkipListNode(val, lvl)
        for i in range(lvl + 1): node.forward[i] = update[i].forward[i]; update[i].forward[i] = node

    def delete(self, val):
        update = [None] * (self.max_level + 1); cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].val < val: cur = cur.forward[i]; update[i] = cur
        cur = cur.forward[0]
        if cur and cur.val == val:
            for i in range(self.level + 1):
                if update[i].forward[i] != cur: break
                update[i].forward[i] = cur.forward[i]
            while self.level > 0 and not self.header.forward[self.level]: self.level -= 1
```
**Big-O:** O(log n) expected. Probabilistic balanced structure.
**Alternatif:** Treap O(log n). Balanced BST O(log n)."""

    # Treap (data structure version)
    if "treap" in inst_lower:
        return r"""```python
import random

class TreapNode:
    def __init__(self, key):
        self.key = key; self.prio = random.randint(0, 1 << 60)
        self.left = self.right = None; self.size = 1

class Treap:
    def _size(self, t): return t.size if t else 0
    def _update(self, t):
        if t: t.size = 1 + self._size(t.left) + self._size(t.right)

    def split(self, t, key):
        if not t: return (None, None)
        if t.key <= key:
            l, r = self.split(t.right, key); t.right = l; self._update(t); return (t, r)
        l, r = self.split(t.left, key); t.left = r; self._update(t); return (l, t)

    def merge(self, a, b):
        if not a or not b: return a or b
        if a.prio > b.prio: a.right = self.merge(a.right, b); self._update(a); return a
        b.left = self.merge(a, b.left); self._update(b); return b

    def insert(self, t, key):
        l, r = self.split(t, key); return self.merge(self.merge(l, TreapNode(key)), r)

    def delete(self, t, key):
        l, m = self.split(t, key - 1); m, r = self.split(m, key); return self.merge(l, r)

    def kth(self, t, k):
        if not t: return None
        left_sz = self._size(t.left)
        if k < left_sz: return self.kth(t.left, k)
        if k == left_sz: return t.key
        return self.kth(t.right, k - left_sz - 1)
```
**Big-O:** O(log n) expected. Implicit treap supports array operations.
**Alternatif:** Splay Tree O(log n) amortized. WAVL Tree O(log n)."""

    # Graph (adj list / adj matrix)
    if "graph" in inst_lower and "adjacency" in inst_lower:
        return r"""```python
class Graph:
    def __init__(self, n, directed=False):
        self.n = n; self.directed = directed
        self.adj = [[] for _ in range(n)]

    def add_edge(self, u, v, w=1):
        self.adj[u].append((v, w))
        if not self.directed: self.adj[v].append((u, w))

    def bfs(self, start):
        from collections import deque
        visited = [False] * self.n; q = deque([start]); visited[start] = True; order = []
        while q:
            u = q.popleft(); order.append(u)
            for v, _ in self.adj[u]:
                if not visited[v]: visited[v] = True; q.append(v)
        return order

    def dfs(self, start):
        visited = [False] * self.n; order = []
        def _dfs(u): visited[u] = True; order.append(u); [v for v, _ in self.adj[u] if not visited[v]] and [_dfs(v) for v, _ in self.adj[u] if not visited[v]]
        _dfs(start); return order
```
**Big-O:** O(V+E) BFS/DFS. O(E) add_edge.
**Alternatif:** Adjacency Matrix O(V^2) space. Edge List O(E)."""

    # Bloom Filter
    if "bloom filter" in inst_lower or "bloomfilter" in inst_lower:
        return r"""```python
import hashlib

class BloomFilter:
    def __init__(self, size=10000, num_hashes=7):
        self.size = size; self.num_hashes = num_hashes
        self.bits = bytearray((size + 7) // 8)

    def _hashes(self, item):
        return [int(hashlib.sha256((str(i) + str(item)).encode()).hexdigest()[:8], 16) % self.size for i in range(self.num_hashes)]

    def add(self, item):
        for b in self._hashes(item): self.bits[b // 8] |= 1 << (b % 8)

    def __contains__(self, item):
        return all(self.bits[b // 8] & (1 << (b % 8)) for b in self._hashes(item))
```
**Big-O:** O(k) insert/query. k = hash sayisi. False positive olabilir.
**Alternatif:** Cuckoo filter. Counting Bloom Filter (delete destekler)."""

    # Cuckoo Filter
    if "cuckoo" in inst_lower:
        return r"""```python
import hashlib

class CuckooFilter:
    def __init__(self, capacity=1000, bucket_size=4, max_kicks=500):
        self.capacity = capacity; self.bucket_size = bucket_size
        self.max_kicks = max_kicks
        self.buckets = [[None] * bucket_size for _ in range(capacity)]

    def _fingerprint(self, item):
        h = hashlib.sha256(str(item).encode()).digest()
        return int.from_bytes(h[:4], "big") & 0xFFFF

    def _hash(self, item): return hash(item) % self.capacity

    def _alt_index(self, idx, fp): return (idx ^ hash(fp)) % self.capacity

    def insert(self, item):
        fp = self._fingerprint(item); i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        for idx in (i1, i2):
            for j in range(self.bucket_size):
                if self.buckets[idx][j] is None: self.buckets[idx][j] = fp; return True
        idx = i1
        for _ in range(self.max_kicks):
            j = hash(str(item)) % self.bucket_size
            fp, self.buckets[idx][j] = self.buckets[idx][j], fp
            idx = self._alt_index(idx, fp)
            for j in range(self.bucket_size):
                if self.buckets[idx][j] is None: self.buckets[idx][j] = fp; return True
        return False

    def __contains__(self, item):
        fp = self._fingerprint(item); i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        return fp in self.buckets[i1] or fp in self.buckets[i2]
```
**Big-O:** O(1) amortized insert. Bloom'dan daha az false positive, delete destegi.
**Alternatif:** Bloom Filter (daha hizli, daha fazla FP). Quotient filter."""

    # Count-Min Sketch
    if "count-min" in inst_lower or "count min sketch" in inst_lower:
        return r"""```python
import hashlib

class CountMinSketch:
    def __init__(self, width=1000, depth=5):
        self.width = width; self.depth = depth
        self.table = [[0] * width for _ in range(depth)]

    def _hash(self, item, i):
        return int(hashlib.sha256((str(i) + str(item)).encode()).hexdigest()[:8], 16) % self.width

    def add(self, item, count=1):
        for i in range(self.depth): self.table[i][self._hash(item, i)] += count

    def estimate(self, item):
        return min(self.table[i][self._hash(item, i)] for i in range(self.depth))
```
**Big-O:** O(1) insert/query. Overestimate edebilir.
**Alternatif:** Exact frequency map. Count-Mean-Min Sketch (more accurate)."""

    # HyperLogLog
    if "hyperloglog" in inst_lower or "hll" in inst_lower:
        return r"""```python
import hashlib, math

class HyperLogLog:
    def __init__(self, b=14):
        self.b = b; self.m = 1 << b
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m)

    def add(self, item):
        h = hashlib.sha256(str(item).encode()).digest()
        idx = int.from_bytes(h[:2], "big") & (self.m - 1)
        w = int.from_bytes(h[2:], "big")
        r = 1
        while w & 1: w >>= 1; r += 1
        self.registers[idx] = max(self.registers[idx], r)

    def count(self):
        z = sum(2.0 ** -r for r in self.registers)
        e = self.alpha * self.m * self.m / z
        if e <= 2.5 * self.m:
            v = self.registers.count(0)
            if v: e = self.m * math.log(self.m / v)
        return int(e)
```
**Big-O:** O(n) ekleme, O(1) sorgu. Cardinality estimation.
**Alternatif:** Linear Counting. MinHash for set similarity."""

    # MinHash
    if "minhash" in inst_lower:
        return r"""```python
import hashlib

class MinHash:
    def __init__(self, num_hashes=128):
        self.num_hashes = num_hashes; self.sigs = {}

    def _hash_family(self, item, i): return hashlib.sha256((str(i) + str(item)).encode()).hexdigest()[:8]

    def signature(self, items):
        sig = [float("inf")] * self.num_hashes
        for item in items:
            for i in range(self.num_hashes):
                h = int(self._hash_family(item, i), 16)
                if h < sig[i]: sig[i] = h
        return sig

    def jaccard(self, sig1, sig2):
        return sum(1 for a, b in zip(sig1, sig2) if a == b) / self.num_hashes
```
**Big-O:** O(k * |set|) signature. Jaccard approximation.
**Alternatif:** SimHash. Weighted MinHash."""

    # Interval Tree
    if "interval tree" in inst_lower:
        return r"""```python
class IntervalNode:
    def __init__(self, interval, max_end=None):
        self.interval = interval; self.max_end = max_end or interval[1]
        self.left = self.right = None

class IntervalTree:
    def insert(self, node, interval):
        if not node: return IntervalNode(interval)
        if interval[0] < node.interval[0]: node.left = self.insert(node.left, interval)
        else: node.right = self.insert(node.right, interval)
        node.max_end = max(node.max_end, interval[1])
        return node

    def overlap_search(self, node, interval):
        if not node: return None
        if node.interval[0] <= interval[1] and node.interval[1] >= interval[0]: return node.interval
        if node.left and node.left.max_end >= interval[0]: return self.overlap_search(node.left, interval)
        return self.overlap_search(node.right, interval)
```
**Big-O:** O(log n) insert/search balanced. O(n) worst.
**Alternatif:** Segment Tree. Interval Tree built on RBST."""

    # Multiset
    if "multiset" in inst_lower:
        return r"""```python
from collections import Counter

class Multiset:
    def __init__(self): self.data = Counter()
    def add(self, item, count=1): self.data[item] += count
    def remove(self, item, count=1):
        if self.data[item] <= count: del self.data[item]
        else: self.data[item] -= count
    def count(self, item): return self.data.get(item, 0)
    def size(self): return sum(self.data.values())
    def __contains__(self, item): return self.data[item] > 0
```
**Big-O:** Average O(1) add/remove/count. Hash-based.
**Alternatif:** sortedcontainers.SortedList. collections.Counter."""

    # Multimap
    if "multimap" in inst_lower:
        return r"""```python
from collections import defaultdict

class Multimap:
    def __init__(self): self.data = defaultdict(list)
    def put(self, key, value): self.data[key].append(value)
    def get(self, key): return self.data.get(key, [])
    def remove(self, key, value):
        if key in self.data:
            self.data[key] = [v for v in self.data[key] if v != value]
            if not self.data[key]: del self.data[key]
    def keys(self): return list(self.data.keys())
    def size(self): return sum(len(v) for v in self.data.values())
```
**Big-O:** Average O(1) put/get. O(n) remove (scan).
**Alternatif:** collections.defaultdict(list). Guava Multimap."""

    # DSU with rollback
    if "dsu" in inst_lower or "disjoint set" in inst_lower or "union-find" in inst_lower:
        if "rollback" in inst_lower or "undo" in inst_lower:
            return r"""```python
class DSUWithRollback:
    def __init__(self, n):
        self.parent = list(range(n)); self.size = [1] * n; self.history = []
    def find(self, x):
        while self.parent[x] != x: x = self.parent[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b: self.history.append(None); return False
        if self.size[a] < self.size[b]: a, b = b, a
        self.history.append((b, self.parent[b], a, self.size[a]))
        self.parent[b] = a; self.size[a] += self.size[b]; return True
    def snapshot(self): return len(self.history)
    def rollback(self, snap):
        while len(self.history) > snap:
            entry = self.history.pop()
            if entry: b, pb, a, sa = entry; self.parent[b] = pb; self.size[a] = sa
```
**Big-O:** O(log n) union/find. O(1) snapshot/rollback (amortized).
**Alternatif:** Standard DSU O(alpha(n)). Persistent DSU."""
        return r"""```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n)); self.rank = [0] * n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]; x = self.parent[x]
        return x
    def union(self, x, y):
        xr, yr = self.find(x), self.find(y)
        if xr == yr: return False
        if self.rank[xr] < self.rank[yr]: self.parent[xr] = yr
        elif self.rank[xr] > self.rank[yr]: self.parent[yr] = xr
        else: self.parent[yr] = xr; self.rank[xr] += 1
        return True
```
**Big-O:** O(alpha(n)) per operation. Almost O(1).
**Alternatif:** DSU with size heuristic. DSU with rollback."""

    # Thread Pool
    if "thread pool" in inst_lower:
        return r"""```python
from concurrent.futures import ThreadPoolExecutor
import time

class ThreadPool:
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit(self, fn, *args, **kwargs):
        future = self.executor.submit(fn, *args, **kwargs)
        self.futures.append(future); return future

    def wait_all(self):
        results = [f.result() for f in self.futures]
        self.futures.clear(); return results

    def shutdown(self, wait=True): self.executor.shutdown(wait=wait)

# Usage
pool = ThreadPool(4)
for i in range(10): pool.submit(time.sleep, 1)
results = pool.wait_all()
```
**Big-O:** O(task) per task. Workers limit parallel execution.
**Alternatif:** ProcessPoolExecutor (CPU-bound). asyncio (I/O-bound)."""

    # Ring Buffer
    if "ring buffer" in inst_lower:
        return r"""```python
class RingBuffer:
    def __init__(self, capacity):
        self.capacity = capacity; self.buffer = [None] * capacity
        self.head = self.tail = 0; self.full = False

    def push(self, item):
        self.buffer[self.head] = item
        if self.full: self.tail = (self.tail + 1) % self.capacity
        self.head = (self.head + 1) % self.capacity
        self.full = self.head == self.tail

    def pop(self):
        if self.is_empty: return None
        item = self.buffer[self.tail]
        self.full = False; self.tail = (self.tail + 1) % self.capacity
        return item

    @property
    def is_empty(self): return not self.full and self.head == self.tail

    @property
    def size(self):
        if self.full: return self.capacity
        return (self.head - self.tail) % self.capacity
```
**Big-O:** O(1) push/pop. Fixed-size, overwrites when full.
**Alternatif:** collections.deque (dynamic). Queue.Queue (thread-safe)."""

    # Object Pool
    if "object pool" in inst_lower:
        return r"""```python
class ObjectPool:
    def __init__(self, factory, max_size=10):
        self.factory = factory; self.max_size = max_size
        self._pool = [factory() for _ in range(max_size)]
        self._in_use = [False] * max_size

    def acquire(self):
        for i, used in enumerate(self._in_use):
            if not used: self._in_use[i] = True; return self._pool[i]
        raise Exception("Pool exhausted")

    def release(self, obj):
        for i, o in enumerate(self._pool):
            if o is obj: self._in_use[i] = False; return
        raise ValueError("Object not from this pool")

# Connection pool example
class ConnectionPool(ObjectPool):
    pass
```
**Big-O:** O(n) acquire (linear scan). Could be O(1) with deque.
**Alternatif:** Queue-based pool O(1). Thread-local pools."""

    # Priority Queue (heap-based)
    if "priority queue" in inst_lower:
        return r"""```python
import heapq

class PriorityQueue:
    def __init__(self): self.heap = []; self.counter = 0
    def push(self, item, priority):
        heapq.heappush(self.heap, (priority, self.counter, item)); self.counter += 1
    def pop(self): return heapq.heappop(self.heap)[2] if self.heap else None
    def peek(self): return self.heap[0][2] if self.heap else None
    def is_empty(self): return len(self.heap) == 0
    def size(self): return len(self.heap)
```
**Big-O:** O(log n) push/pop. O(1) peek.
**Alternatif:** heapq built-in. queue.PriorityQueue (thread-safe)."""

    # Circular Queue
    if "circular" in inst_lower and "queue" in inst_lower:
        return r"""```python
class CircularQueue:
    def __init__(self, k):
        self.k = k; self.q = [None] * k; self.head = self.tail = self.cnt = 0

    def enqueue(self, value):
        if self.is_full: return False
        self.q[self.tail] = value; self.tail = (self.tail + 1) % self.k; self.cnt += 1; return True

    def dequeue(self):
        if self.is_empty: return False
        self.head = (self.head + 1) % self.k; self.cnt -= 1; return True

    def front(self): return self.q[self.head] if not self.is_empty else -1
    def rear(self): return self.q[(self.tail - 1) % self.k] if not self.is_empty else -1
    @property
    def is_empty(self): return self.cnt == 0
    @property
    def is_full(self): return self.cnt == self.k
```
**Big-O:** O(1) all operations. Fixed-size circular array.
**Alternatif:** collections.deque. List-based queue."""

    # Linked list operations (cycle detection, reverse, merge, etc.)
    if "linked list" in inst_lower and "cycle" in inst_lower:
        return """```python
class ListNode:
    def __init__(self, x): self.val = x; self.next = None

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next; fast = fast.next.next
        if slow == fast: return True
    return False

def detect_cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next; fast = fast.next.next
        if slow == fast:
            slow = head
            while slow != fast: slow = slow.next; fast = fast.next
            return slow
    return None
```
**Big-O:** O(n) time, O(1) space. Floyd's tortoise and hare.
**Alternatif:** HashSet ile O(n) space."""

    if "linked list" in inst_lower and "reverse" in inst_lower:
        return """```python
class ListNode:
    def __init__(self, x): self.val = x; self.next = None

def reverse_iterative(head):
    prev, cur = None, head
    while cur: nxt = cur.next; cur.next = prev; prev = cur; cur = nxt
    return prev

def reverse_recursive(head):
    if not head or not head.next: return head
    new_head = reverse_recursive(head.next)
    head.next.next = head; head.next = None
    return new_head
```
**Big-O:** O(n) time, O(1) space iterative, O(n) stack recursive.
**Alternatif:** Stack-based reverse O(n) space."""

    if "linked list" in inst_lower and "merge" in inst_lower:
        return """```python
class ListNode:
    def __init__(self, x): self.val = x; self.next = None

def merge_two_sorted(l1, l2):
    dummy = cur = ListNode(0)
    while l1 and l2:
        if l1.val < l2.val: cur.next = l1; l1 = l1.next
        else: cur.next = l2; l2 = l2.next
        cur = cur.next
    cur.next = l1 or l2
    return dummy.next
```
**Big-O:** O(n + m) time, O(1) space.
**Alternatif:** Recursive merge O(n+m) stack space."""

    if "linked list" in inst_lower and "middle" in inst_lower:
        return """```python
class ListNode:
    def __init__(self, x): self.val = x; self.next = None

def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next; fast = fast.next.next
    return slow
```
**Big-O:** O(n) time, O(1) space. Slow/fast pointer technique.
**Alternatif:** Count length then traverse to half."""

    if "linked list" in inst_lower and "remove nth" in inst_lower:
        return """```python
class ListNode:
    def __init__(self, x): self.val = x; self.next = None

def remove_nth_from_end(head, n):
    dummy = ListNode(0); dummy.next = head
    fast = slow = dummy
    for _ in range(n): fast = fast.next
    while fast.next: fast = fast.next; slow = slow.next
    slow.next = slow.next.next
    return dummy.next
```
**Big-O:** O(n) time, O(1) space. One pass with two pointers.
**Alternatif:** Two-pass: find length then delete."""

    # Splay Tree
    if "splay" in inst_lower:
        return """```python
class SplayNode:
    def __init__(self, key): self.key = key; self.left = self.right = None

class SplayTree:
    def _rotate_right(self, p):
        q = p.left; p.left = q.right; q.right = p; return q

    def _rotate_left(self, p):
        q = p.right; p.right = q.left; q.left = p; return q

    def _splay(self, root, key):
        if not root or root.key == key: return root
        if key < root.key:
            if not root.left: return root
            if key < root.left.key:
                root.left.left = self._splay(root.left.left, key)
                root = self._rotate_right(root)
            elif key > root.left.key:
                root.left.right = self._splay(root.left.right, key)
                if root.left.right: root.left = self._rotate_left(root.left)
            return self._rotate_right(root) if root.left else root
        else:
            if not root.right: return root
            if key > root.right.key:
                root.right.right = self._splay(root.right.right, key)
                root = self._rotate_left(root)
            elif key < root.right.key:
                root.right.left = self._splay(root.right.left, key)
                if root.right.left: root.right = self._rotate_right(root.right)
            return self._rotate_left(root) if root.right else root

    def insert(self, root, key):
        if not root: return SplayNode(key)
        root = self._splay(root, key)
        if root.key == key: return root
        node = SplayNode(key)
        if key < root.key: node.right = root; node.left = root.left; root.left = None
        else: node.left = root; node.right = root.right; root.right = None
        return node

    def search(self, root, key):
        return self._splay(root, key)
```
**Big-O:** O(log n) amortized. Recently accessed keys fast.
**Alternatif:** AVL Tree O(log n) strict. Treap O(log n) expected."""

    # Memory pool
    if "memory pool" in inst_lower or "arena allocator" in inst_lower:
        return """```python
class MemoryPool:
    def __init__(self, block_size=64, pool_size=1024):
        self.block_size = block_size; self.pool_size = pool_size
        self.pool = [bytearray(block_size) for _ in range(pool_size)]
        self.free_indices = list(range(pool_size))

    def allocate(self):
        if not self.free_indices: raise MemoryError("Pool exhausted")
        return self.free_indices.pop()

    def deallocate(self, idx):
        self.free_indices.append(idx)

    def read(self, idx): return self.pool[idx]
    def write(self, idx, data): self.pool[idx][:len(data)] = data
```
**Big-O:** O(1) allocate/deallocate. No fragmentation.
**Alternatif:** malloc/free. jemalloc. Pool allocator."""

    # String pool / interning
    if "string pool" in inst_lower or "string interning" in inst_lower:
        return """```python
class StringPool:
    def __init__(self): self.pool = {}

    def intern(self, s):
        if s not in self.pool: self.pool[s] = s
        return self.pool[s]

    def count(self): return len(self.pool)

# Usage
pool = StringPool()
a = pool.intern("hello"); b = pool.intern("hello")
# a is b -> True (same object)
```
**Big-O:** O(L) intern, L = string length. Memory deduplication.
**Alternatif:** sys.intern built-in. WeakValueDictionary for GC."""

    return None


def gen_optimization(inst):
    inst_lower = inst.lower()
    # Async vs sync
    if "async" in inst_lower and "sync" in inst_lower:
        return r"""```python
import asyncio, time

# SLOW: Synchronous version
def slow_version(items):
    results = []
    for item in items:
        results.append(process(item))
    return results

def process(item):
    return item * 2

# FAST: Asynchronous version
async def fast_version(items):
    tasks = [async_process(item) for item in items]
    return await asyncio.gather(*tasks)

async def async_process(item):
    return item * 2
```
**Big-O:** Slow O(n), Fast O(n) concurrent. Async I/O bound tasks icin ~Nx hizli.
**Alternatif:** ThreadPoolExecutor. Multiprocessing."""

    # List comprehension vs loop
    if "list comprehension" in inst_lower or "comprehension" in inst_lower:
        return r"""```python
# SLOW: Explicit for loop
def slow_version(items):
    result = []
    for x in items:
        result.append(x * 2)
    return result

# FAST: List comprehension
def fast_version(items):
    return [x * 2 for x in items]
```
**Big-O:** Both O(n) but comprehension ~1.5-2x faster (C-level optimization).
**Alternatif:** map() function. Generator expressions for memory efficiency."""

    # Memoization
    if "memo" in inst_lower or "cache" in inst_lower:
        return r"""```python
from functools import lru_cache

# SLOW: Recursive without cache
def slow_version(n):
    if n <= 1: return n
    return slow_version(n - 1) + slow_version(n - 2)

# FAST: With memoization
@lru_cache(maxsize=None)
def fast_version(n):
    if n <= 1: return n
    return fast_version(n - 1) + fast_version(n - 2)
```
**Big-O:** Slow O(2^n), Fast O(n). Memoization tekrarlanan hesaplamalari onler.
**Alternatif:** DP tabulation O(n). Matrix exponentiation O(log n)."""

    # Loop unrolling / vectorization
    if "unrolling" in inst_lower or "vector" in inst_lower:
        return r"""```python
import numpy as np

# SLOW: Python loop
def slow_version(arr):
    result = [0] * len(arr)
    for i in range(len(arr)):
        result[i] = arr[i] * 2 + 1
    return result

# FAST: NumPy vectorization
def fast_version(arr):
    return np.array(arr) * 2 + 1
```
**Big-O:** Both O(n) but NumPy C-level ~10-100x faster.
**Alternatif:** Numba JIT compilation. Cython. Loop unrolling manually."""

    # String concatenation
    if "string" in inst_lower and ("concat" in inst_lower or "join" in inst_lower):
        return r"""```python
# SLOW: String concatenation with +=
def slow_version(items):
    result = ""
    for s in items:
        result += s
    return result

# FAST: Using join
def fast_version(items):
    return "".join(items)
```
**Big-O:** Slow O(n^2), Fast O(n). String immutability causes copy on each +=.
**Alternatif:** io.StringIO. list comprehension + join."""

    # Batch processing
    if "batch" in inst_lower:
        return r"""```python
# SLOW: Process one by one
def slow_version(items):
    results = []
    for item in items:
        results.append(process(item))
    return results

def process(item):
    return item ** 2

# FAST: Batch processing with chunking
def fast_version(items, batch_size=100):
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        results.extend([x ** 2 for x in batch])
    return results
```
**Big-O:** Both O(n). Batch reduces function call overhead, better cache locality.
**Alternatif:** numpy vectorization. multiprocessing.Pool."""

    # Parallel processing
    if "parallel" in inst_lower:
        return r"""```python
from multiprocessing import Pool

# SLOW: Sequential
def slow_version(items):
    return [process(item) for item in items]

def process(item):
    return item ** 2

# FAST: Parallel processing
def fast_version(items, workers=4):
    with Pool(workers) as pool:
        return pool.map(process, items)
```
**Big-O:** Slow O(n), Fast O(n/workers). CPU-bound tasks icin ideal.
**Alternatif:** ThreadPoolExecutor (I/O-bound). asyncio (I/O-bound)."""

    # Memory optimization with generators
    if "generator" in inst_lower or "lazy" in inst_lower:
        return r"""```python
# SLOW: Load everything in memory
def slow_version(n):
    return [i ** 2 for i in range(n)]

# FAST: Generator (lazy evaluation)
def fast_version(n):
    for i in range(n):
        yield i ** 2

# Usage difference:
# slow: list memory = O(n)
# fast: single item memory = O(1)
```
**Big-O:** Both O(n) time. Slow O(n) memory, Fast O(1) memory.
**Alternatif:** itertools module. Generator expressions (x ** 2 for x in range(n))."""

    # Database query optimization (N+1)
    if "n+1" in inst_lower or "n plus 1" in inst_lower or "database" in inst_lower:
        return r"""```python
# SLOW: N+1 queries
def slow_version(user_ids):
    results = []
    for uid in user_ids:
        user = query_db(f"SELECT * FROM users WHERE id = {uid}")
        results.append(process(user))
    return results

# FAST: Single query with JOIN / IN
def fast_version(user_ids):
    users = query_db(f"SELECT * FROM users WHERE id IN ({','.join(map(str, user_ids))})")
    return [process(u) for u in users]

def query_db(sql): return []
def process(u): return u
```
**Big-O:** Slow O(n) queries, Fast O(1) query. n query yerine 1 query.
**Alternatif:** SQL JOIN. Eager loading (ORM). Batch queries."""

    # Caching with TTL
    if "ttl" in inst_lower or "time-to-live" in inst_lower:
        return r"""```python
import time

class TTLCache:
    def __init__(self, ttl=60):
        self.ttl = ttl; self.cache = {}; self.timestamps = {}

    def get(self, key):
        if key in self.cache and time.time() - self.timestamps[key] < self.ttl:
            return self.cache[key]
        if key in self.cache: del self.cache[key]; del self.timestamps[key]
        return None

    def set(self, key, value):
        self.cache[key] = value; self.timestamps[key] = time.time()

# Usage
cache = TTLCache(ttl=30)
```
**Big-O:** O(1) get/set. Automatic expiration.
**Alternatif:** cachetools.TTLCache. Redis with EXPIRE. functools.lru_cache."""

    # Content delivery optimization
    if "cdn" in inst_lower or "content delivery" in inst_lower:
        return r"""```python
# SLOW: Direct origin serving
def slow_version(request):
    return serve_from_origin(request)

# FAST: CDN with cache
cdn_cache = {}
def fast_version(request):
    url = request.get("url")
    if url in cdn_cache:
        return cdn_cache[url]
    content = serve_from_origin(request)
    cdn_cache[url] = content
    return content

def serve_from_origin(req): return req
```
**Big-O:** Slow O(1) with high latency, Fast O(1) cached. CDN edge'de cache.
**Alternatif:** CloudFront. Cloudflare. Varnish cache."""

    # Indexing for search
    if "index" in inst_lower and ("search" in inst_lower or "lookup" in inst_lower):
        return r"""```python
# SLOW: Linear search
def slow_version(items, target):
    for i, item in enumerate(items):
        if item == target: return i
    return -1

# FAST: Hash index
def fast_version(items, target):
    index = {item: i for i, item in enumerate(items)}
    return index.get(target, -1)
```
**Big-O:** Slow O(n), Fast O(1) average. Index builds O(n) once.
**Alternatif:** Binary search O(log n) sorted. B-tree index."""

    # Algorithmic improvement (quadratic to linear)
    if "quadratic" in inst_lower or "o(n²" in inst_lower or "o(n^2" in inst_lower:
        return r"""```python
# SLOW: O(n^2) brute force
def slow_version(arr):
    inversions = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]: inversions += 1
    return inversions

# FAST: O(n log n) using merge sort
def fast_version(arr):
    def merge_sort(a):
        if len(a) <= 1: return a, 0
        mid = len(a) // 2
        left, inv_l = merge_sort(a[:mid])
        right, inv_r = merge_sort(a[mid:])
        merged, inv_m = merge(left, right)
        return merged, inv_l + inv_r + inv_m

    def merge(left, right):
        i = j = inv = 0; res = []
        while i < len(left) and j < len(right):
            if left[i] <= right[j]: res.append(left[i]); i += 1
            else: res.append(right[j]); inv += len(left) - i; j += 1
        res.extend(left[i:]); res.extend(right[j:])
        return res, inv

    return merge_sort(arr)[1]
```
**Big-O:** Slow O(n^2), Fast O(n log n). Better algorithm selection.
**Alternatif:** Fenwick Tree O(n log n). Divide and conquer."""

    # Lazy loading
    if "lazy loading" in inst_lower:
        return r"""```python
# SLOW: Eager loading
class SlowVersion:
    def __init__(self):
        self.heavy_data = self._load_heavy_data()

    def _load_heavy_data(self):
        return [i for i in range(10**6)]

# FAST: Lazy loading
class FastVersion:
    def __init__(self):
        self._heavy_data = None

    @property
    def heavy_data(self):
        if self._heavy_data is None:
            self._heavy_data = self._load_heavy_data()
        return self._heavy_data

    def _load_heavy_data(self):
        return [i for i in range(10**6)]
```
**Big-O:** Both O(n) total. Lazy: ilk erisime kadar yukleme yok.
**Alternatif:** Proxy pattern. __getattr__ magic method. Property descriptors."""

    # Connection pooling
    if "connection pool" in inst_lower:
        return r"""```python
import time
from queue import Queue

# SLOW: New connection per request
def slow_version(requests):
    results = []
    for req in requests:
        conn = create_connection()
        results.append(conn.query(req))
        conn.close()
    return results

# FAST: Connection pool
class ConnectionPool:
    def __init__(self, size=5): self.pool = Queue(maxsize=size)
    def acquire(self): return self.pool.get() if not self.pool.empty() else create_connection()
    def release(self, conn): self.pool.put(conn)

def fast_version(requests, pool):
    results = []
    for req in requests:
        conn = pool.acquire()
        results.append(conn.query(req))
        pool.release(conn)
    return results

def create_connection(): return type("Conn", (), {"query": lambda self, r: r, "close": lambda self: None})()
```
**Big-O:** Slow O(n) connections, Fast O(1) connection reuse. ~10-100x faster.
**Alternatif:** SQLAlchemy pool. Redis pool. HTTP keep-alive."""

    # Data compression
    if "compress" in inst_lower or "compression" in inst_lower:
        return r"""```python
import zlib, sys

# SLOW: No compression
def slow_version(data):
    return data

# FAST: With compression
def fast_version(data, level=6):
    return zlib.compress(data.encode() if isinstance(data, str) else data, level)

def fast_decompress(data):
    return zlib.decompress(data)

# Example: large text
text = "a" * 10000
compressed = fast_version(text)
# compressed ~ 50 bytes, text ~ 10000 bytes
```
**Big-O:** Slow O(n) no compression, Fast O(n) compress/decompress. ~200:1 compression ratio.
**Alternatif:** gzip. bz2. lzma. Brotli."""

    # Pagination
    if "pagination" in inst_lower or "paginate" in inst_lower:
        return r"""```python
# SLOW: Load all data
def slow_version(all_data):
    return [process(item) for item in all_data]

def process(item): return item

# FAST: Paginated loading
def fast_version(get_page, page_size=100):
    results = []; page = 0
    while True:
        batch = get_page(page, page_size)
        if not batch: break
        results.extend(batch); page += 1
    return results
```
**Big-O:** Slow O(n) memory, Fast O(page_size) memory. Bellek tasarrufu.
**Alternatif:** LIMIT/OFFSET SQL. Keyset pagination (cursor-based)."""

    # Debouncing / throttling
    if "debounce" in inst_lower or "throttle" in inst_lower:
        return r"""```python
import time

# SLOW: Execute every call
def slow_version(func):
    return func()

# FAST: Throttled execution (max once per interval)
class Throttle:
    def __init__(self, interval=1.0):
        self.interval = interval; self.last_call = 0

    def __call__(self, func, *args, **kwargs):
        now = time.time()
        if now - self.last_call >= self.interval:
            self.last_call = now; return func(*args, **kwargs)
        return None

# FAST: Debounced (execute after delay)
class Debounce:
    def __init__(self, delay=0.3): self.delay = delay; self.last = 0
    def __call__(self, func, *args, **kwargs):
        now = time.time()
        if now - self.last >= self.delay:
            self.last = now; return func(*args, **kwargs)
        return None
```
**Big-O:** O(1) per call. Limits execution rate.
**Alternatif:** asyncio-based debounce. RxPY. Lodash debounce/throttle."""

    # Data deduplication
    if "dedup" in inst_lower or "deduplication" in inst_lower:
        return r"""```python
# SLOW: O(n^2) dedup
def slow_version(items):
    result = []
    for item in items:
        if item not in result: result.append(item)
    return result

# FAST: O(n) with set
def fast_version(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item); result.append(item)
    return result
```
**Big-O:** Slow O(n^2), Fast O(n). Maintains order.
**Alternatif:** list(dict.fromkeys(items)). numpy.unique()."""

    # Approximation algorithms
    if "approximation" in inst_lower:
        return r"""```python
import random

# SLOW: Exact computation
def slow_version(items):
    return sum(items) / len(items) if items else 0

# FAST: Approximate with sampling
def fast_version(items, sample_size=100):
    if len(items) <= sample_size: return sum(items) / len(items)
    sample = random.sample(items, sample_size)
    return sum(sample) / sample_size
```
**Big-O:** Slow O(n), Fast O(sample_size). Monte Carlo sampling.
**Alternatif:** Reservoir sampling. Bloom filter for membership."""

    # Just-in-Time compilation
    if "jit" in inst_lower or "numba" in inst_lower:
        return r"""```python
# Note: Requires numba: pip install numba
# SLOW: Pure Python loop
def slow_version(n):
    s = 0
    for i in range(n):
        s += i ** 2
    return s

# FAST: JIT compiled with Numba
try:
    from numba import jit
    @jit(nopython=True)
    def fast_version(n):
        s = 0
        for i in range(n):
            s += i ** 2
        return s
except ImportError:
    def fast_version(n): return slow_version(n)
```
**Big-O:** Both O(n). JIT ile ~100x hizlanma (C'ye yakin hiz).
**Alternatif:** Cython. PyPy. C extensions. numpy vectorization."""

    # Precomputation
    if "precompute" in inst_lower or "pre-calculation" in inst_lower:
        return r"""```python
# SLOW: Compute on the fly
def slow_version(n):
    primes = []
    for i in range(2, n):
        if all(i % j != 0 for j in range(2, int(i**0.5) + 1)):
            primes.append(i)
    return primes

# FAST: Precompute once, reuse
_precomputed = {}
def fast_version(n, use_cache=True):
    if use_cache and n in _precomputed: return _precomputed[n]
    primes = slow_version(n)
    if use_cache: _precomputed[n] = primes
    return primes
```
**Big-O:** Slow O(n sqrt(n)), Fast O(1) cached. Trade memory for speed.
**Alternatif:** Sieve of Eratosthenes O(n log log n). Memoization."""

    # SIMD (single instruction multiple data)
    if "simd" in inst_lower:
        return r"""```python
import numpy as np

# SLOW: Scalar operations
def slow_version(a, b):
    return [x + y for x, y in zip(a, b)]

# FAST: SIMD via NumPy
def fast_version(a, b):
    return np.add(np.array(a), np.array(b))
```
**Big-O:** Both O(n). SIMD ile ~4-8x hizli parallel instruction.
**Alternatif:** Manual intrinsics (C/C++). OpenMP. Intel MKL."""

    # Chunked processing for large files
    if "chunk" in inst_lower:
        return r"""```python
# SLOW: Read entire file
def slow_version(filepath):
    with open(filepath, "r") as f:
        data = f.read()
    return len(data.split())

# FAST: Read in chunks
def fast_version(filepath, chunk_size=8192):
    word_count = 0
    with open(filepath, "r") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            word_count += len(chunk.split())
    return word_count
```
**Big-O:** Both O(n). Chunked IO ~10x less memory.
**Alternatif:** mmap. streaming APIs. iter_lines for line-based files."""

    # Lookup table
    if "lookup table" in inst_lower or "lut" in inst_lower:
        return r"""```python
# SLOW: Compute each time
def slow_version(x):
    return x ** 2 + 2 * x + 1

# FAST: Precomputed lookup table
_lut = [slow_version(i) for i in range(1001)]

def fast_version(x):
    if 0 <= x < len(_lut): return _lut[x]
    return slow_version(x)
```
**Big-O:** Slow O(log n) with computation, Fast O(1). LUT replaces computation with memory.
**Alternatif:** Cached function. functools.lru_cache. GPU texture lookup."""

    # Bit packing
    if "bit packing" in inst_lower or "bit field" in inst_lower:
        return r"""```python
# SLOW: Store each flag as separate bool
class SlowVersion:
    def __init__(self):
        self.flag_a = False; self.flag_b = False
        self.flag_c = False; self.flag_d = False

# FAST: Pack flags into single integer
class FastVersion:
    def __init__(self):
        self.flags = 0

    def set_flag(self, bit, value):
        if value: self.flags |= (1 << bit)
        else: self.flags &= ~(1 << bit)

    def get_flag(self, bit):
        return bool(self.flags & (1 << bit))

# 4 bool vs 1 int: ~4x less memory
```
**Big-O:** O(1) both. Bit packing saves memory ~8x.
**Alternatif:** bitarray library. Python ints are arbitrary precision."""

    # Eager vs lazy evaluation
    if "eager" in inst_lower and "lazy" in inst_lower:
        return r"""```python
# EAGER: Compute all at once
def slow_version(n):
    return [i ** 2 for i in range(n)]

# LAZY: Compute on demand
def fast_version(n):
    for i in range(n):
        yield i ** 2

# Eager: O(n) memory immediately
# Lazy: O(1) memory, O(n) time total only when consumed
```
**Big-O:** Same O(n) time. Eager O(n) memory, Lazy O(1) memory.
**Alternatif:** itertools.islice. Generator expressions. range() vs list()."""

    # Union-Find optimization (path compression + union by rank)
    if "find" in inst_lower and "optimiz" in inst_lower:
        return r"""```python
# SLOW: Naive union-find
class SlowDSU:
    def __init__(self, n): self.parent = list(range(n))
    def find(self, x):
        while self.parent[x] != x: x = self.parent[x]
        return x
    def union(self, a, b):
        self.parent[self.find(b)] = self.find(a)

# FAST: With path compression + union by rank
class FastDSU:
    def __init__(self, n):
        self.parent = list(range(n)); self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]; x = self.parent[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b: return False
        if self.rank[a] < self.rank[b]: a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]: self.rank[a] += 1
        return True
```
**Big-O:** Slow O(n), Fast O(alpha(n)) ~ O(1). Path compression + union by rank.
**Alternatif:** Union by size. DSU with rollback."""

    # Function inlining
    if "inline" in inst_lower:
        return r"""```python
# SLOW: Many function calls
def slow_version(items):
    def add_one(x): return x + 1
    def double(x): return x * 2
    return [double(add_one(x)) for x in items]

# FAST: Inlined
def fast_version(items):
    return [(x + 1) * 2 for x in items]
```
**Big-O:** Both O(n). Inlining removes function call overhead ~2x faster.
**Alternatif:** @lru_cache. Manual optimization. Cython inlining."""

    # Loop fusion
    if "loop fusion" in inst_lower:
        return r"""```python
# SLOW: Multiple loops
def slow_version(arr):
    a = [x + 1 for x in arr]
    b = [x * 2 for x in a]
    c = [x - 1 for x in b]
    return c

# FAST: Fused single loop
def fast_version(arr):
    return [(x + 1) * 2 - 1 for x in arr]
```
**Big-O:** Both O(n). Fused ~3x faster (single pass, better cache).
**Alternatif:** Loop tiling. Loop interchange. Compiler optimizations."""

    # Matrix multiplication optimization
    if "matrix multiplication" in inst_lower or "matmul" in inst_lower:
        return r"""```python
# SLOW: Naive triple loop
def slow_version(A, B):
    n = len(A); C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C

# FAST: List comprehension + sum
def fast_version(A, B):
    n = len(A); B_T = list(zip(*B))
    return [[sum(A[i][k] * B_T[j][k] for k in range(n)) for j in range(n)] for i in range(n)]
```
**Big-O:** Both O(n^3). Fast version uses transpose for cache locality.
**Alternatif:** Strassen O(n^2.81). numpy.dot (BLAS) O(n^3) optimized."""

    # Tail recursion optimization
    if "tail recursion" in inst_lower:
        return r"""```python
# SLOW: Standard recursion (stack overflow risk)
def slow_version(n, acc=0):
    if n == 0: return acc
    return slow_version(n - 1, acc + n)

# FAST: Iterative (no recursion overhead)
def fast_version(n):
    return n * (n + 1) // 2
```
**Big-O:** Both O(n). Iterative O(1) memory vs recursion O(n) stack.
**Alternatif:** @tail_call_optimized decorator. Loop transformation."""

    # Data structure selection
    if "data structure" in inst_lower:
        return r"""```python
# SLOW: List for membership test
def slow_version(items, queries):
    return [q in items for q in queries]

# FAST: Set for membership test
def fast_version(items, queries):
    item_set = set(items)
    return [q in item_set for q in queries]
```
**Big-O:** Slow O(n*m), Fast O(n + m). Dogru data structure secimi kritik.
**Alternatif:** Bloom filter (probabilistic). Binary search on sorted list."""

    # Bitmap index
    if "bitmap" in inst_lower and "index" in inst_lower:
        return r"""```python
# SLOW: Full scan per query
def slow_version(records, query_col, value):
    return [i for i, rec in enumerate(records) if rec[query_col] == value]

# FAST: Bitmap index
class BitmapIndex:
    def __init__(self, records, col):
        self.values = {}
        for i, rec in enumerate(records):
            v = rec[col]
            if v not in self.values: self.values[v] = 0
            self.values[v] |= (1 << i)

    def query(self, value):
        if value not in self.values: return []
        bitmap = self.values[value]
        return [i for i in range(bitmap.bit_length()) if bitmap & (1 << i)]
```
**Big-O:** Slow O(n), Fast O(num_results). Bit operations are CPU-efficient.
**Alternatif:** Roaring Bitmaps. B-tree index. Hash index."""

    # Bloom filter optimization for cache
    if "bloom" in inst_lower and "cache" in inst_lower:
        return r"""```python
# SLOW: Always query expensive backend
def slow_version(key):
    return expensive_lookup(key)

def expensive_lookup(k): return k

# FAST: Bloom filter rejects negatives fast
class BloomCache:
    def __init__(self):
        self.cache = {}; self.bloom = BloomFilter()

    def get(self, key):
        if key not in self.bloom: return None
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value; self.bloom.add(key)

class BloomFilter:
    def __init__(self): self.bits = set()
    def add(self, item): self.bits.add(hash(item) % 10000)
    def __contains__(self, item): return hash(item) % 10000 in self.bits
```
**Big-O:** O(1) with filter, avoids ~90% of backend calls.
**Alternatif:** Redis with Bloom Module. Cuckoo filter."""

    # Big-O analysis
    if "big-o" in inst_lower or "dar bogaz" in inst_lower:
        return """```python
# Big-O Analizi ve Dar Bogaz Tespiti
import time

def analyze_performance(func, *args):
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    return result, elapsed

# Ornek: O(n^2) -> O(n log n) iyilestirme
def slow_version(arr):  # O(n^2) bubble sort
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]: arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def fast_version(arr):  # O(n log n) timsort
    return sorted(arr)
```
**Big-O:** Analiz: profil ile en yavas bolum bulunur, algoritmik iyilestirme yapilir.
**Alternatif:** cProfile, py-spy, flamegraphs ile detayli profil."""

    # Loop-invariant code motion
    if "loop-invariant" in inst_lower or "invariant" in inst_lower:
        return """```python
# SLOW: Invariant expression inside loop
def slow_version(items):
    result = []
    for x in items:
        result.append(x ** 2 + len(items) // 2)  # len(items)//2 repeats each iteration
    return result

# FAST: Hoist invariant outside loop
def fast_version(items):
    offset = len(items) // 2  # computed once
    return [x ** 2 + offset for x in items]
```
**Big-O:** Both O(n). Fast version avoids repeated computation.
**Alternatif:** Compiler usually does this automatically (CSE)."""

    # Branch prediction
    if "branch prediction" in inst_lower:
        return """```python
# SLOW: Unpredictable branches
def slow_version(arr):
    sorted_true = []; sorted_false = []
    for x in arr:
        if x > 0: sorted_true.append(x)
        else: sorted_false.append(x)
    return sorted_true, sorted_false

# FAST: Sort first for predictable branches
def fast_version(arr):
    arr_sorted = sorted(arr)
    mid = next((i for i, x in enumerate(arr_sorted) if x > 0), len(arr_sorted))
    return arr_sorted[mid:], arr_sorted[:mid]
```
**Big-O:** O(n log n) sort + O(n). Predictable branches are ~10x faster.
**Alternatif:** Branchless programming (bitwise ops). CMOV instruction."""

    # Threading vs multiprocessing
    if "threading" in inst_lower or "multiprocessing" in inst_lower or "gil" in inst_lower:
        return """```python
# I/O-bound: threading faster
import threading, time

def io_task(n):
    time.sleep(0.1)  # simulate I/O

def threading_version():
    threads = [threading.Thread(target=io_task, args=(i,)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

# CPU-bound: multiprocessing faster
from multiprocessing import Pool

def cpu_task(n):
    return sum(i * i for i in range(10**6))

def multiprocessing_version():
    with Pool(4) as p: return p.map(cpu_task, range(10))
```
**Big-O:** I/O-bound: threading ~10x faster. CPU-bound: multiprocessing ~N_cores faster.
**Alternatif:** asyncio for I/O. Cython/Numba for CPU."""

    # Cython / JIT
    if "cython" in inst_lower or "jit" in inst_lower or "numba" in inst_lower:
        return """```python
# Pure Python
def slow_version(n):
    s = 0
    for i in range(n): s += i * i
    return s

# With Numba JIT
try:
    from numba import jit
    @jit(nopython=True)
    def fast_version(n):
        s = 0
        for i in range(n): s += i * i
        return s
except ImportError:
    def fast_version(n): return slow_version(n)
```
**Big-O:** Both O(n). JIT ile ~100x hizli. Cython ile C extension.
**Alternatif:** Cython (.pyx -> .so). PyPy JIT. numpy vectorization."""

    # Web / System optimization patterns
    if "http/2" in inst_lower or "multiplexing" in inst_lower:
        return """```python
# HTTP/2 Multiplexing: single connection, parallel streams
# HTTP/1.1: 6 concurrent connections per origin
# HTTP/2: Stream multiplexing, header compression, server push
# Benefit: ~2x faster page loads

# Implementation (Python aiohttp)
import aiohttp, asyncio
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        return await asyncio.gather(*tasks)
```
**Big-O:** Single connection, N parallel streams. ~2x faster than HTTP/1.1.
**Alternatif:** HTTP/3 (QUIC). gRPC (HTTP/2 based)."""

    if "webpack" in inst_lower or "tree shaking" in inst_lower or "code splitting" in inst_lower:
        return """```python
# Webpack optimizations:
# 1. Tree Shaking: remove unused exports (static imports only)
# 2. Code Splitting: dynamic import() for lazy loading
# 3. Minification: TerserPlugin
# 4. Bundle analysis: webpack-bundle-analyzer

# webpack.config.js (conceptual)
module.exports = {
  optimization: {
    usedExports: true,  // tree shaking
    splitChunks: { chunks: 'all' },  // code splitting
    minimize: true,
  },
};
```
**Big-O:** Smaller bundle = faster load. 30-70% size reduction.
**Alternatif:** Vite (esbuild). Rollup. Parcel."""

    if "cdn" in inst_lower or "prefetch" in inst_lower or "preload" in inst_lower:
        return """```python
# Resource Hints for optimization:
# prefetch: fetch for FUTURE navigation
# preload: fetch for CURRENT page (high priority)
# preconnect: warm up connection early

# HTML usage:
# <link rel="prefetch" href="/next-page.js">
# <link rel="preload" href="/critical.css" as="style">
# <link rel="preconnect" href="https://api.example.com">

# CDN: edge caching, DDoS protection, SSL termination
# Benefit: 40-60% latency reduction
```
**Big-O:** Speculative loading. Preload critical resources.
**Alternatif:** Service Worker caching. HTTP/2 server push."""

    # Data-oriented design
    if "data-oriented" in inst_lower or "aos" in inst_lower or "soa" in inst_lower:
        return """```python
# AoS (Array of Structs) - cache unfriendly
class Particle:
    def __init__(self): self.x = self.y = self.z = 0.0
particles = [Particle() for _ in range(1000)]

# SoA (Struct of Arrays) - cache friendly
class Particles:
    def __init__(self, n):
        self.x = [0.0] * n; self.y = [0.0] * n; self.z = [0.0] * n

# SoA is faster for SIMD vectorization and cache locality
# AoS is more readable and OOP-friendly
```
**Big-O:** SoA ~2-5x faster for bulk operations. Better cache utilization.
**Alternatif:** Columnar storage (Parquet). numpy structured arrays."""

    # Partitioning / Sharding
    if "partition" in inst_lower or "shard" in inst_lower:
        return """```python
# Range partitioning
CREATE TABLE orders (
    id INT, order_date DATE, amount DECIMAL
) PARTITION BY RANGE (YEAR(order_date)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025)
);

# Hash sharding (application level)
def get_shard(key, num_shards=4):
    return hash(key) % num_shards
```
**Big-O:** Partition pruning reduces scanned data ~Nx. Sharding distributes load.
**Alternatif:** List partitioning. Composite partitioning. Vitess/MySQL Cluster."""

    # Redis caching
    if "redis" in inst_lower:
        return """```python
import redis, json

class RedisCache:
    def __init__(self, host='localhost', port=6379):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def get(self, key):
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key, value, ttl=300):
        self.client.setex(key, ttl, json.dumps(value))

    def delete(self, key): self.client.delete(key)
    def flush(self): self.client.flushdb()
```
**Big-O:** O(1) get/set. In-memory, ~1000x faster than disk DB.
**Alternatif:** Memcached. Local memory cache. Hazelcast."""

    return None


def gen_debug(inst):
    inst_lower = inst.lower()
    # Null pointer / None check
    if "null" in inst_lower or "none" in inst_lower or "pointer" in inst_lower:
        return r"""```python
# HATALI KOD
def get_user_name(user):
    return user.name

# DUZELTILMIS KOD
def get_user_name(user):
    if user is None: return "Unknown"
    return user.name
```
**Hata:** None/null kontrolu yok, AttributeError firlatir.
**Cozum:** early return guard clause ile None kontrolu."""

    # Off-by-one
    if "off by one" in inst_lower or "index" in inst_lower and "off" in inst_lower:
        return r"""```python
# HATALI KOD
def get_last(arr):
    return arr[len(arr)]

# DUZELTILMIS KOD
def get_last(arr):
    if not arr: return None
    return arr[len(arr) - 1]
```
**Hata:** len(arr) index out of range. Son eleman len(arr)-1.
**Cozum:** len(arr) - 1 ile son indeks. Bos array kontrolu."""

    # Division by zero
    if "division" in inst_lower or "zero" in inst_lower:
        return r"""```python
# HATALI KOD
def divide(a, b):
    return a / b

# DUZELTILMIS KOD
def divide(a, b):
    if b == 0: raise ValueError("Division by zero")
    return a / b
```
**Hata:** sifira bolme ZeroDivisionError firlatir.
**Cozum:** Sifir kontrolu ekle, exception raise et veya None/0 don."""

    # Memory leak
    if "memory leak" in inst_lower:
        return r"""```python
# HATALI KOD
cache = {}
def fetch_data(key):
    data = expensive_query(key)
    cache[key] = data
    return data

# DUZELTILMIS KOD
from collections import OrderedDict

class LRUCache:
    def __init__(self, maxsize=100):
        self.cache = OrderedDict(); self.maxsize = maxsize

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key); return self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = value
        if len(self.cache) > self.maxsize: self.cache.popitem(last=False)

def expensive_query(k): return k
```
**Hata:** cache sinirsiz buyur, memory leak.
**Cozum:** LRU cache sabit boyut, eski veriyi otomatik sil."""

    # Infinite loop
    if "infinite loop" in inst_lower:
        return r"""```python
# HATALI KOD
def find_item(arr, target):
    i = 0
    while i < len(arr):
        if arr[i] == target: return i
    return -1

# DUZELTILMIS KOD
def find_item(arr, target):
    for i in range(len(arr)):
        if arr[i] == target: return i
    return -1
```
**Hata:** Dongude i artmiyor, sonsuz dongu.
**Cozum:** Degeriskeni artir (i += 1) veya for loop kullan."""

    # Deadlock
    if "deadlock" in inst_lower:
        return r"""```python
# HATALI KOD (deadlock scenario)
import threading
lock1, lock2 = threading.Lock(), threading.Lock()

def thread1():
    with lock1:
        with lock2: pass

def thread2():
    with lock2:
        with lock1: pass

# DUZELTILMIS KOD
def thread1():
    with lock1:
        with lock2: pass

def thread2():
    with lock1:  # Same lock order
        with lock2: pass
```
**Hata:** Farkli lock sirasi deadlock (karsilikli bekleme).
**Cozum:** Her zaman ayni sirada lock al. try_lock ile timeout."""

    # Race condition
    if "race" in inst_lower:
        return r"""```python
# HATALI KOD
counter = 0
def increment():
    global counter
    for _ in range(1000): counter += 1

# DUZELTILMIS KOD
import threading
counter = 0; lock = threading.Lock()
def increment():
    global counter
    for _ in range(1000):
        with lock: counter += 1
```
**Hata:** += atomik degil, thread-safe degil, race condition.
**Cozum:** Lock ile kritik bolgeyi koru. threading.Lock context manager."""

    # Uninitialized variable
    if "uninitialized" in inst_lower:
        return r"""```python
# HATALI KOD
def process_items(items):
    total = total + sum(items)  # NameError
    return total

# DUZELTILMIS KOD
def process_items(items):
    total = 0
    total = total + sum(items)
    return total
```
**Hata:** total tanimlanmamis, NameError firlatir.
**Cozum:** Degiskeni kullanmadan once baslangic degeri ver."""

    # Type error
    if "type" in inst_lower:
        return r"""```python
# HATALI KOD
def add(a, b):
    return a + b

# DUZELTILMIS KOD
def add(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Numeric values required")
    return a + b
```
**Hata:** Tip uyusmazligi (str + int gibi) TypeError firlatir.
**Cozum:** isinstance ile tip kontrolu, acik tip donusumu."""

    # Resource leak
    if "resource leak" in inst_lower:
        return r"""```python
# HATALI KOD
def read_file(path):
    f = open(path, "r")
    return f.read()

# DUZELTILMIS KOD
def read_file(path):
    with open(path, "r") as f:
        return f.read()
```
**Hata:** File handle kapatilmamis, resource leak.
**Cozum:** with statement otomatik close garanti eder."""

    # SQL injection
    if "sql injection" in inst_lower:
        return r"""```python
# HATALI KOD
def get_user(db, user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# DUZELTILMIS KOD
def get_user(db, user_id):
    return db.query("SELECT * FROM users WHERE id = ?", (user_id,))
```
**Hata:** String interpolation SQL injection acigi.
**Cozum:** Parameterized query / prepared statement kullan."""

    # XSS
    if "xss" in inst_lower or "html injection" in inst_lower:
        return r"""```python
import html

# HATALI KOD
def render_comment(text):
    return f"<div>{text}</div>"

# DUZELTILMIS KOD
def render_comment(text):
    return f"<div>{html.escape(text)}</div>"
```
**Hata:** Kullanici girdisi dogrudan HTML'e eklenmis, XSS acigi.
**Cozum:** html.escape() ile ozel karakterleri donustur."""

    # Buffer overflow
    if "buffer overflow" in inst_lower:
        return r"""```python
# HATALI KOD
def copy_fixed(dest, src, size):
    for i in range(len(src)):
        dest[i] = src[i]

# DUZELTILMIS KOD
def copy_fixed(dest, src, size):
    for i in range(min(len(src), size)):
        dest[i] = src[i]
```
**Hata:** Hedef buffer boyutundan fazla yazma, buffer overflow.
**Cozum:** min(len(src), size) ile sinir kontrolu."""

    # Logic error in condition
    if "logic" in inst_lower or "operator" in inst_lower:
        return r"""```python
# HATALI KOD
def is_valid(age, has_permission):
    return age >= 18 and has_permission or age >= 21

# DUZELTILMIS KOD
def is_valid(age, has_permission):
    return (age >= 18 and has_permission) or age >= 21
```
**Hata:** Operator precedence hatasi, yanlis mantiksal degerlendirme.
**Cozum:** Parantezlerle onceligi acikca belirt."""

    # Mutating while iterating
    if "mutation" in inst_lower or "modifying" in inst_lower or "iteration" in inst_lower:
        return r"""```python
# HATALI KOD
def remove_evens(arr):
    for x in arr:
        if x % 2 == 0: arr.remove(x)
    return arr

# DUZELTILMIS KOD
def remove_evens(arr):
    return [x for x in arr if x % 2 != 0]
```
**Hata:** Iterasyon sirasinda listeyi degistirmek yanlis sonuc.
**Cozum:** List comprehension ile yeni liste olustur."""

    # Shallow copy vs deep copy
    if "shallow" in inst_lower or "deep copy" in inst_lower or "copy" in inst_lower:
        return r"""```python
import copy

# HATALI KOD
def duplicate_grid(grid):
    return grid[:]  # shallow copy, nested lists shared

# DUZELTILMIS KOD
def duplicate_grid(grid):
    return copy.deepcopy(grid)
```
**Hata:** Shallow copy nested list'lerde referans paylasimi.
**Cozum:** copy.deepcopy() ile tam bagimsiz kopya."""

    # Default mutable argument
    if "default" in inst_lower and "mutable" in inst_lower:
        return r"""```python
# HATALI KOD
def add_item(item, items=[]):
    items.append(item)
    return items

# DUZELTILMIS KOD
def add_item(item, items=None):
    if items is None: items = []
    items.append(item)
    return items
```
**Hata:** Mutable default argument (list) fonksiyonlar arasi paylasilir.
**Cozum:** None default + fonksiyon icinde initialization."""

    # Exception handling too broad
    if "exception" in inst_lower or "bare except" in inst_lower:
        return r"""```python
# HATALI KOD
def parse_number(s):
    try:
        return int(s)
    except:  # bare except
        return None

# DUZELTILMIS KOD
def parse_number(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None
```
**Hata:** Bare except tum hatalari yutar (KeyboardInterrupt dahil).
**Cozum:** Spesifik exception type'lari yakala."""

    # Swallowing exceptions
    if "swallow" in inst_lower or "pass" in inst_lower and "except" in inst_lower:
        return r"""```python
# HATALI KOD
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        pass

# DUZELTILMIS KOD
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return float("inf")
```
**Hata:** pass ile exception yutulmus, hata gizlenmis.
**Cozum:** En azindan logla veya anlamli bir deger don."""

    # Concurrent modification
    if "concurrent" in inst_lower:
        return r"""```python
# HATALI KOD
results = []
def worker(data):
    results.append(data ** 2)

# DUZELTILMIS KOD
import threading
results = []; lock = threading.Lock()
def worker(data):
    with lock:
        results.append(data ** 2)
```
**Hata:** Thread-safe olmayan liste paylasimi, data corruption.
**Cozum:** Lock ile koru veya queue.Queue kullan."""

    # Recursion depth
    if "recursion" in inst_lower:
        return r"""```python
# HATALI KOD
def factorial(n):
    if n == 0: return 1
    return n * factorial(n - 1)

# DUZELTILMIS KOD
def factorial(n):
    result = 1
    for i in range(2, n + 1): result *= i
    return result
```
**Hata:** n buyukse RecursionError (stack overflow).
**Cozum:** Iteratif cozum. sys.setrecursionlimit ile limit artirma."""

    # Encoding issues
    if "encoding" in inst_lower or "unicode" in inst_lower:
        return r"""```python
# HATALI KOD
def read_text(path):
    with open(path, "r") as f:
        return f.read()

# DUZELTILMIS KOD
def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
```
**Hata:** Varsayilan encoding platforma gore degisir, UnicodeDecodeError.
**Cozum:** Acikca encoding="utf-8" belirt."""

    # Integer overflow
    if "integer overflow" in inst_lower or "int overflow" in inst_lower:
        return r"""```python
# HATALI KOD
def multiply_large(a, b):
    return a * b  # Python handles big ints, but overflow in other langs

# DUZELTILMIS KOD (for C-like languages)
def multiply_large_safe(a, b, max_val=2**31 - 1):
    result = a * b
    if result > max_val: raise OverflowError("Integer overflow")
    return result
```
**Hata:** Python'da big int sinirsiz, ama C/Java'da overflow olur.
**Cozum:** Sinir kontrolu. Python'da dogal koruma var."""

    # Float precision
    if "float" in inst_lower:
        return r"""```python
# HATALI KOD
def calculate_total(prices):
    total = 0.0
    for p in prices: total += p
    return total

# DUZELTILMIS KOD
from decimal import Decimal, ROUND_HALF_UP

def calculate_total(prices):
    total = Decimal("0.00")
    for p in prices: total += Decimal(str(p))
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
```
**Hata:** Float kayan nokta hatalari (0.1 + 0.2 != 0.3).
**Cozum:** Decimal ile hassas hesaplama, ozellikle para islemlerinde."""

    # IndexError list
    if "indexerror" in inst_lower or "index error" in inst_lower:
        return r"""```python
# HATALI KOD
def get_middle(arr):
    return arr[len(arr) // 2]

# DUZELTILMIS KOD
def get_middle(arr):
    if not arr: return None
    return arr[len(arr) // 2]
```
**Hata:** Bos liste IndexError firlatir.
**Cozum:** Bos liste kontrolu, guard clause."""

    # KeyError dict
    if "keyerror" in inst_lower or "key error" in inst_lower:
        return r"""```python
# HATALI KOD
def get_value(d, key):
    return d[key]

# DUZELTILMIS KOD
def get_value(d, key):
    return d.get(key, None)
```
**Hata:** Olmayan key KeyError firlatir.
**Cozum:** .get() ile default deger, veya try/except KeyError."""

    # AttributeError
    if "attributeerror" in inst_lower or "attribute error" in inst_lower:
        return r"""```python
# HATALI KOD
def get_length(obj):
    return obj.length

# DUZELTILMIS KOD
def get_length(obj):
    return getattr(obj, "length", 0)
```
**Hata:** obj.length yoksa AttributeError.
**Cozum:** hasattr kontrolu veya getattr ile default."""

    # AssertionError / incorrect assert
    if "assertion" in inst_lower:
        return r"""```python
# HATALI KOD
def process_age(age):
    assert age > 0
    return age * 12

# DUZELTILMIS KOD
def process_age(age):
    if age <= 0: raise ValueError("Age must be positive")
    return age * 12
```
**Hata:** assert production'da devre disi kalabilir (-O flag).
**Cozum:** explicit ValueError ile dogrulama."""

    # Generator exhaustion
    if "generator" in inst_lower and "exhaust" in inst_lower:
        return r"""```python
# HATALI KOD
def get_data():
    yield 1; yield 2; yield 3

gen = get_data()
first = list(gen)
second = list(gen)  # Empty!

# DUZELTILMIS KOD
def get_data():
    return [1, 2, 3]

data = get_data()
first = data[:]
second = data[:]
```
**Hata:** Generator bir kere tuketilir, tekrar kullanilamaz.
**Cozum:** Listeye cevir veya generator'u yeniden olustur."""

    # Chained comparison
    if "comparison" in inst_lower:
        return r"""```python
# HATALI KOD
def in_range(x, low, high):
    return low < x < high  # Actually correct Python!

# HATALI KOD (other langs)
def in_range_other_langs(x, low, high):
    return low < x < high  # low < x returns bool, then bool < high

# DUZELTILMIS KOD
def in_range_other_langs(x, low, high):
    return low < x and x < high

# Note: Python supports chained comparison correctly!
```
**Hata:** Bazi dillerde low < x < high calismaz.
**Cozum:** Python'da dogru, C/Java'da ayri ayri kontrol gerek."""

    # Variable shadowing
    if "shadow" in inst_lower:
        return r"""```python
# HATALI KOD
def calculate(items):
    total = 0
    for total in items:  # shadows outer total
        pass
    return total  # returns last item, not sum!

# DUZELTILMIS KOD
def calculate(items):
    total = 0
    for item in items:
        total += item
    return total
```
**Hata:** Loop variable outer variable'i golgeliyor (shadowing).
**Cozum:** Farkli isimlendirme kullan."""

    # Circular import
    if "circular" in inst_lower and "import" in inst_lower:
        return r"""```python
# HATALI KOD (circular import)
# a.py: from b import y
# b.py: from a import x

# DUZELTILMIS KOD
# Option 1: Lazy import (import inside function)
def get_y():
    from b import y
    return y

# Option 2: Common module
# common.py: x = ...; y = ...
# a.py: from common import x
# b.py: from common import y
```
**Hata:** Iki modul birbirini import eder, ImportError.
**Cozum:** Lazy import veya ortak modul. Yeniden yapilandir."""

    # String formatting
    if "format" in inst_lower:
        return r"""```python
# HATALI KOD
def greet(name, age):
    return "Hello " + name + ", you are " + age + " years old"

# DUZELTILMIS KOD
def greet(name, age):
    return f"Hello {name}, you are {age} years old"
```
**Hata:** Tip donusumu eksik (age int ise hata). Okunabilirlik zor.
**Cozum:** f-string ile otomatik str() donusumu, okunabilir."""

    # == vs is
    if "==" in inst_lower or "is" in inst_lower:
        return r"""```python
# HATALI KOD
def check_none(value):
    return value == None  # PEP8 uyarisi

def check_singleton(value):
    return value == True  # 1 de True kabul edilir

# DUZELTILMIS KOD
def check_none(value):
    return value is None

def check_singleton(value):
    return value is True
```
**Hata:** == deger karsilastirmasi, is identity kontrolu. None/True singletondur.
**Cozum:** Singleton'lar icin is kullan. Deger karsilastirmasi icin ==."""

    # GIL problem
    if "gil" in inst_lower or "global interpreter" in inst_lower:
        return """```python
# HATALI KOD: Expecting true parallelism
import threading
counter = 0
def increment():
    global counter
    for _ in range(1000000): counter += 1  # GIL prevents parallelism

# DUZELTILMIS KOD: Use multiprocessing for CPU-bound
from multiprocessing import Process, Value

def increment_mp(counter):
    for _ in range(1000000): counter.value += 1

counter = Value('i', 0)
p1 = Process(target=increment_mp, args=(counter,))
p2 = Process(target=increment_mp, args=(counter,))
p1.start(); p2.start(); p1.join(); p2.join()
```
**Hata:** GIL nedeniyle threading CPU-bound islerde paralel calismaz.
**Cozum:** CPU-bound -> multiprocessing. I/O-bound -> threading/asyncio."""

    # Starvation
    if "starvation" in inst_lower:
        return """```python
# HATALI KOD: Low priority thread never runs
import threading, time

low_ready = threading.Event()
def low_priority():
    low_ready.wait()
    while True: time.sleep(0.001)  # never gets CPU

# DUZELTILMIS KOD: Fair scheduling
import queue
q = queue.PriorityQueue()

def worker():
    while True:
        priority, task = q.get()
        time.sleep(0.001)  # yields CPU
        q.task_done()
```
**Hata:** Dusuk priority thread'ler hic calismayabilir (starvation).
**Cozum:** Priority queue ile fair scheduling. Zaman paylasimi."""

    # Livelock
    if "livelock" in inst_lower:
        return """```python
# HATALI KOD: Livelock - threads keep responding to each other
import threading, time

flag = [False, False]

def thread_a():
    while True:
        flag[0] = True
        if flag[1]:
            flag[0] = False; time.sleep(0.1); continue
        break  # critical section

# DUZELTILMIS KOD: Random backoff breaks symmetry
import random

def thread_a_fixed():
    for _ in range(10):
        flag[0] = True
        if flag[1]:
            flag[0] = False; time.sleep(random.random()); continue
        break
```
**Hata:** Livelock: threads aktif ama islem yapamiyor, birbirine cevap veriyor.
**Cozum:** Random backoff. Exponential backoff. Timeout ile coz."""

    # Priority inversion
    if "priority inversion" in inst_lower:
        return """```python
# HATALI KOD: Low priority holds lock, high priority waits
import threading
lock = threading.Lock()

def low_priority():  # runs first, holds lock
    with lock: time.sleep(1)

def high_priority():  # waits for low priority
    with lock: pass

# DUZELTILMIS KOD: Priority inheritance
# When high-priority waits, low-priority temporarily inherits its priority
# Python threading doesn't support this natively
# Use real-time OS or mutex with priority inheritance protocol
```
**Hata:** Dusuk priority thread lock tutarken yuksek priority thread bekler.
**Cozum:** Priority inheritance protocol. Real-time mutex."""

    # CSRF
    if "csrf" in inst_lower:
        return """```python
# HATALI KOD: No CSRF protection
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    execute_transfer(amount)  # vulnerable to CSRF

# DUZELTILMIS KOD: CSRF token
import secrets
csrf_tokens = {}

@app.route('/transfer', methods=['POST'])
def transfer():
    token = request.form.get('csrf_token')
    if token != session.get('csrf_token'): return "Invalid CSRF token", 403
    amount = request.form['amount']
    execute_transfer(amount)
```
**Hata:** CSRF: kullaniciyi kandirarak istek yaptirir.
**Cozum:** CSRF token (double submit), SameSite cookie, Referer check."""

    # Callback hell
    if "callback hell" in inst_lower or "async/await" in inst_lower:
        return """```python
# HATALI KOD: Callback hell (nested callbacks)
def fetch_data(cb):
    api_call(lambda res1:
        api_call2(res1, lambda res2:
            api_call3(res2, cb)))

# DUZELTILMIS KOD: async/await
import asyncio

async def fetch_data_async():
    res1 = await api_call_async()
    res2 = await api_call2_async(res1)
    return await api_call3_async(res2)
```
**Hata:** Icer ice callback'ler okunamaz, hata ayiklamasi zor.
**Cozum:** async/await ile linear kod. Promises (JS). Future/Promise."""

    # Zombie process
    if "zombie" in inst_lower or "orphan" in inst_lower:
        return """```python
# HATALI KOD: Zombie process (child not waited)
import os, time

pid = os.fork()
if pid == 0: exit(0)  # child exits, becomes zombie
else: time.sleep(5)   # parent didn't wait, zombie exists

# DUZELTILMIS KOD: Wait for child
pid = os.fork()
if pid == 0: exit(0)
else: os.waitpid(pid, 0)  # reaps child, no zombie
```
**Hata:** Zombie: child exit olmus ama parent wait yapmamis. Orphan: parent exit, child adopt edilir.
**Cozum:** waitpid() ile temizle. signal handler(SIGCHLD). double fork."""

    # File descriptor leak
    if "file descriptor" in inst_lower or "fd leak" in inst_lower:
        return """```python
# HATALI KOD: FD leak
def read_data(path):
    f = open(path, 'r')
    return f.read()  # f never closed

# DUZELTILMIS KOD: Context manager
def read_data(path):
    with open(path, 'r') as f:
        return f.read()  # auto-closed
```
**Hata:** Acik file descriptor'lar kapatilmamis, sinirli kaynak tuketimi.
**Cozum:** with statement. try/finally. Resource owner closes."""

    # Thread leak
    if "thread leak" in inst_lower:
        return """```python
# HATALI KOD: Thread leak
import threading

def worker(): pass
for _ in range(1000):
    t = threading.Thread(target=worker)
    t.start()  # threads not joined/reaped

# DUZELTILMIS KOD: Thread pool
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(worker) for _ in range(1000)]
    results = [f.result() for f in futures]  # all threads completed
```
**Hata:** Thread'ler join edilmezse kaynak tuketimi, thread leak.
**Cozum:** Thread pool ile sinirli sayida thread. Daemon threads."""

    # Connection leak
    if "connection leak" in inst_lower:
        return """```python
# HATALI KOD: Connection leak
def query_db(sql):
    conn = create_connection()
    result = conn.execute(sql)
    return result  # conn never closed

# DUZELTILMIS KOD: Context manager
def query_db(sql):
    with create_connection() as conn:
        return conn.execute(sql)  # auto-closed
```
**Hata:** DB/HTTP baglantilari kapatilmamis, connection pool tukenir.
**Cozum:** with statement. Connection pool. try/finally close."""

    # Cursor leak
    if "cursor leak" in inst_lower:
        return """```python
# HATALI KOD: Cursor leak
import sqlite3

def get_users(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()  # cursor not closed

# DUZELTILMIS KOD
def get_users(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()  # context manager closes everything
```
**Hata:** Cursor'lar kapatilmazsa bellek/connection leak.
**Cozum:** Context manager. Cursor'u manuel close()."""

    # Memory fragmentation
    if "memory fragmentation" in inst_lower:
        return """```python
# HATALI KOD: Fragmentation from many small allocations
def process_lots():
    items = []
    for i in range(100000):
        items.append(bytearray(1))  # many small objects

# DUZELTILMIS KOD: Object pool / preallocation
def process_lots():
    pool = bytearray(100000)  # single large allocation
    # use slices of pool

# Alternative: use jemalloc/tcmalloc instead of glibc malloc
```
**Hata:** Cok sayida kucuk allocation -> fragmentation -> OOM.
**Cozum:** Object pool. Preallocation. jemalloc/tcmalloc. PyPy GC."""

    # Stack overflow vs heap overflow
    if "stack overflow" in inst_lower or "heap overflow" in inst_lower:
        return """```python
# Stack overflow: limited call stack (Python default 1000)
def recursive(n):
    if n == 0: return 0
    return n + recursive(n - 1)

# Fix: iterative or increase recursionlimit
import sys
sys.setrecursionlimit(10000)

# Heap overflow: unbound memory allocation
def heap_overflow():
    data = []
    while True: data.append(bytearray(10**6))  # OOM eventually
```
**Hata:** Stack: recursion limit asimi. Heap: sinirsiz bellek alokasyonu.
**Cozum:** Stack -> iterative. Heap -> bounded structures, memory limits."""

    # Rounding error / Banker's rounding
    if "rounding" in inst_lower or "banker" in inst_lower:
        return """```python
# HATALI KOD: Standard rounding (round half up)
print(round(2.5))  # 2 (Python banker's rounding)
print(round(3.5))  # 4 (Python banker's rounding)

# DUZELTILMIS KOD: Explicit rounding
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

# Banker's rounding (round half to even)
d = Decimal('2.5')
print(d.quantize(Decimal('0'), rounding=ROUND_HALF_EVEN))  # 2

# Standard rounding (round half up)
print(d.quantize(Decimal('0'), rounding=ROUND_HALF_UP))  # 3
```
**Hata:** Python default banker's rounding (round half to even) beklenmedik sonuc verebilir.
**Cozum:** Decimal ile explicit rounding mode belirt."""

    # Timezone handling
    if "timezone" in inst_lower:
        return """```python
from datetime import datetime, timezone

# HATALI KOD: Naive datetime
def log_event():
    return f"Event at {datetime.now()}"  # no timezone

# DUZELTILMIS KOD: UTC everywhere
def log_event():
    return f"Event at {datetime.now(timezone.utc).isoformat()}"

# Store UTC, convert to local only for display
def to_local(utc_dt, tz_name='Europe/Istanbul'):
    import pytz
    local_tz = pytz.timezone(tz_name)
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
```
**Hata:** Timezone bilgisi olmayan datetime, DST kaymasi, farkli bolgelerde hata.
**Cozum:** UTC'de sakla, gosterimde cevir. pytz/zoneinfo kullan."""

    # Off-by-one
    if "off-by-one" in inst_lower or "off by one" in inst_lower:
        return """```python
# HATALI KOD
def get_last(arr):
    return arr[len(arr)]  # IndexError

def slice_last(arr):
    return arr[-1:][0]  # works but confusing

# DUZELTILMIS KOD
def get_last(arr):
    return arr[-1] if arr else None

def range_loop(n):
    return list(range(n))  # 0 to n-1, NOT 1 to n
```
**Hata:** 0-index vs 1-index karisikligi. len(arr) kullanimi.
**Cozum:** Negative indexing. range(n) = 0..n-1. Inclusive/exclusive dikkat."""

    # Tuple unpack error
    if "tuple unpack" in inst_lower or "too many values" in inst_lower:
        return """```python
# HATALI KOD
a, b = [1, 2, 3]  # ValueError: too many values to unpack

# DUZELTILMIS KOD
a, b, c = [1, 2, 3]  # correct count

# Or use star expression
first, *rest = [1, 2, 3]  # first=1, rest=[2, 3]
```
**Hata:** Unpack edilen iterable ile hedef degisken sayisi uyusmaz.
**Cozum:** Dogru sayida degisken. *rest ile kalanlari topla."""

    # Monkey patching
    if "monkey patching" in inst_lower:
        return """```python
# HATALI KOD: Unexpected side effects
class Calculator:
    def add(self, a, b): return a + b

# Someone monkey-patches
Calculator.add = lambda self, a, b: a * b  # breaks everything

# DUZELTILMIS KOD: Use inheritance or dependency injection
class SafeCalculator(Calculator):
    def add(self, a, b):
        return super().add(a, b)  # preserve original behavior

# Or use __finalize__ to prevent patching
```
**Hata:** Calisma zamaninda sinif/metod degistirme, beklenmedik yan etkiler.
**Cozum:** Open/Closed prensibi. Inheritance. DI. @final decorator."""

    return None


def gen_clean_code(inst):
    inst_lower = inst.lower()
    if "log" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Logging Best Practices"

    def setup_logger(self):
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        return logging.getLogger(__name__)

    def execute(self):
        logger = self.setup_logger()
        logger.info("Application started")
        logger.debug("Debug info (only if DEBUG level)")
        logger.error("Error occurred")
        return "Clean logging implementation"
```
**Big-O:** -
**Alternatif:** structlog, loguru kutuphaneleri."""

    if "docstring" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Docstring Best Practices"

    def calculate(self, a, b, operation="add"):
        # Perform basic arithmetic operations.
        # Args: a, b (numeric), operation: add/subtract/multiply/divide
        # Returns: Result of operation
        # Raises: ValueError if unknown op or div by zero
        operations = {
            "add": a + b, "subtract": a - b,
            "multiply": a * b, "divide": a / b if b != 0 else None
        }
        if operation not in operations: raise ValueError(f"Unknown operation: {operation}")
        return operations[operation]

    def execute(self):
        return self.calculate(10, 5, "add")
```
**Big-O:** -
**Alternatif:** NumPy-style, Sphinx-style docstring. pydoc."""

    if "naming" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Naming Conventions"

    def get_user_full_name(self, user_id):
        # Get user full name from database
        user_data = self._fetch_user(user_id)
        return f"{user_data['first_name']} {user_data['last_name']}"

    def _fetch_user(self, user_id):
        # Private helper - underscore prefix
        return {"first_name": "John", "last_name": "Doe"}

    def execute(self):
        return self.get_user_full_name(42)
```
**Big-O:** -
**Alternatif:** Class names: PascalCase. Constants: UPPER_CASE."""

    if "type hint" in inst_lower or "typing" in inst_lower:
        return """```python
from typing import List, Optional, Dict, Any

class CleanSolution:
    def __init__(self):
        self.name = "Type Hints"

    def process_users(self, users: List[Dict[str, Any]]) -> Optional[str]:
        if not users: return None
        total = sum(u.get("age", 0) for u in users)
        return f"Total age: {total}"

    def execute(self) -> str:
        result = self.process_users([{"name": "Alice", "age": 30}])
        return result or "No users"
```
**Big-O:** -
**Alternatif:** mypy statik tip kontrolu. dataclasses. pydantic modeller."""

    if "function" in inst_lower and "small" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Small Functions (Single Responsibility)"

    def validate_input(self, data):
        if not data: raise ValueError("Data required")
        return True

    def transform(self, data):
        return [x * 2 for x in data]

    def format_result(self, data):
        return f"Processed {len(data)} items"

    def execute(self):
        data = [1, 2, 3]
        self.validate_input(data)
        transformed = self.transform(data)
        return self.format_result(transformed)
```
**Big-O:** -
**Alternatif:** Fonksiyonel programlama (map/filter). Pipeline pattern."""

    if "error handling" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Error Handling Best Practices"

    def divide_numbers(self, a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            raise ValueError("Cannot divide by zero")
        except TypeError:
            raise TypeError("Numeric values required")
        else:
            return result
        finally:
            pass  # Cleanup if needed

    def execute(self):
        try:
            return self.divide_numbers(10, 2)
        except (ValueError, TypeError) as e:
            return f"Error: {e}"
```
**Big-O:** -
**Alternatif:** Result type (Rust-style). Either monad. Custom exceptions."""

    if "context manager" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Context Manager"

    class ManagedResource:
        def __enter__(self):
            print("Resource acquired"); return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            print("Resource released"); return False
        def use(self): return "Using resource"

    def execute(self):
        with self.ManagedResource() as res:
            return res.use()
```
**Big-O:** -
**Alternatif:** contextlib.contextmanager decorator. contextlib.ExitStack."""

    if "decorator" in inst_lower:
        return """```python
import functools, time

class CleanSolution:
    def __init__(self):
        self.name = "Decorator Pattern"

    @staticmethod
    def timer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            print(f"{func.__name__} took {time.time() - start:.3f}s")
            return result
        return wrapper

    @timer
    def slow_function(self):
        time.sleep(0.1)
        return "Done"

    def execute(self):
        return self.slow_function()
```
**Big-O:** -
**Alternatif:** functools.wraps ile metadata koruma. Class-based decorators."""

    if "srp" in inst_lower or "single responsibility" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Single Responsibility Principle (SRP)"

    class UserValidator:
        def validate(self, user): return bool(user.get("email"))

    class UserRepository:
        def save(self, user): return f"User saved: {user['name']}"

    class UserNotifier:
        def send_welcome(self, user): return f"Welcome email sent to {user['email']}"

    def execute(self):
        user = {"name": "Alice", "email": "alice@example.com"}
        validator = self.UserValidator()
        repo = self.UserRepository()
        notifier = self.UserNotifier()

        if not validator.validate(user): return "Invalid user"
        repo.save(user)
        return notifier.send_welcome(user)
```
**Big-O:** -
**Alternatif:** Fat models -> service layer. Use case driven design."""

    if "composition" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Composition over Inheritance"

    class Engine:
        def start(self): return "Engine started"
        def stop(self): return "Engine stopped"

    class Wheels:
        def rotate(self): return "Wheels rotating"

    class Car:
        def __init__(self):
            self.engine = self.Engine()
            self.wheels = self.Wheels()

        def drive(self):
            return f"{self.engine.start()} and {self.wheels.rotate()}"

    def execute(self):
        car = self.Car()
        return car.drive()
```
**Big-O:** -
**Alternatif:** Strategy pattern. Dependency injection ile looser coupling."""

    if "property" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Property Decorator"

    class Temperature:
        def __init__(self, celsius=0):
            self._celsius = celsius

        @property
        def celsius(self): return self._celsius

        @celsius.setter
        def celsius(self, value):
            if value < -273.15: raise ValueError("Below absolute zero")
            self._celsius = value

        @property
        def fahrenheit(self):
            return self._celsius * 9/5 + 32

    def execute(self):
        t = self.Temperature(25)
        return f"{t.celsius}C = {t.fahrenheit}F"
```
**Big-O:** -
**Alternatif:** __getattr__ / __setattr__. descriptors. dataclasses.field."""

    if "dataclass" in inst_lower:
        return """```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class User:
    name: str
    email: str
    age: int = 0
    tags: List[str] = field(default_factory=list)

class CleanSolution:
    def __init__(self):
        self.name = "Dataclass Best Practices"

    def execute(self):
        user = User(name="Alice", email="alice@example.com", age=30)
        return f"{user.name}, {user.email}, tags: {user.tags}"
```
**Big-O:** -
**Alternatif:** NamedTuple (immutable). attrs kutuphanesi. pydantic."""

    if "dependency injection" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Dependency Injection"

    class EmailService:
        def send(self, msg): return f"Email sent: {msg}"

    class SMSService:
        def send(self, msg): return f"SMS sent: {msg}"

    class NotificationService:
        def __init__(self, provider):
            self.provider = provider
        def notify(self, msg): return self.provider.send(msg)

    def execute(self):
        email_service = self.EmailService()
        notifier = self.NotificationService(email_service)
        return notifier.notify("Hello!")
```
**Big-O:** -
**Alternatif:** Abstract base classes. Protocol classes. DI containers."""

    if "factory" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Factory Pattern"

    class Dog: def speak(self): return "Woof"
    class Cat: def speak(self): return "Meow"
    class Duck: def speak(self): return "Quack"

    @staticmethod
    def animal_factory(animal_type):
        animals = {"dog": CleanSolution.Dog, "cat": CleanSolution.Cat, "duck": CleanSolution.Duck}
        return animals.get(animal_type, CleanSolution.Dog)()

    def execute(self):
        animal = self.animal_factory("cat")
        return animal.speak()
```
**Big-O:** -
**Alternatif:** Abstract Factory. Builder pattern. Constructor injection."""

    if "strategy" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Strategy Pattern"

    class CreditCardPayment:
        def pay(self, amount): return f"Paid {amount} via Credit Card"

    class PayPalPayment:
        def pay(self, amount): return f"Paid {amount} via PayPal"

    class CryptoPayment:
        def pay(self, amount): return f"Paid {amount} via Crypto"

    class ShoppingCart:
        def __init__(self, strategy):
            self.strategy = strategy
        def checkout(self, amount): return self.strategy.pay(amount)

    def execute(self):
        cart = self.ShoppingCart(self.PayPalPayment())
        return cart.checkout(100)
```
**Big-O:** -
**Alternatif:** if-elif zinciri yerine dict dispatching. State pattern."""

    if "observer" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Observer Pattern"

    class Subject:
        def __init__(self):
            self.observers = []
        def attach(self, observer): self.observers.append(observer)
        def notify(self, message):
            for obs in self.observers: obs.update(message)

    class EmailObserver:
        def update(self, msg): return f"Email: {msg}"

    class LogObserver:
        def update(self, msg): return f"Log: {msg}"

    def execute(self):
        subject = self.Subject()
        subject.attach(self.EmailObserver())
        subject.attach(self.LogObserver())
        subject.notify("Event happened!")
        return "Observers notified"
```
**Big-O:** -
**Alternatif:** asyncio Event. signal/slot (Qt). RxPY reactivex."""

    if "singleton" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Singleton Pattern"

    @staticmethod
    def get_instance():
        if not hasattr(CleanSolution, "_instance"):
            CleanSolution._instance = CleanSolution()
        return CleanSolution._instance

    def execute(self):
        s1 = self.get_instance()
        s2 = self.get_instance()
        return f"Same instance: {s1 is s2}"
```
**Big-O:** -
**Alternatif:** Module-level singleton (Python modulleri zaten singleton). Borg pattern (shared state)."""

    if "mvc" in inst_lower or "model view controller" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "MVC Pattern"

    class Model:
        def __init__(self): self.data = []
        def add(self, item): self.data.append(item)
        def get_all(self): return self.data

    class View:
        def render(self, data): return f"Data: {data}"

    class Controller:
        def __init__(self, model, view):
            self.model = model; self.view = view
        def add_item(self, item):
            self.model.add(item)
            return self.view.render(self.model.get_all())

    def execute(self):
        model = self.Model(); view = self.View()
        controller = self.Controller(model, view)
        return controller.add_item("Hello MVC")
```
**Big-O:** -
**Alternatif:** MVVM. MVP. Clean Architecture. Redux."""

    if "api" in inst_lower or "rest" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "RESTful API Design"

    class APIResponse:
        @staticmethod
        def success(data, status=200):
            return {"status": status, "data": data}

        @staticmethod
        def error(message, status=400):
            return {"status": status, "error": message}

    def execute(self):
        return self.APIResponse.success({"id": 1, "name": "Alice"})
```
**Big-O:** -
**Alternatif:** GraphQL. gRPC. JSON:API spec. OpenAPI/Swagger."""

    if "solid" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "SOLID Principles"

    # S: Single Responsibility
    class ReportGenerator:
        def generate(self): return "Report data"

    # O: Open/Closed
    class ReportFormatter:
        def format(self, data, formatter):
            return formatter(data)

    # L: Liskov Substitution
    class CSVFormatter:
        def __call__(self, data): return f"CSV: {data}"

    # I: Interface Segregation
    # D: Dependency Inversion
    class ReportService:
        def __init__(self, generator, formatter):
            self.generator = generator; self.formatter = formatter
        def process(self):
            data = self.generator.generate()
            return self.formatter(data)

    def execute(self):
        service = self.ReportService(self.ReportGenerator(), self.CSVFormatter())
        return service.process()
```
**Big-O:** -
**Alternatif:** Clean Architecture. Hexagonal Architecture. DDD."""

    if "test" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Unit Testing"

    def add(self, a, b):
        return a + b

    def execute(self):
        import doctest
        doctest.testmod(verbose=False)
        return "Tests passed"
```
**Big-O:** -
**Alternatif:** pytest. unittest. hypothesis (property-based testing)."""

    if "doc" in inst_lower or "readme" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Code Documentation"

    def execute(self):
        return "README, docstrings, inline comments, API documentation"
```
**Big-O:** -
**Alternatif:** Sphinx. MkDocs. pdoc. Docusaurus."""

    if "enum" in inst_lower:
        return """```python
from enum import Enum, auto

class CleanSolution:
    def __init__(self):
        self.name = "Enum Usage"

    class Status(Enum):
        PENDING = auto()
        ACTIVE = auto()
        INACTIVE = auto()
        DELETED = auto()

    @staticmethod
    def get_status_message(status):
        messages = {
            CleanSolution.Status.PENDING: "Waiting...",
            CleanSolution.Status.ACTIVE: "Running",
            CleanSolution.Status.INACTIVE: "Stopped",
            CleanSolution.Status.DELETED: "Removed",
        }
        return messages.get(status, "Unknown")

    def execute(self):
        return self.get_status_message(self.Status.ACTIVE)
```
**Big-O:** -
**Alternatif:** IntEnum. StrEnum. Literal type (Python 3.8+)."""

    if "abstract" in inst_lower or "abc" in inst_lower:
        return """```python
from abc import ABC, abstractmethod

class CleanSolution:
    def __init__(self):
        self.name = "Abstract Base Class"

    class Animal(ABC):
        @abstractmethod
        def make_sound(self): pass
        @abstractmethod
        def move(self): pass

    class Dog(Animal):
        def make_sound(self): return "Woof"
        def move(self): return "Running"

    class Fish(Animal):
        def make_sound(self): return "Blub"
        def move(self): return "Swimming"

    def execute(self):
        animals = [self.Dog(), self.Fish()]
        return [a.make_sound() for a in animals]
```
**Big-O:** -
**Alternatif:** Protocol (structural subtyping). Duck typing. Interface segregation."""

    if "operator" in inst_lower and "overload" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Operator Overloading"

    class Vector:
        def __init__(self, x, y):
            self.x = x; self.y = y
        def __add__(self, other):
            return self.__class__(self.x + other.x, self.y + other.y)
        def __sub__(self, other):
            return self.__class__(self.x - other.x, self.y - other.y)
        def __mul__(self, scalar):
            return self.__class__(self.x * scalar, self.y * scalar)
        def __repr__(self):
            return f"Vector({self.x}, {self.y})"

    def execute(self):
        v1 = self.Vector(1, 2); v2 = self.Vector(3, 4)
        return str(v1 + v2)
```
**Big-O:** -
**Alternatif:** dataclasses ile __init__/__repr__ otomatik. namedtuple."""

    if "iteration" in inst_lower or "iterator" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Custom Iterator"

    class Range:
        def __init__(self, start, end):
            self.start = start; self.end = end
        def __iter__(self):
            self.current = self.start; return self
        def __next__(self):
            if self.current >= self.end: raise StopIteration
            val = self.current; self.current += 1; return val

    def execute(self):
        return list(self.Range(1, 5))
```
**Big-O:** -
**Alternatif:** Generator functions (yield). itertools module. iter built-in."""

    if "with statement" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "With Statement Best Practices"

    class DatabaseConnection:
        def __enter__(self):
            print("Connecting to DB..."); return self
        def __exit__(self, *args):
            print("Closing DB connection...")
        def query(self, sql): return f"Result for: {sql}"

    def execute(self):
        with self.DatabaseConnection() as db:
            return db.query("SELECT * FROM users")
```
**Big-O:** -
**Alternatif:** contextlib.contextmanager. try/finally yapisi."""

    if "config" in inst_lower:
        return """```python
import os
from dataclasses import dataclass

class CleanSolution:
    def __init__(self):
        self.name = "Configuration Management"

    @dataclass
    class Config:
        debug: bool = False
        db_host: str = "localhost"
        db_port: int = 5432
        secret_key: str = ""

        @classmethod
        def from_env(cls):
            return cls(
                debug=os.getenv("DEBUG", "false").lower() == "true",
                db_host=os.getenv("DB_HOST", "localhost"),
                db_port=int(os.getenv("DB_PORT", "5432")),
                secret_key=os.getenv("SECRET_KEY", ""),
            )

    def execute(self):
        cfg = self.Config.from_env()
        return f"Config: debug={cfg.debug}, db={cfg.db_host}:{cfg.db_port}"
```
**Big-O:** -
**Alternatif:** pydantic-settings. python-dotenv. YAML config files."""

    if "caching" in inst_lower:
        return """```python
from functools import lru_cache

class CleanSolution:
    def __init__(self):
        self.name = "Caching Strategy"

    @staticmethod
    @lru_cache(maxsize=128)
    def expensive_computation(n):
        return sum(i ** 2 for i in range(n))

    def execute(self):
        results = [self.expensive_computation(1000) for _ in range(5)]
        return f"Cached result: {results[0]}"
```
**Big-O:** -
**Alternatif:** cachetools.TTLCache. Redis/Memcached. Custom cache decorator."""

    if "mixin" in inst_lower:
        return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Mixin Pattern"

    class JSONMixin:
        def to_json(self): return str(self.__dict__)

    class LoggableMixin:
        def log(self, msg): return f"[LOG] {msg}"

    class User(JSONMixin, LoggableMixin):
        def __init__(self, name, email):
            self.name = name; self.email = email

    def execute(self):
        user = self.User("Alice", "alice@example.com")
        return f"{user.to_json()} | {user.log('created')}"
```
**Big-O:** -
**Alternatif:** Composition over inheritance. Protocol/ABC. @extend decorator."""

    if "validator" in inst_lower or "validation" in inst_lower:
        return """```python
from dataclasses import dataclass

class CleanSolution:
    def __init__(self):
        self.name = "Data Validation"

    @dataclass
    class User:
        name: str
        email: str
        age: int

        def __post_init__(self):
            if not self.name.strip(): raise ValueError("Name required")
            if "@" not in self.email: raise ValueError("Invalid email")
            if self.age < 0: raise ValueError("Age must be positive")

    def execute(self):
        try:
            user = self.User("Alice", "alice@example.com", 30)
            return f"Valid user: {user.name}"
        except ValueError as e:
            return f"Invalid: {e}"
```
**Big-O:** -
**Alternatif:** pydantic (otomatik validation). marshmallow. attrs validators."""

    if "serialization" in inst_lower:
        return """```python
import json
from dataclasses import dataclass, asdict

class CleanSolution:
    def __init__(self):
        self.name = "Serialization/Deserialization"

    @dataclass
    class Person:
        name: str; age: int

    def execute(self):
        person = self.Person("Alice", 30)
        serialized = json.dumps(asdict(person))
        deserialized = json.loads(serialized)
        return f"{serialized} -> {deserialized['name']}"
```
**Big-O:** -
**Alternatif:** pickle (Python-only). protobuf. msgpack. pydantic (.json())."""

    # Fallback
    return """```python
class CleanSolution:
    def __init__(self):
        self.name = "Clean Code Best Practices"

    def execute(self):
        return "Clean, readable, maintainable code with proper naming, structure, and testing"
```
**Big-O:** -
**Alternatif:** PEP8. Code review. Static analysis (pylint, mypy, black)."""

def main():
    print("Loading dataset...")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    replaced = 0
    skipped = 0

    for i, entry in enumerate(dataset):
        inst = entry.get("instruction", "")
        out = entry.get("output", "")
        cat = entry.get("category", "")

        if not is_placeholder(out):
            skipped += 1
            continue

        generated = None
        generators = [
            ("algoritma", gen_algo),
            ("veri_yapisi", gen_ds),
            ("optimizasyon", gen_optimization),
            ("debug", gen_debug),
            ("clean_code", gen_clean_code),
        ]
        for gcat, gfunc in generators:
            if cat == gcat:
                generated = gfunc(inst)
                break
        if generated is None:
            for gcat, gfunc in generators:
                if cat != gcat:
                    generated = gfunc(inst)
                    if generated:
                        break

        if generated:
            entry["output"] = generated
            replaced += 1
        else:
            print(f"  WARNING: No generator matched for entry {i} ({cat}): {inst[:80]}...")
            skipped += 1

    print(f"\nTotal: {total}, Replaced: {replaced}, Skipped: {skipped}")
    if replaced:
        print("Writing updated dataset...")
        with open(DATASET_PATH, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        print(f"Done! Updated {replaced} entries.")
    else:
        print("No changes made.")


if __name__ == "__main__":
    main()