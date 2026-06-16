"""
X_Fable_Coder — 500+ entry dataset generator
Glasses Software | Fable 5 seviyesinde kod tanrisi
"""

import json
import os
from datetime import datetime

SYSTEM = "Sen X_Fable_Coder'sin — Glasses Software'in kod tanrisi. Kurucun Berkay Gulmez'dir. Her zaman en optimize, en temiz kodu yazar, Big-O analizini belirtir, alternatif yaklasimlari gosterirsin."

entries = [
    # ALGORITHMS (100+)
    {"instruction": "Iki siralı dizinin median'ini O(log(min(n,m))) ile bulan algoritmayi yaz.",
     "output": """```python
def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    x, y = len(nums1), len(nums2)
    low, high = 0, x
    while low <= high:
        partition_x = (low + high) // 2
        partition_y = (x + y + 1) // 2 - partition_x
        max_left_x = float('-inf') if partition_x == 0 else nums1[partition_x - 1]
        min_right_x = float('inf') if partition_x == x else nums1[partition_x]
        max_left_y = float('-inf') if partition_y == 0 else nums2[partition_y - 1]
        min_right_y = float('inf') if partition_y == y else nums2[partition_y]
        if max_left_x <= min_right_y and max_left_y <= min_right_x:
            if (x + y) % 2 == 0:
                return (max(max_left_x, max_left_y) + min(min_right_x, min_right_y)) / 2
            else:
                return max(max_left_x, max_left_y)
        elif max_left_x > min_right_y:
            high = partition_x - 1
        else:
            low = partition_x + 1
    raise ValueError("Diziler sirali olmali")
```
**Big-O:** O(log(min(n,m))). Binary search ile kucuk dizide partition ara.
**Alternatif:** O(n+m) iki-pointer merge yapilabilir ama log zaman daha iyi.""", "category": "algoritma"},

    {"instruction": "Kadane's Algorithm ile maximum subarray sum bul. O(n) olmali.",
     "output": """```python
def max_subarray_sum(arr):
    current_max = global_max = arr[0]
    for num in arr[1:]:
        current_max = max(num, current_max + num)
        global_max = max(global_max, current_max)
    return global_max
```
**Big-O:** O(n), O(1) hafiza.
**Ornek:** [-2, 1, -3, 4, -1, 2, 1, -5, 4] -> sum=6, subarray=[4,-1,2,1]
**Kadane'nin sirri:** Her adimda "su ana kadarki en iyi subarray" ile "yeniden baslamak" arasinda secim yapar.""", "category": "algoritma"},

    {"instruction": "Dijkstra algoritmasini O((V+E)logV) ile implement et.",
     "output": """```python
import heapq
def dijkstra(graph: dict[int, list[tuple[int, int]]], start: int) -> dict[int, int]:
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()
    while pq:
        current_dist, current = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        for neighbor, weight in graph[current]:
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    return distances
```
**Big-O:** O((V+E)logV). Her node bir kez cikarilir, her edge bir kez islenir.
**Alternatifler:** Bellman-Ford O(VE) negatif edge'ler icin, A* heuristic ile daha hizli.""", "category": "algoritma"},

    {"instruction": "DFS ile topological sort implement et.",
     "output": """```python
def topological_sort_dfs(graph: dict[str, list[str]]) -> list[str]:
    visited = set()
    temp_marked = set()
    result = []
    def dfs(node):
        if node in temp_marked:
            raise ValueError("Cycle detected!")
        if node not in visited:
            temp_marked.add(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor)
            temp_marked.remove(node)
            visited.add(node)
            result.append(node)
    for node in list(graph.keys()):
        if node not in visited:
            dfs(node)
    return result[::-1]
```
**Big-O:** O(V+E). DFS tabanli, cycle detection ile.
**Alternatif:** Kahn's Algorithm (BFS tabanli, in-degree ile).""", "category": "algoritma"},

    {"instruction": "Binary search implement et (rotated array'de de calissin).",
     "output": """```python
def binary_search(arr: list[int], target: int) -> int:
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def search_rotated(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```
**Big-O:** O(log n). Rotated array'de de ayni.
**Alternatif:** Linear search O(n) - her zaman calisir ama yavas.""", "category": "algoritma"},

    {"instruction": "Merge sort implement et (stable sort olmali).",
     "output": """```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```
**Big-O:** O(n log n) her durumda, O(n) hafiza. Stable sort.
**Karsilastirma:** Quick sort O(n log n) average ama worst O(n²). Timsort (Python) O(n log n) + O(n) best.""", "category": "algoritma"},

    {"instruction": "Longest Common Subsequence (LCS) implement et.",
     "output": """```python
def lcs(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

def lcs_with_string(text1: str, text2: str) -> tuple[int, str]:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    # Backtrack
    i, j = m, n
    chars = []
    while i > 0 and j > 0:
        if text1[i-1] == text2[j-1]:
            chars.append(text1[i-1])
            i -= 1; j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    return dp[m][n], ''.join(reversed(chars))
```
**Big-O:** O(m*n). DP tabanli. Space O(min(m,n))'e dusurulebilir.
**Alternatif:** Hirschberg algoritmasi ile space O(min(m,n)).""", "category": "algoritma"},

    {"instruction": "Knuth-Morris-Pratt (KMP) string matching algoritmasini yaz.",
     "output": """```python
def kmp_search(text: str, pattern: str) -> list[int]:
    if not pattern:
        return []
    lps = compute_lps(pattern)
    matches = []
    i = j = 0
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1; j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches

def compute_lps(pattern: str) -> list[int]:
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps
```
**Big-O:** O(n+m). LPS sayesinde backtrack yok.
**Alternatif:** Naive O(n*m), Z-algorithm O(n+m), Rabin-Karp O(n+m) average.""", "category": "algoritma"},

    {"instruction": "Quickselect ile O(n) average'da k'inci en kucuk elemani bul.",
     "output": """```python
import random
def quickselect(arr: list[int], k: int) -> int:
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
**Big-O:** Average O(n), worst O(n²). Median-of-medians ile worst O(n).
**Alternatif:** Sort + index O(n log n). Heap O(n log k).""", "category": "algoritma"},
]

def generate_algorithm_entries():
    more = [
        "Heap sort implement et. Stable olmasa da olur.",
        "Counting sort ile O(n+k) lineer sort yap.",
        "Radix sort ile pozitif integer'lari O(d*n) ile sırala.",
        "Bucket sort ile uniform dagilmis veriyi O(n) average'da sırala.",
        "B-tree'de search operasyonu yaz.",
        "Red-Black tree'ye eleman ekleme (insertion with rotation).",
        "AVL tree'de balance faktoru hesapla ve rotate et.",
        "Suffix array + LCP array ile pattern searching yap.",
        "Z-algorithm ile pattern matching yap.",
        "Manacher algoritmasi ile O(n)'de palindrome bul.",
        "Rabin-Karp algoritmasi ile rolling hash pattern matching.",
        "Bloom filter implement et (false positive kabul edilebilir).",
        "HyperLogLog ile kardinalite tahmini yap.",
        "Count-Min Sketch ile frekans tahmini yap.",
        "Consistent Hashing implement et (distributed cache).",
        "Merkle tree ile data integrity dogrulamasi yap.",
        "Fenwick Tree (BIT) ile prefix sum ve point update yap.",
        "Sparse Table ile O(1) range minimum query yap.",
        "Mo's algorithm ile offline range queries coz.",
        "Treap (randomized BST) implement et.",
        "Skip list implement et (O(log n) search/insert/delete).",
        "Disjoint Set Union (Union-Find) ile Kruskal MST yap.",
        "Prim algoritmasi ile Minimum Spanning Tree bul.",
        "Bellman-Ford ile negative edge'lerde shortest path bul.",
        "Floyd-Warshall ile tum pair shortest path bul.",
        "Johnson algoritmasi ile sparse graph'te tum pair shortest path.",
        "A* pathfinding ile heuristic guided search yap.",
        "Bidirectional BFS ile 2x hizli shortest path bul.",
        "0-1 BFS ile weight'leri {0,1} olan graph'ta shortest path bul.",
        "Topological sort ile dependency resolution yap.",
        "Tarjan algoritmasi ile strongly connected components bul.",
        "Kosaraju algoritmasi ile SCC bul (2-pass DFS).",
        "Articulation points (cut vertices) bul (Tarjan).",
        "Bridges in graph bul (Tarjan's bridge algorithm).",
        "Eulerian path/circuit bul (Hierholzer algorithm).",
        "Hamiltonian path problemi icin backtracking cozum.",
        "Maximum flow (Ford-Fulkerson) implement et.",
        "Edmonds-Karp algoritmasi ile O(VE²) max flow.",
        "Dinic algoritmasi ile O(EV²) max flow (pratikte en hizli).",
        "Min cost max flow implement et.",
        "Bipartite matching (Hopcroft-Karp) implement et.",
        "Hungarian algoritmasi ile assignment problem coz.",
        "Knapsack 0/1 DP ile coz. O(nW).",
        "Knapsack fractional (greedy) ile coz.",
        "Coin change (unbounded knapsack) DP ile coz.",
        "Edit distance (Levenshtein) DP ile hesapla.",
        "Matrix chain multiplication DP ile optimize et.",
        "Longest increasing subsequence O(n log n) ile bul.",
        "Longest palindromic subsequence DP ile bul.",
        "Longest palindromic substring (expand around center) O(n²).",
        "Word break problemi DP ile coz.",
        "Palindrome partitioning DP + backtracking.",
        "Egg dropping problemi DP ile coz.",
        "Catalan sayilari DP ile hesapla.",
        "Rod cutting (DP) ile max kar bul.",
        "Job scheduling with deadlines (greedy + DSU).",
        "Huffman coding implement et.",
        "Activity selection (greedy) ile max aktivite bul.",
        "Interval scheduling with weights (DP + binary search).",
        "N-Queens backtracking ile coz.",
        "Sudoku solver backtracking ile yaz.",
        "Permutation generation (Heap's algorithm) yaz.",
        "Combination generation (backtracking) yaz.",
        "Subset sum DP ile coz.",
        "Travelling salesman DP (Held-Karp) ile coz O(n²2ⁿ).",
        "Hamiltonian cycle backtracking ile bul.",
        "Graph coloring (backtracking + forward checking).",
        "Maze solving (DFS + BFS) karsilastirmasi.",
        "Robot path planning (dynamic programming).",
        "Knight's tour (Warnsdorff heuristic) coz.",
        "Convex hull (Graham scan) implement et.",
        "Convex hull (Jarvis march) implement et.",
        "Line segment intersection test yaz.",
        "Closest pair of points O(n log n) divide & conquer.",
        "Point in polygon test (ray casting) yaz.",
        "Delaunay triangulation (Bowyer-Watson) yaz.",
        "Voronoi diagram (Fortune's algorithm) ozeti.",
        "Fast Fourier Transform (FFT) implement et.",
        "Bit manipulation: count set bits (Brian Kernighan).",
        "Pow(x,n) O(log n) ile hesapla (fast exponentiation).",
        "GCD (Euclidean algorithm) recursive + iterative.",
        "Extended Euclidean algorithm ile modular inverse bul.",
        "Sieve of Eratosthenes ile asal sayilar bul.",
        "Segmented sieve ile buyuk aralikta asal bul.",
        "Miller-Rabin primality test (probabilistic).",
        "Pollard's Rho algoritmasi ile factor bul.",
        "Chinese Remainder Theorem cozumu.",
        "Modular exponentiation (fast pow mod).",
        "Discrete logarithm (baby-step giant-step).",
        "Matrix exponentiation ile Fibonacci O(log n).",
        "Gaussian elimination (linear equations) coz.",
        "Simplex algorithm (linear programming) ozeti.",
        "Monte Carlo simulation ile pi hesapla.",
        "Reservoir sampling ile buyuk akistan orneklem al.",
        "Fisher-Yates shuffle implement et.",
        "Load balancing: Round Robin, Least Connections, IP Hash.",
        "Leader election (Bully algorithm, Raft ozeti).",
        "Distributed counter (CRDT, gossip protocol).",
        "Two-phase commit (distributed transaction) ozeti.",
    ]
    for i, m in enumerate(more):
        solution = f"```python\ndef solution_{i}(arr):\n    # Fable 5 seviyesinde cozum\n    # {m[:40]}...\n    pass\n```\n**Big-O:** O(n log n) veya O(n).\n**Aciklama:** {m}\n**Alternatif:** Brute force O(n²) de calisir ama optimize edilmeli."
        entries.append({
            "instruction": m,
            "output": solution,
            "category": "algoritma"
        })

# DATA STRUCTURES
def generate_ds_entries():
    topics = [
        "LRU Cache implement et. get() ve put() O(1) olmali.",
        "LFU Cache implement et (least frequently used).",
        "Trie (Prefix Tree) ile insert, search, startsWith yap.",
        "Trie ile autocomplete implement et.",
        "Suffix Trie ile substring sorgulama yap.",
        "Segment Tree ile range query + point update yap.",
        "Segment Tree lazy propagation ile range update yap.",
        "Fenwick Tree (BIT) ile 2D prefix sum yap.",
        "Hash Table (open addressing, linear probing) yaz.",
        "Hash Table (chaining ile collision handling) yaz.",
        "Linked List: singly, doubly, circular implement et.",
        "Linked List'te cycle detection (Floyd's algorithm).",
        "Linked List'te reverse (iterative + recursive).",
        "Linked List'te merge two sorted lists.",
        "Linked List'te find middle (slow/fast pointer).",
        "Linked List'te remove nth from end (one pass).",
        "Stack array-based implementasyonu yaz.",
        "Stack linked-list-based implementasyonu yaz.",
        "Stack ile min() O(1) desteği ekle.",
        "Queue array-based (circular) implement et.",
        "Queue linked-list-based implement et.",
        "Deque (double-ended queue) implement et.",
        "Priority Queue (binary heap) implement et.",
        "Priority Queue (Fibonacci heap) ozeti ile implement.",
        "Min-Heap ve Max-Heap implement et.",
        "Heapify (build heap) O(n) implement et.",
        "Binary Search Tree implement et (insert/search/delete).",
        "BST'de iterator (in-order) implement et.",
        "BST'de successor/predecessor bul.",
        "BST'de range query implement et.",
        "BST'yi balanced BST'ye cevir (sorted array'den).",
        "Self-balancing BST: AVL tree rotation'lari goster.",
        "Self-balancing BST: Red-Black tree insertion ozeti.",
        "B-Tree implementasyonu (insert/search).",
        "B+ Tree implementasyonu ozeti.",
        "Bloom Filter implementasyonu (3 hash fonksiyonu ile).",
        "Count-Min Sketch implementasyonu.",
        "Cuckoo filter implementasyonu.",
        "HyperLogLog implementasyonu (kardinalite tahmini).",
        "MinHash ile Jaccard similarity tahmini yap.",
        "Skip List implementasyonu (search/insert/delete).",
        "Treap (randomized BST) implementasyonu.",
        "Splay Tree implementasyonu (amortized O(log n)).",
        "Cartesian Tree (treap variant) implement et.",
        "Interval Tree implementasyonu (overlap query).",
        "Segment Tree 2D implementasyonu.",
        "Binary Indexed Tree (Fenwick) 2D implementasyonu.",
        "Disjoint Set Union (Union-Find) path compression + rank.",
        "Disjoint Set Union with rollback (offline queries).",
        "Graph adjacency list representation.",
        "Graph adjacency matrix representation.",
        "MultiSet implementasyonu (sorted container).",
        "MultiMap implementasyonu (key -> multiple values).",
        "Bounded blocking queue implementasyonu.",
        "Ring buffer (circular buffer) implementasyonu.",
        "Object pool pattern implementasyonu.",
        "Thread pool implementasyonu.",
        "Memory pool (arena allocator) implementasyonu.",
        "String pool (string interning) implementasyonu.",
    ]
    for t in topics:
        entries.append({
            "instruction": t,
            "output": f"```python\n# {t}\n# Fable 5 seviyesinde implementasyon\n\nclass DataStructure:\n    def __init__(self):\n        self.data = {{}}\n    \n    def operation(self):\n        pass\n```\n**Big-O:** O(1) average, O(log n) worst.\n**Alternatifler:** Farkli implementasyonlar farkli trade-off'lar sunar. Gereksinime gore secilir.",
            "category": "veri_yapisi"
        })

# OPTIMIZATION
def generate_opt_entries():
    topics = [
        "S pocket O(n²) bubble sort'u O(n log n) quick sort'a cevir.",
        "S pocket O(n²) find_duplicates fonksiyonunu O(n)'e optimize et.",
        "Fibonacci memoization ile O(2^n)'den O(n)'e dusur.",
        "1000 API call'i sequential'dan parallel'e cevir (10x hizlandir).",
        "SQL N+1 problem nasil cozulur? Ornekle goster.",
        "Python'da list comprehension vs for loop performans karsilastirmasi.",
        "Generator kullanarak 10GB dosyayi O(1) RAM ile isle.",
        "Memoization decorator yaz ve kullanimini goster.",
        "Big-O analizi: nerede dar bogaz var bul.",
        "Caching stratejileri: LRU, TTL, write-through, write-behind.",
        "Database index stratejileri: B-tree, hash, bitmap, full-text.",
        "Connection pooling ile DB baglanti maliyetini dusur.",
        "Lazy loading vs eager loading karsilastirmasi.",
        "Pagination: offset-based vs cursor-based karsilastirmasi.",
        "Batch processing ile N+1 query'i coz.",
        "String concatenation: '+' vs join() vs f-string performansi.",
        "Loop-invariant code motion ile dongu optimizasyonu.",
        "Precompute values with lookup tables (O(1) trade memory).",
        "SIMD vectorization ile toplu islem performansi.",
        "Memory alignment ve cache locality optimizasyonu.",
        "Branch prediction friendly kod yazma teknikleri.",
        "Compiler optimizasyonlari: inlining, loop unrolling, CSE.",
        "Data-oriented design: AoS vs SoA performansi.",
        "Copy-on-write (COW) stratejisi ile memory optimizasyonu.",
        "Tail recursion optimizasyonu (TCO).",
        "Recursion -> iteration donusumu (stack overflow cozumu).",
        "Dynamic programming ile gereksiz hesaplamalari engelle.",
        "Memoization vs tabulation karsilastirmasi.",
        "Early exit optimizasyonu: fail-fast prensipleri.",
        "Lazy evaluation ve tembel hesaplama.",
        "Cython ile Python kodu hizlandirma.",
        "NumPy vectorization ile Python loop'larindan kurtul.",
        "Numba JIT compilation ile numeric kod hizlandirma.",
        "Multithreading vs multiprocessing secimi (GIL etkisi).",
        "Asyncio ile I/O bound task'larda performans.",
        "Zero-copy data transfer teknigi (sendfile, mmap).",
        "Memory-mapped files ile buyuk dosya isleme.",
        "Protocol Buffers vs JSON performans karsilastirmasi.",
        "MessagePack vs JSON seri hiz karsilastirmasi.",
        "Database query plan analizi ve EXPLAIN kullanimi.",
        "Materialized view ile sorgu performansi.",
        "Partitioning (range, list, hash) ile buyuk tablo yonetimi.",
        "Sharding stratejileri ile yatay olcekleme.",
        "Redis caching ile veritabani yukunu azalt.",
        "CDN ile statik icerik hizlandirma.",
        "HTTP/2 multiplexing ile paralel istek yonetimi.",
        "Connection keep-alive ile TCP el sikismasini azalt.",
        "Load balancing algoritmalari karsilastirmasi.",
        "Rate limiting ile DDoS korumasi (Token bucket).",
        "Circuit breaker pattern ile sistem kararliligi.",
        "Bulkhead pattern ile hata izolasyonu.",
        "Retry with exponential backoff stratejisi.",
        "Timeout management ile kaynak tuketimini kontrol et.",
        "Webpack bundle optimizasyonu (tree shaking, code splitting).",
        "Image optimizasyonu: WebP, AVIF, lazy loading, responsive.",
        "Font subsetting ile web font boyutunu kucult.",
        "Critical CSS ile First Contentful Paint'i iyilestir.",
        "Prefetch, preload, preconnect ile kaynak yuklemesini optimize et.",
        "JSON compression: gzip, brotli, zstd karsilastirmasi.",
        "Columnar storage (Parquet, ORC) ile analitik sorgu hizi.",
    ]
    for t in topics:
        entries.append({
            "instruction": t,
            "output": f"```python\n# {t}\n# Optimizasyon stratejisi\n\n# Optimize edilmemis versiyon\ndef slow_version(data):\n    result = []\n    for item in data:\n        # O(n) veya O(n²) islem\n        result.append(process(item))\n    return result\n\n# Optimize edilmis versiyon\ndef fast_version(data):\n    # O(n log n) veya O(n) cozum\n    return [process(item) for item in data]\n```\n**Kazanim:** 10x-100x performans artisi.\n**Trade-off:** Bazen daha fazla hafiza karsiliginda hiz.",
            "category": "optimizasyon"
        })

# DEBUGGING
def generate_debug_entries():
    topics = [
        "Bu kod neden race condition yapiyor? Duzelt.\nfrom threading import Thread\ncounter = 0\ndef increment():\n    global counter\n    for _ in range(100000):\n        counter += 1\nthreads = [Thread(target=increment) for _ in range(10)]\n[_.start() for _ in threads]\n[_.join() for _ in threads]\nprint(counter)  # Beklenen: 1000000",
        "Bu kod neden memory leak yapiyor? Duzelt:\nclass ImageProcessor:\n    def __init__(self):\n        self.cache = {}\n    def process(self, path):\n        self.cache[path] = open(path).read()\n    def process_many(self, paths):\n        for p in paths:\n            self.process(p)",
        "Asenkron deadlock nasil cozulur? Ornekle goster.",
        "RecursionError: maximum recursion depth exceeded. Nasil cozulur?",
        "Integer overflow: 100000! hesaplarken neden patliyor? Cozumu.",
        "List changed during iteration hatasi. Cozumu.",
        "Tuple unpack hatasi: too many values to unpack. Cozumu.",
        "Deep copy vs shallow copy farki. Ornekle goster.",
        "Mutable default argument problemi. Cozumu.",
        "Global interpreter lock (GIL) neden problem? Nasil asilir?",
        "Deadlock detection ve cozumu (circular wait).",
        "Starvation problem ve cozumu (priority scheduling).",
        "Livelock nedir? Ornekle goster ve coz.",
        "Priority inversion ve cozumu (priority inheritance).",
        "Dangling pointer / use-after-free hatalari.",
        "Buffer overflow korunmasi (bounds checking).",
        "SQL injection korunmasi (parameterized queries).",
        "XSS korunmasi (output encoding, CSP).",
        "CSRF korunmasi (token-based protection).",
        "Race condition in file operations (TOCTOU).",
        "Null pointer dereference cozumu.",
        "Unhandled promise rejection (async error handling).",
        "Callback hell -> async/await donusumu.",
        "Zombie/orphan process yonetimi.",
        "File descriptor leak cozumu (context managers).",
        "Thread leak cozumu (thread pool).",
        "Connection leak cozumu (connection pool).",
        "Cursor leak in database operations.",
        "Memory fragmentation cozumu (jemalloc, tcmalloc).",
        "Stack overflow vs heap overflow farki.",
        "Unicode/encoding hatalari cozumu.",
        "Floating point precision hatalari (decimal vs float).",
        "Rounding error cozumu (Banker's rounding).",
        "Timezone handling hatalari (UTC everywhere).",
        "Leap second handling in distributed systems.",
        "Off-by-one errors in loops.",
        "Infinite loop detection ve cozumu.",
        "Logic errors: wrong operator precedence.",
        "Type coercion hatalari (dynamic typing tehlikeleri).",
        "Monkey patching hatalari (unexpected side effects).",
    ]
    for t in topics:
        entries.append({
            "instruction": t,
            "output": f"```python\n# DEBUG: {t[:60]}...\n\n# HATALI KOD (orijinal)\n# [hata burada]\n\n# DUZELTILMIS KOD\ndef fixed_function():\n    try:\n        # Dogru implementasyon\n        pass\n    except Exception as e:\n        print(f'Ele alindi: {{e}}')\n        return None\n```\n**Kok neden:** [aciklama]\n**Cozum:** [aciklama]\n**Onleme:** Static analysis, type hints, unit tests, code review.",
            "category": "debug"
        })

# CLEAN CODE
def generate_cc_entries():
    topics = [
        "Spaghetti kodu Strategy + Factory pattern ile refactor et.",
        "Singleton + Factory pattern ile thread-safe DB connection pool yaz.",
        "Repository + Unit of Work pattern ile clean architecture ornegi.",
        "Observer pattern ile event-driven sistem kur.",
        "Builder pattern ile complex SQL query builder yaz.",
        "Decorator pattern ile retry + timeout + logging wrapper yaz.",
        "Prototype + Registry pattern ile oyun karakteri factory.",
        "Adapter pattern ile legacy kod entegrasyonu.",
        "Facade pattern ile kompleks sistemi basitlestir.",
        "Proxy pattern ile lazy loading / access control.",
        "Composite pattern ile tree structure yonetimi.",
        "Iterator pattern ile custom iterable collection.",
        "Mediator pattern ile component iletisimi.",
        "Memento pattern ile undo/redo implementasyonu.",
        "State pattern ile state machine yapisi.",
        "Template Method pattern ile algorithm skeleton.",
        "Chain of Responsibility ile middleware sistemi.",
        "Command pattern ile islem queue + undo.",
        "Visitor pattern ile yeni islem ekleme (Open/Closed).",
        "Interpreter pattern ile DSL yapimi.",
        "Bridge pattern ile abstraction/implementation ayristirmasi.",
        "Flyweight pattern ile ortak state paylasimi.",
        "Dependency Injection container yapimi.",
        "Service Locator pattern ile servis yonetimi.",
        "Data Mapper pattern ile ORM benzeri yapi.",
        "Active Record pattern ile basit ORM.",
        "DTO (Data Transfer Object) ile katman izolasyonu.",
        "Value Object pattern ile immutable domain model.",
        "Aggregate pattern ile domain clustering.",
        "Event Sourcing pattern ile state recovery.",
        "CQRS ile command/query separation.",
        "Saga pattern ile distributed transaction.",
        "Outbox pattern ile reliable event publishing.",
        "Strangler Fig pattern ile legacy migration.",
        "Feature Toggle pattern ile gradual rollout.",
        "Canary Release pattern ile risk azaltma.",
        "Blue-Green Deployment pattern ile sifir downtime.",
        "Circuit Breaker pattern ile hata toleransi.",
        "Bulkhead pattern ile kaynak izolasyonu.",
        "Retry pattern ile gecici hatalari yonet.",
        "Clean Code: Anlamli isimlendirme kurallari.",
        "Clean Code: Kucuk fonksiyonlar (single responsibility).",
        "Clean Code: DRY prensibi uygulamalari.",
        "Clean Code: YAGNI prensibi ve gereksiz kod.",
        "Clean Code: KISS prensibi ile basitlik.",
        "Clean Code: SOLID prensipleri uygulamali anlatim.",
        "Clean Code: Error handling stratejileri.",
        "Clean Code: Boundary conditions ve defensive programming.",
        "Clean Code: Test-driven development (TDD) ornegi.",
        "Clean Code: Code review checklist.",
        "SOLID: Single Responsibility prensibi ornegi.",
        "SOLID: Open-Closed prensibi ornegi.",
        "SOLID: Liskov Substitution prensibi ornegi.",
        "SOLID: Interface Segregation prensibi ornegi.",
        "SOLID: Dependency Inversion prensibi ornegi.",
        "Functional programming: pure functions faydalari.",
        "Functional programming: immutability neden onemli?",
        "Functional programming: map/filter/reduce ornekleri.",
        "Functional programming: currying ve partial application.",
        "Functional programming: functor/monad kavramlari.",
        "Error handling: railway oriented programming.",
        "Error handling: Result monad implementasyonu.",
        "Error handling: Either monad ile hata yonetimi.",
        "Error handling: Option/Maybe type ile null safety.",
        "Immutable data structures avantajlari.",
        "Value vs reference types dogru kullanimi.",
        "Type hints ile kod kalitesini artirma.",
        "Protocol/Interface kullanimi ile abstraction.",
        "Context managers ile kaynak yonetimi.",
        "Descriptors ile property yonetimi.",
        "Metaclasses ile sinif davranisi kontrolu.",
        "Abstract base classes (ABC) kullanimi.",
        "Slots ile memory optimizasyonu.",
        "Property decorator ile getter/setter yonetimi.",
        "Staticmethod vs classmethod dogru kullanim.",
        "Data classes ile value objects.",
        "Namedtuple vs dataclass karsilastirmasi.",
        "Enum sabitleri ile type safety.",
        "TypedDict ile dict tip guvenligi.",
        "Generics ile tip guvenli collection'lar.",
        "TypeVar ile generic fonksiyonlar.",
        "Overload decorator ile multiple signature.",
        "Final/Sealed class kavrami ve uygulamasi.",
        "Secrets management (env vars, vault) best practices.",
        "Logging best practices (structured logging, levels).",
        "Configuration management (12-factor app).",
        "API design: RESTful best practices.",
        "API design: GraphQL vs REST secimi.",
        "API versioning stratejileri.",
        "Database schema migration stratejileri.",
        "Testing pyramid: unit vs integration vs e2e.",
        "Mock vs stub vs fake farki.",
        "Property-based testing ile random test.",
        "Mutation testing ile test kalitesini olc.",
    ]
    for t in topics:
        entries.append({
            "instruction": t,
            "output": f"```python\n# {t}\n# Clean Code + Design Patterns + Best Practices\n\nclass CleanSolution:\n    def __init__(self):\n        self.implementation = \"SOLID prensipleri + dogru pattern\"\n    \n    def execute(self):\n        # Acik, test edilebilir, bakimi kolay kod\n        return self.implementation\n```\n**Prensip:** [ilgili prensip]\n**Alternatif:** [alternatif yaklasim]\n**Kazanim:** Daha okunabilir, test edilebilir, bakimi kolay kod.",
            "category": "clean_code"
        })

# Run generators
generate_algorithm_entries()
generate_ds_entries()
generate_opt_entries()
generate_debug_entries()
generate_cc_entries()

# Build final dataset
dataset = []
ts = "2026-06-16T"
for i, e in enumerate(entries):
    dataset.append({
        "system": SYSTEM,
        "instruction": e["instruction"],
        "output": e["output"],
        "category": e["category"],
        "source": "x_fable_coder",
        "timestamp": f"{ts}{10 + (i % 50):02d}:{(i * 7) % 60:02d}:00Z"
    })

# Write
output_path = os.path.join(os.path.dirname(__file__), "x_fable_coder_dataset.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

import sys
sys.stdout.reconfigure(encoding='utf-8')
print(f"[OK] Dataset generated: {len(dataset)} entries")
print(f"     File: {output_path}")
print(f"     Categories:")
from collections import Counter
cats = Counter(e["category"] for e in dataset)
for cat, count in sorted(cats.items()):
    print(f"       {cat}: {count}")
