# `bplustree`

## Tree:
bplustree/
    ├── tree.py              - Core B+ tree implementation: BPlusTree class, overflow handling, tree orchestration, and the public persistent mapping API. Owns the tree-level persistence API and coordinates low-level paging and overflow handling.
    └── utils.py             - Small utilities used by tree.py: byte/chunking helpers (iter_slice) and adjacent-pair iteration (pairwise).

## Purpose:
This repository provides a durable, on-disk B+ tree implementation exposing a mapping-like API from comparable keys to bytes values. It is optimized for persistent ordered storage with support for values that may span pages via overflow pages.

Why this matters:
- Offers an embedded ordered index for applications that need durable, transactional key/value storage without a full DBMS.
- Enables efficient range queries and bulk insertion while handling large values transparently via overflow chaining.

Target users and scenarios:
- Application developers embedding a persistent ordered index in their projects.
- Storage-engine or database implementers who need a B+ tree abstraction.
- Scripts and tools performing bulk ingestion or maintenance tasks on ordered data.

Position in the ecosystem:
- Library/package intended to be imported into Python applications. It is not a standalone network service. The core module (tree.py) orchestrates storage and uses small utilities (utils.py) to implement paging behaviors.

Refer to component-level docs for in-depth behavior:
- bplustree.tree.BPlusTree
- bplustree.utils.iter_slice
- bplustree.utils.pairwise

## Architecture:

End-to-end data flow (Mermaid flowchart TD):

flowchart TD
    Client["Client (app code)"]
    BTree["bplustree.tree.BPlusTree"]
    Utils["bplustree.utils (iter_slice, pairwise)"]
    Serializer["Serializer (key codec)"]
    NodeLayer["Node/Entry representations (leaf/internal/record/reference)"]
    FileMemory["FileMemory-like storage backend"]
    Overflow["Overflow pages (chained pages)"]

    Client -->|import / call API| BTree
    BTree -->|encode/decode keys| Serializer
    BTree -->|use helpers| Utils
    BTree -->|manipulate nodes| NodeLayer
    BTree -->|page alloc/read/write| FileMemory
    FileMemory -->|store chain| Overflow
    NodeLayer -->|serialize nodes| FileMemory
    BTree -->|transactions| FileMemory

Key architectural patterns:
- Layered responsibilities:
  - tree.py: tree-level orchestration, public API, search/insert/split logic, overflow handling, and transactional boundaries.
  - Node/entry representations: in-memory node and entry data structures (may be implemented in the same module or as cooperating classes); BPlusTree uses these to represent and mutate node state.
  - Storage backend (FileMemory-like): page allocation, read/write page operations, metadata storage, and transaction context managers.
  - Utilities (utils.py): small helpers for byte-chunking and adjacent-pair iteration used by overflow and node algorithms.
- Transaction-scoped operations:
  - Read and write transactions are provided by the storage backend and used by BPlusTree to guarantee atomicity and durability of operations.
- Overflow chaining:
  - Values larger than inline capacity are written to overflow pages that contain fixed-size integer fields (next-page reference and payload length) followed by payload bytes. Utilities are used to chunk payloads and reconstruct them during reads.

## Entry Points:

Importable APIs (primary):

- bplustree.tree.BPlusTree
  - Typical constructor signature:
    - BPlusTree(filename: str,
                page_size: int = 4096,
                order: int = 100,
                key_size: int = 8,
                value_size: int = 32,
                cache_size: int = 64,
                serializer: Optional[Serializer] = None)
  - Exposes mapping-like behavior with methods for insertion, bulk insertion, lookups, membership tests, iteration, slicing, checkpointing, and lifecycle management (close/context-manager support).
  - Exact method semantics, argument names, and edge-case behavior are defined in the component-level BPlusTree documentation; implementers should consult that doc for precise contracts.

- bplustree.utils.iter_slice
  - Signature (conceptual): iter_slice(buf: bytes, n: int) -> Iterator[tuple[bytes, bool]]
  - Use: split a bytes-like buffer into chunks of size <= n; yields (chunk, is_final_chunk).

- bplustree.utils.pairwise
  - Signature (conceptual): pairwise(iterable) -> Iterator[tuple[Any, Any]]
  - Use: iterate overlapping adjacent pairs from an iterable; useful for comparing neighbors during scans or splits.

Note: This package contains no CLI entrypoints; it is intended to be imported.

## Core Features:
- Persistent on-disk B+ tree API
  - Ordered, durable mapping of keys to bytes values; supports standard mapping operations and range scans (tree.py).

- Transactional reads and writes
  - Public mutating operations are executed within write transactions supplied by the storage backend; reads use read transactions (tree.py + FileMemory interaction).

- Overflow page support
  - Handles values larger than inline capacity by chaining overflow pages with explicit next-page and payload-length fields (tree.py + utils.iter_slice).

- Iteration and slicing
  - Ordered iterators and range-slice retrievals that operate under read-transaction snapshots (tree.py).

- Bulk insertion
  - Batch insertion of many key/value pairs inside a single write transaction to improve ingestion performance (tree.py).

- Checkpointing and lifecycle management
  - Exposes checkpoint() and close() to manage backend checkpoints and resource cleanup (tree.py delegating to the storage backend).

## Dependencies:

Internal or cooperating components (expected) and their roles:
- FileMemory-like storage backend (required interface)
  - Role: low-level page allocation and read/write, metadata access, and transaction context managers.
  - Expected API surface (implementers must provide compatible behavior):
    - read_transaction(), write_transaction(): context managers used for scoped operations. Read transactions may be held open by iterators; write transactions are used for all mutations.
    - get_page(page_no) / set_page(page_no, data): read and write raw page bytes.
    - next_available_page(), last_page() or equivalent page allocation helpers.
    - get_metadata() / set_metadata(): read/write tree-level metadata stored in the file.
    - perform_checkpoint(reopen_wal=True) or equivalent checkpointing operation.
    - close(): release resources and close the underlying file.
  - Note: BPlusTree relies on the presence of these behaviors but does not mandate how FileMemory is implemented.

- Node/Entry representations (part of the tree layer)
  - Role: represent leaf/internal nodes and entries in memory; support operations required by BPlusTree: insertion, ability checks for adding an entry, splitting, extracting smallest/biggest keys, and (de)serialization to/from page bytes.
  - These representations may be implemented inside tree.py or as cooperating classes; BPlusTree expects a stable contract from them.

- Serializer (key codec)
  - Role: encode/decode keys into bytes (and possibly enforce fixed-size encodings). Must preserve comparability semantics across operations.

Standard library:
- functools, itertools, typing, logging are used by utilities and orchestration code.

Versioning:
- Designed for modern Python (typing usage); no external pip dependencies are required by the repository code itself.

## Important constants and overflow encoding (conceptual):
- PAGE_REFERENCE_BYTES (int)
  - Bytes allocated to encode the next-page reference in an overflow page. A zero or sentinel value indicates no further page.

- USED_PAGE_LENGTH_BYTES (int)
  - Bytes used to encode how many payload bytes are stored in the overflow page.

- ENDIAN (str, 'big' or 'little')
  - Endianness used to encode integer fields into fixed-width byte regions.

Encoding and invariants (conceptual):
- Overflow page layout (conceptual):
  - [next_page (PAGE_REFERENCE_BYTES bytes)] [payload_length (USED_PAGE_LENGTH_BYTES bytes)] [payload bytes (payload_length)]
- Constraints:
  - page_size must be larger than PAGE_REFERENCE_BYTES + USED_PAGE_LENGTH_BYTES so that each overflow page can store a positive payload.
  - Values written into the fixed-width integer fields must fit within the allotted number of bytes; implementations must check sizes and raise appropriate errors if values are too large to encode.
- Behavior:
  - Writing overflow: chunk payload into per-page payload-capacity pieces (use iter_slice), allocate pages, write header+payload with next_page linking to the next chunk.
  - Reading overflow: follow the next_page chain, read payload_length and payload bytes from each page, and concatenate until the chain ends.

## Constraints and invariants:
- Keys must be comparable and consistently encoded by the serializer. Mixing incompatible key types or serializers will break ordering invariants.
- Values are bytes. Implementations should validate input type and raise on non-bytes inputs rather than silently accepting other types.
- All mutating operations must run inside write transactions provided by the backend. Read iterators hold read transactions open until exhausted or closed.
- batch_insert requires callers to supply data according to ordering preconditions (see component-level BPlusTree docs). Violations should result in a ValueError and abort the write transaction.
- The library does not guarantee thread-safety; concurrency behavior depends on the storage backend.

## Extension Points:
- Replace FileMemory backend:
  - Implement a compatible storage backend (in-memory, on-disk, or remote) that provides the required API surface to change storage medium or enable testing.

- Provide custom serializers:
  - Implement key serializers that produce consistent, comparable encodings for different key types.

- Alternative node/entry layouts:
  - Implement different node packing, compression, or entry formats as long as the node contract expected by BPlusTree is honored.

## Implementation guidance & next steps:
To reimplement this system from scratch:
1. Implement a FileMemory-like backend offering page-level reads/writes, page allocation, metadata storage, and read/write transaction context managers matching the expected behaviors described above.
2. Implement node and entry representations that support insertion, splitting, (de)serialization to/from page bytes, and provide smallest/biggest key accessors.
3. Implement serializers for keys (and, if desired, values) ensuring ordering is preserved after encoding.
4. Implement BPlusTree in tree.py:
   - Manage metadata and root node allocation on create/open.
   - Implement search, insert, split, and iterator logic. Wrap mutations in backend write transactions and perform reads under read transactions.
   - Implement overflow handling per the conceptual encoding above using utils.iter_slice for chunking.
   - Provide mapping-like public methods (insert, batch_insert, get, __getitem__, __contains__, __len__, __iter__, keys, items, values, checkpoint, close) with semantics and preconditions documented at component level.
5. Implement utils.iter_slice and utils.pairwise as small, well-tested helpers used by overflow and node algorithms.

For precise control-flow, method-level contracts, and edge-case handling (e.g., exact behavior when inserting duplicate keys, precise exceptions raised, iterator semantics), consult the component-level documentation for:
- bplustree.tree.BPlusTree
- bplustree.utils.iter_slice
- bplustree.utils.pairwise

This repository-level documentation describes the system architecture, responsibilities, extension points, and the minimal expected interfaces a developer must provide to reconstruct a compatible implementation.

---

## Modules

- [`bplustree`](bplustree.md)

