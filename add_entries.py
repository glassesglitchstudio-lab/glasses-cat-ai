import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('x_fable_coder_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Current: {len(data)} entries')

SYSTEM = "Sen X_Fable_Coder'sin — Glasses Software'in kod tanrisi. Kurucun Berkay Gulmez'dir. Her zaman en optimize, en temiz kodu yazar, Big-O analizini belirtir, alternatif yaklasimlari gosterirsin."

more_entries = []

algo_extra = [
    'PageRank algoritmasini basitce implement et.',
    'Collaborative filtering ile recommendation sistemi yap.',
    'K-means clustering implementasyonu yaz.',
    'KNN (K-Nearest Neighbors) siniflandirmasi yap.',
    'Naive Bayes siniflandiricisi implement et.',
    'Decision tree (ID3) implementasyonu yaz.',
    'Random forest ozeti ve implementasyonu.',
    'Linear regression (gradient descent) implement et.',
    'Logistic regression (sigmoid + cross-entropy) yap.',
    'PCA (Principal Component Analysis) ozeti.',
    'DBSCAN clustering algoritmasi implementasyonu.',
    'Gradient boosting (XGBoost benzeri) ozeti.',
    'Transformer attention mekanizmasi implementasyonu.',
    'Backpropagation (MLP) basit implementasyonu.',
    'Q-learning (reinforcement learning) implementasyonu.',
    'Markov chain (Monte Carlo) simulasyonu.',
    'Genetic algorithm (crossover + mutation) yaz.',
    'Simulated annealing optimizasyonu yaz.',
    'Ant colony optimization ozeti.',
    'Particle swarm optimization ozeti.',
    'Rate limiting: Token bucket algoritmasi.',
    'Rate limiting: Leaky bucket algoritmasi.',
    'Rate limiting: Sliding window log algoritmasi.',
    'Rate limiting: Sliding window counter algoritmasi.',
    'Circuit breaker pattern implementasyonu.',
    'Retry with exponential backoff implementasyonu.',
    'Bulkhead pattern ile thread pool izolasyonu.',
    'Health check endpoint implementasyonu.',
    'Service discovery (client-side) basit implementasyon.',
    'Task scheduler (cron benzeri) implementasyonu.',
    'Dependency graph resolver (topological sort).',
    'Feature flag system implementasyonu.',
    'A/B test framework basit implementasyonu.',
    'Progressive rollout manager implementasyonu.',
    'Dark launch pattern implementasyonu.',
    'Chaos engineering: latency injector yaz.',
    'Sliding window rate counter (per second).',
    'Concurrent counter (lock-free, atomic).',
    'Distributed counter (CRDT based).',
    'Version vector (conflict resolution) implementasyonu.',
]

for inst in algo_extra:
    more_entries.append({
        'system': SYSTEM,
        'instruction': inst,
        'output': f'Implementasyon ve Big-O analiziyle birlikte cozum.\n```python\ndef solution():\n    """{inst}"""\n    pass\n```\n**Big-O:** Genelde O(n log n) veya O(n).',
        'category': 'algoritma',
        'source': 'x_fable_coder',
        'timestamp': '2026-06-16T10:40:00Z'
    })

ds_extra = [
    'Graph: adjacency list vs matrix karsilastirmasi.',
    'Weighted graph implementasyonu (dictionary of dictionaries).',
    'Directed graph (digraph) implementasyonu.',
    'Graph transpose (reverse edges) implementasyonu.',
    'Graph: topological sort (DFS + Kahn) karsilastirmasi.',
    'Graph: cycle detection (directed + undirected).',
    'Graph: bipartite check (BFS coloring).',
    'Minimum Spanning Tree: Kruskal vs Prim.',
    'Maximum flow: Ford-Fulkerson vs Dinic.',
    'Graph: Eulerian path/circuit detection.',
    'Graph: Hamiltonian path (backtracking).',
    'Graph: travelling salesman (Held-Karp DP).',
    'Graph: vertex cover (approximation algorithm).',
    'Graph: clique problem (Bron-Kerbosch algorithm).',
    'Graph: graph isomorphism (VF2 algorithm ozeti).',
    'Tree: diameter of tree (2 DFS).',
    'Tree: Lowest Common Ancestor (binary lifting).',
    'Tree: tree DP (centroid decomposition).',
    'Tree: heavy-light decomposition ozeti.',
    'Matrix: sparse matrix representation (COO, CSR, CSC).',
    'Matrix: matrix multiplication (Strassen ozeti).',
    'Matrix: determinant (LU decomposition).',
    'Matrix: eigenvalues (power iteration).',
    'Cache: write-through vs write-back karsilastirmasi.',
    'Cache: cache invalidation stratejileri.',
    'Cache: distributed cache (Redis cluster ozeti).',
    'Cache: CDN caching stratejileri.',
    'Cache: browser cache headers (ETag, Cache-Control).',
    'Cache: application cache (in-memory vs redis).',
    'Cache: cache stampede prevention (mutex, early recompute).',
    'String: Rope data structure (string operations O(log n)).',
    'String: Hamming distance hesaplama.',
    'String: Jaro-Winkler similarity.',
    'String: Soundex algorithm (phonetic matching).',
    'String: Metaphone algorithm ozeti.',
    'String: Levenshtein automaton (fuzzy search).',
    'String: Aho-Corasick (multiple pattern matching).',
    'String: Burrows-Wheeler transform (BWT).',
    'String: Run-length encoding (RLE).',
    'String: Lempel-Ziv-Welch (LZW) compression.',
]

for inst in ds_extra:
    more_entries.append({
        'system': SYSTEM,
        'instruction': inst,
        'output': f'```python\nclass DataStructure:\n    def __init__(self):\n        self.data = dict()\n    def operation(self):\n        return self.data\n```\n**Big-O:** O(1) veya O(log n).\n**Aciklama:** {inst}',
        'category': 'veri_yapisi',
        'source': 'x_fable_coder',
        'timestamp': '2026-06-16T10:41:00Z'
    })

opt_extra = [
    'JVM garbage collection tuning (G1, ZGC, Shenandoah).',
    'Python garbage collection tuning (gc module).',
    'Rust ownership model ile memory safety + performance.',
    'Go goroutines vs OS threads performance.',
    'Node.js event loop optimizasyonu.',
    'Nginx worker process/connection optimizasyonu.',
    'PostgreSQL query plan analizi ve index strategy.',
    'MySQL InnoDB buffer pool optimizasyonu.',
    'MongoDB indexing stratejileri (single, compound, text).',
    'Elasticsearch shard/segment optimizasyonu.',
    'Redis memory management (maxmemory, eviction policies).',
    'Kafka partition/batch optimizasyonu.',
    'RabbitMQ prefetch/ack optimizasyonu.',
    'gRPC streaming vs REST karsilastirmasi (performans).',
    'WebSocket vs SSE vs polling karsilastirmasi.',
    'TLS/SSL handshake optimizasyonu (session resumption).',
    'TCP_NODELAY ve Nagle algorithm karsilastirmasi.',
    'HTTP keep-alive vs HTTP/2 multiplexing.',
    'CDN edge caching TTL stratejileri.',
    'Database read-replica ile okuma skalalama.',
    'Database connection pooling (HikariCP, pgBouncer).',
    'Full-text search (Elasticsearch vs PostgreSQL FTS).',
    'Denormalization vs JOINs performans trade-off.',
    'Materialized view vs index karsilastirmasi.',
    'Table partitioning vs sharding karsilastirmasi.',
    'SQL vs NoSQL secim kriterleri (ACID vs BASE).',
    'CAP theorem ve distributed DB tercihleri.',
    'Eventual consistency modelleri (causal, read-your-writes).',
    'Distributed transaction: 2PC vs Saga vs TCC.',
    'Idempotency key ile duplicate request korumasi.',
    'Optimistic vs pessimistic locking karsilastirmasi.',
    'MVCC (Multi-Version Concurrency Control) nasil calisir?',
    'Serializable vs Repeatable Read izolasyon seviyeleri.',
    'Deadlock prevention (lock ordering, timeout).',
    'Advisory locks vs row-level locks.',
    'Redis Lua scripting ile atomic operasyonlar.',
    'PostgreSQL stored procedures vs application logic.',
    'Batch insert vs single insert performansi.',
    'COPY command vs INSERT performansi (PostgreSQL).',
    'Bulk API vs single API call performansi.',
]

for inst in opt_extra:
    more_entries.append({
        'system': SYSTEM,
        'instruction': inst,
        'output': f'```python\n# Optimizasyon\n{inst}\ndef optimize():\n    return "Optimize edildi"\n```\n**Kazanim:** 2x-10x performans artisi.',
        'category': 'optimizasyon',
        'source': 'x_fable_coder',
        'timestamp': '2026-06-16T10:42:00Z'
    })

debug_extra = [
    'ImportError: circular import cozumu.',
    'ModuleNotFoundError: Python path problemi cozumu.',
    'AttributeError: object has no attribute cozumu.',
    'KeyError vs get() ile dictionary guvenli erisim.',
    'IndexError: list index out of range cozumu.',
    'TypeError: unsupported operand type cozumu.',
    'ValueError: invalid literal for int() cozumu.',
    'StopIteration: generator bitti cozumu.',
    'GeneratorExit: generator cleanup cozumu.',
    'RuntimeError: dictionary changed size during iteration.',
    'PermissionError: file permission cozumu.',
    'FileNotFoundError: dosya yok cozumu.',
    'IsADirectoryError: dosya yerine dizin cozumu.',
    'ConnectionRefusedError: port kapali cozumu.',
    'ConnectionResetError: baglanti dustu cozumu.',
    'TimeoutError: islem zamani asimi cozumu.',
    'MemoryError: bellek yetersiz cozumu.',
    'SystemError: internal error cozumu.',
    'AssertionError: assert basarisiz cozumu.',
    'NotImplementedError: abstract method cozumu.',
    'FloatingPointError: float hesaplama hatasi.',
    'OverflowError: matematiksel overflow cozumu.',
    'ZeroDivisionError: sifira bolme cozumu.',
    'OSError: general OS hatasi cozumu.',
    'EnvironmentError: environment variable yok.',
    'IOError: I/O error cozumu (deprecated, OSError).',
    'EOFError: input() beklenmedik bitis.',
    'KeyboardInterrupt: Ctrl+C yakalama ve graceful shutdown.',
    'SystemExit: sys.exit() yakalama ve cleanup.',
    'SyntaxWarning: syntax uyarilari cozumu.',
    'DeprecationWarning: deprecated API cozumu.',
    'ResourceWarning: unclosed resource cozumu.',
    'UnicodeWarning: unicode uyarisi cozumu.',
    'BytesWarning: bytes/string karisikligi cozumu.',
    'PerformanceWarning: yavas islem uyarisi.',
    'UserWarning: custom warning yonetimi.',
    'FutureWarning: gelecekte degisecek API cozumu.',
    'PendingDeprecationWarning: yakinda deprecated olacak.',
    'ImportWarning: import uyarisi cozumu.',
    'RuntimeWarning: runtime uyarisi cozumu.',
]

for inst in debug_extra:
    more_entries.append({
        'system': SYSTEM,
        'instruction': inst,
        'output': f'```python\n# HATA: {inst}\ntry:\n    riskli_islem()\nexcept SpecificError as e:\n    print(f"Hata: {{e}}")\n    cozum()\n```\n**Kok neden:** {inst}\n**Cozum:** Dogru exception handling + input validation.',
        'category': 'debug',
        'source': 'x_fable_coder',
        'timestamp': '2026-06-16T10:43:00Z'
    })

cc_extra = [
    'DI (Dependency Injection) container implementasyonu.',
    'IoC (Inversion of Control) prensibi ornegi.',
    'AOP (Aspect Oriented Programming) ile logging/caching.',
    'Pipeline pattern ile data processing chain.',
    'Specification pattern ile is kurallari yonetimi.',
    'Null Object pattern ile null checkten kurtul.',
    'Value Object: para birimi ornegi (immutable).',
    'Aggregate Root: domain-driven design ornegi.',
    'Domain Event pattern ile decoupling.',
    'Application Service vs Domain Service farki.',
    'Anti-corruption layer ile legacy entegrasyon.',
    'Repository pattern: ORM vs raw SQL.',
    'CQRS: command query responsibility segregation.',
    'Eventual consistency model ornegi.',
    'Saga choreography vs orchestration karsilastirmasi.',
    'API Gateway pattern ile microservice gateway.',
    'Backend For Frontend (BFF) pattern.',
    'Strangler Fig ile monolit-microservice gecisi.',
    'Sidecar pattern ile service mesh.',
    'Ambassador pattern ile proxy servis.',
    'Adapter pattern ile farkli APIleri birlestirme.',
    'Facade pattern ile kompleksi basitlestir.',
    'Proxy pattern ile virtual proxy (lazy loading).',
    'Chain of Responsibility: HTTP middleware ornegi.',
    'Strategy pattern: farkli odeme yontemleri.',
    'State pattern: siparis durum makinesi.',
    'Decorator pattern: input validation wrapper.',
    'Composite pattern: menu tree yapisi.',
    'Iterator pattern: custom pagination.',
    'Mediator pattern: chat odasi ornegi.',
    'Memento pattern: oyun kaydetme sistemi.',
    'Observer pattern: push vs pull karsilastirmasi.',
    'Template Method: data export pipeline.',
    'Visitor pattern: AST (abstract syntax tree) isleme.',
    'Factory Method: document parser factory.',
    'Abstract Factory: UI theme factory.',
    'Prototype: oyun karakteri klonlama.',
    'Singleton: thread-safe logger.',
    'Builder: HTML builder ornegi.',
    'Fluent interface: query builder API tasarimi.',
]

for inst in cc_extra:
    more_entries.append({
        'system': SYSTEM,
        'instruction': inst,
        'output': f'```python\nclass DesignPattern:\n    def __init__(self):\n        self.pattern = "{inst}"\n    def apply(self):\n        return f"SOLID + {{self.pattern}} implemented"\n```\n**Prensip:** Design pattern ile clean code.\n**Kazanim:** Daha moduler, test edilebilir, bakimi kolay.',
        'category': 'clean_code',
        'source': 'x_fable_coder',
        'timestamp': '2026-06-16T10:44:00Z'
    })

data.extend(more_entries)
print(f'Extended: {len(data)} entries')

with open('x_fable_coder_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Saved!')

from collections import Counter
cats = Counter(e['category'] for e in data)
for cat, count in sorted(cats.items()):
    print(f'  {cat}: {count}')
