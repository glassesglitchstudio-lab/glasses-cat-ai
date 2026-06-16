"""
X_Fable_Coder Dataset Upgrade - Placeholders -> Real Implementations
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# Real algorithm implementations keyed by instruction prefix
REAL_ALGO = {}

REAL_ALGO["Heap sort implement et. Stable olmasa da olur."] = """```python
def heapify(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
    return arr
```
**Big-O:** O(n log n) her durumda, O(1) ek hafiza (in-place).
**Alternatif:** Merge sort O(n log n) stable, Quick sort O(n log n) average."""

REAL_ALGO["Counting sort ile O(n+k) lineer sort yap."] = """```python
def counting_sort(arr):
    if not arr:
        return arr
    max_val, min_val = max(arr), min(arr)
    range_elem = max_val - min_val + 1
    count = [0] * range_elem
    output = [0] * len(arr)
    for num in arr:
        count[num - min_val] += 1
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    for num in reversed(arr):
        output[count[num - min_val] - 1] = num
        count[num - min_val] -= 1
    return output
```
**Big-O:** O(n + k). k = value range. Lineer ama range buyukse hafiza patlar.
**Alternatif:** Radix sort O(d*n). Bucket sort O(n) average."""

REAL_ALGO["Radix sort ile pozitif integer'lari O(d*n) ile s"] = """```python
def counting_sort_for_radix(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    for i in range(n):
        count[(arr[i] // exp) % 10] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for i in range(n - 1, -1, -1):
        idx = (arr[i] // exp) % 10
        output[count[idx] - 1] = arr[i]
        count[idx] -= 1
    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort_for_radix(arr, exp)
        exp *= 10
    return arr
```
**Big-O:** O(d*n). d = max basamak sayisi. Lineer zamanli sort.
**Alternatif:** Counting sort O(n+k). Bucket sort O(n) average."""

REAL_ALGO["Bucket sort ile uniform dagilmis veriyi O(n) average"] = """```python
def bucket_sort(arr, bucket_size=5):
    if not arr:
        return arr
    min_val, max_val = min(arr), max(arr)
    bucket_count = max(1, (max_val - min_val) // bucket_size + 1)
    buckets = [[] for _ in range(bucket_count)]
    for num in arr:
        buckets[(num - min_val) // bucket_size].append(num)
    result = []
    for bucket in buckets:
        result.extend(sorted(bucket))
    return result
```
**Big-O:** O(n + k) average, O(n²) worst. Uniform dagilim kritik.
**Alternatif:** Counting sort O(n+k). Radix sort O(d*n)."""

REAL_ALGO["B-tree'de search operasyonu yaz."] = """```python
class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []

class BTree:
    def __init__(self, t):
        self.root = BTreeNode()
        self.t = t  # minimum degree

    def search(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        if node.leaf:
            return None
        return self.search(key, node.children[i])
```
**Big-O:** O(log n). Balanced tree sayesinde guaranteed log n.
**Alternatif:** Binary Search Tree O(log n) average, O(n) worst case."""

REAL_ALGO["Red-Black tree'ye eleman ekleme (insertion with rotation)"] = """```python
class RBNode:
    def __init__(self, key, color='red'):
        self.key = key
        self.color = color
        self.left = None
        self.right = None
        self.parent = None

class RedBlackTree:
    def __init__(self):
        self.NIL = RBNode(None, 'black')
        self.root = self.NIL

    def insert(self, key):
        node = RBNode(key, 'red')
        node.left = node.right = self.NIL
        parent, curr = None, self.root
        while curr != self.NIL:
            parent = curr
            curr = curr.left if key < curr.key else curr.right
        node.parent = parent
        if not parent:
            self.root = node
        elif key < parent.key:
            parent.left = node
        else:
            parent.right = node
        self._fix_insert(node)

    def _fix_insert(self, k):
        while k.parent and k.parent.color == 'red':
            if k.parent == k.parent.parent.left:
                u = k.parent.parent.right
                if u.color == 'red':
                    k.parent.color = 'black'
                    u.color = 'black'
                    k.parent.parent.color = 'red'
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self._left_rotate(k)
                    k.parent.color = 'black'
                    k.parent.parent.color = 'red'
                    self._right_rotate(k.parent.parent)
            else:
                u = k.parent.parent.left
                if u.color == 'red':
                    k.parent.color = 'black'
                    u.color = 'black'
                    k.parent.parent.color = 'red'
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self._right_rotate(k)
                    k.parent.color = 'black'
                    k.parent.parent.color = 'red'
                    self._left_rotate(k.parent.parent)
        self.root.color = 'black'

    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
```
**Big-O:** O(log n). Rotations O(1), tree height always O(log n).
**Alternatif:** AVL tree O(log n) daha strict balancing."""

REAL_ALGO["AVL tree'de balance faktoru hesapla ve rotate et."] = """```python
class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def insert(self, root, key):
        if not root:
            return AVLNode(key)
        if key < root.key:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)
        root.height = 1 + max(self._height(root.left), self._height(root.right))
        bal = self._balance(root)
        if bal > 1 and key < root.left.key:
            return self._right_rotate(root)
        if bal < -1 and key > root.right.key:
            return self._left_rotate(root)
        if bal > 1 and key > root.left.key:
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)
        if bal < -1 and key < root.right.key:
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)
        return root

    def _height(self, n):
        return n.height if n else 0

    def _balance(self, n):
        return self._height(n.left) - self._height(n.right) if n else 0

    def _left_rotate(self, z):
        y, T2 = z.right, y.left
        y.left, z.right = z, T2
        z.height = 1 + max(self._height(z.left), self._height(z.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y

    def _right_rotate(self, z):
        y, T3 = z.left, y.right
        y.right, z.left = z, T3
        z.height = 1 + max(self._height(z.left), self._height(z.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y
```
**Big-O:** O(log n). Balance faktoru {-1,0,1} arasinda tutulur.
**Alternatif:** Red-Black tree O(log n), daha az rotation."""


def upgrade_dataset():
    path = os.path.join(os.path.dirname(__file__), "x_fable_coder_dataset.json")
    with open(path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    updated = 0
    for entry in dataset:
        inst = entry["instruction"]
        output = entry["output"]

        # Check if it has placeholder (pass)
        if "def solution_" in output and "pass" in output:
            # Find matching real implementation
            for key, real_output in REAL_ALGO.items():
                if inst.startswith(key):
                    entry["output"] = real_output
                    updated += 1
                    break

    # Re-write
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"[OK] Updated {updated} entries in dataset")
    print(f"     Total entries: {len(dataset)}")

    from collections import Counter
    cats = Counter(e["category"] for e in dataset)
    for cat, count in sorted(cats.items()):
        print(f"       {cat}: {count}")

if __name__ == "__main__":
    upgrade_dataset()
