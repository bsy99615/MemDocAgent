# `events.py`

## `flower.events.get_prometheus_metrics` · *function*

## Summary:
Returns a shared PrometheusMetrics instance, creating and caching it on first call so callers receive a single, process-wide metrics container.

## Description:
This function implements the simple "singleton getter" for the module-level PROMETHEUS_METRICS variable. On the first call, when PROMETHEUS_METRICS is None, it constructs a new PrometheusMetrics() and stores it in the global PROMETHEUS_METRICS; subsequent calls return that cached instance.

Known callers and typical call contexts:
- Components that need to record or expose Prometheus metrics (for example, Celery event handlers, HTTP endpoints exposing metrics, or background tasks that emit metrics).
- Typical use is at application startup or lazily on first use: event-processing code or monitoring endpoints call this function to obtain the shared metrics object before calling .inc(), .observe(), or .set() on the contained metric objects.
- No specific function names from the codebase are required here; the convention is a single shared instance per process used by multiple parts of the Flower events/monitoring subsystem.

Why this logic is extracted:
- Responsibility boundary: centralizes lazy initialization and caching of the PrometheusMetrics instance so callers do not need to manage creation, duplicate registration, or share a common instance manually.
- Avoids duplicating the creation-and-cache pattern across modules and reduces the risk of multiple independent constructions in simple uses.

## Args:
    None

## Returns:
    PrometheusMetrics: The (cached) process-wide PrometheusMetrics instance.
    - On first invocation, returns a newly constructed PrometheusMetrics instance (and stores it in the global PROMETHEUS_METRICS).
    - On subsequent invocations, returns the same object previously stored in PROMETHEUS_METRICS.
    - The function never intentionally returns None under normal operation; a None return would only occur if PrometheusMetrics.__init__ somehow returns None (which would be an implementation bug).

## Raises:
    No exceptions are raised directly by this function body.
    However, constructing PrometheusMetrics() may raise exceptions that propagate to the caller, including but not limited to:
    - NameError: if PrometheusMetrics is not defined in the module scope.
    - ImportError / ModuleNotFoundError: raised earlier if prometheus_client or other dependencies are missing.
    - AttributeError: if required runtime configuration (e.g., options.task_runtime_metric_buckets) is missing.
    - ValueError: duplicate metric registration if multiple PrometheusMetrics instances or metrics with the same names are registered in the default Prometheus registry.
    - TypeError / ValueError: invalid constructor arguments passed to prometheus_client metric constructors inside PrometheusMetrics.__init__.

## Constraints:
Preconditions:
    - The module-level global PROMETHEUS_METRICS must exist (the function references it). It is expected to be initialized to None at import time.
    - PrometheusMetrics must be defined/importable in the same module.
    - Any invariants required by PrometheusMetrics.__init__ (for example, options.task_runtime_metric_buckets being configured) must hold; otherwise instantiation will fail and exceptions will propagate.

Postconditions:
    - After a successful call, PROMETHEUS_METRICS is guaranteed to reference a PrometheusMetrics instance (the same object returned to the caller).
    - Calling this function repeatedly will return the same PrometheusMetrics object until the global is reassigned elsewhere.

## Side Effects:
    - Global state mutation: may assign a newly created PrometheusMetrics instance to the module-level global PROMETHEUS_METRICS.
    - PrometheusMetrics.__init__ side effects: constructing the instance registers prometheus_client metric objects in the default CollectorRegistry (this may raise ValueError if the same metric names are already registered).
    - No file, network, or stdout side effects are performed directly by this function itself; any I/O is dependent on PrometheusMetrics or other code executed during construction.

## Thread-safety and concurrency notes:
    - The function is not synchronized. If multiple threads call get_prometheus_metrics concurrently while PROMETHEUS_METRICS is None, multiple threads may attempt to construct PrometheusMetrics() concurrently, potentially:
        - Causing duplicate metric registration errors, or
        - Producing multiple instances with the last assignment winning.
    - If callers expect concurrent initialization, protect calls with a module-level lock, or ensure initialization occurs at process startup in a single thread.

## Control Flow:
flowchart TD
    A[Call get_prometheus_metrics()] --> B{PROMETHEUS_METRICS is None?}
    B -- Yes --> C[Construct PrometheusMetrics()]
    C --> D[Assign instance to PROMETHEUS_METRICS]
    D --> E[Return PROMETHEUS_METRICS]
    B -- No --> E[Return PROMETHEUS_METRICS]

## Examples:
- Basic usage (happy path)
    try:
        metrics = get_prometheus_metrics()
        metrics.events.labels(worker='w1', type='task-received', task='mytask').inc()
    except Exception as exc:
        # Handle construction or metrics errors (e.g., duplicate registration)
        logging.exception("Failed to obtain or use Prometheus metrics: %r", exc)

- Safe initialization at startup (single-threaded)
    # At application startup, ensure a single initialization:
    PROMETHEUS_METRICS = None  # module-level default
    # Later, during startup sequence (single-threaded):
    get_prometheus_metrics()  # forces construction and registration early

- Concurrent-safe pattern (if you cannot guarantee single-threaded startup)
    _metrics_lock = threading.Lock()
    def safe_get_metrics():
        with _metrics_lock:
            return get_prometheus_metrics()
    # Use safe_get_metrics() from concurrent contexts to avoid race conditions.

Implementation notes:
    - To avoid duplicate metric registration in tests or worker reloads, either:
        * Ensure a single process-level instance is reused, or
        * Replace PrometheusMetrics to use an explicit CollectorRegistry and pass it to the prometheus_client constructors.
    - The function intentionally delegates error handling for metric construction to callers: it does not catch or wrap exceptions raised during PrometheusMetrics() construction.

## `flower.events.PrometheusMetrics` · *class*

## Summary:
Container object that constructs and exposes a set of Prometheus metric objects (counters, gauges, histograms) used by Flower's events subsystem; it centralizes metric names, label keys, and histogram bucket configuration so callers can record observability data consistently.

## Description:
PrometheusMetrics is designed to be created once (commonly at Flower server startup) and shared with components that record metrics for Celery events and worker/task state. It does not record events itself — it only constructs and exposes metric objects that callers interact with (for example, by calling .inc(), .observe(), .set()).

Typical instantiation scenarios:
- Created during Flower application initialization or by an events/monitoring factory that wires up Celery event handling into metrics collection.
- No constructor arguments are required; call sites simply run metrics = PrometheusMetrics() and use the returned object.

Motivation and responsibility boundary:
- Responsibility: create and expose ready-to-use, consistently named prometheus metrics with predefined label schemas and histogram buckets.
- Boundary: does not abstract metric operations; it does not manage lifecycle of the Prometheus registry, perform I/O, or remove/unregister metrics. Callers are responsible for recording metric values and for any registry management if required.

## State:
All attributes are created in __init__ and expected to remain present and unchanged for the object's lifetime.

- events
    - Type: PrometheusCounter (unknown wrapper) OR functionally equivalent to prometheus_client.Counter
    - Metric name: 'flower_events_total'
    - Label keys / order: ['worker', 'type', 'task'] (order matters when calling .labels())
    - Semantics: cumulative counter (non-decreasing). Use .labels(worker=..., type=..., task=...).inc() to increment.
    - Invariant: each call to .inc() increases the counter. Label values must be provided for all keys.

- runtime
    - Type: prometheus_client.Histogram
    - Metric name: 'flower_task_runtime_seconds'
    - Label keys / order: ['worker', 'task']
    - Semantics: observes task runtime in seconds via .labels(...).observe(value)
    - Configuration: constructed with buckets=options.task_runtime_metric_buckets
    - Constraints: options.task_runtime_metric_buckets must be an iterable of numeric bucket upper bounds (monotonically increasing). If not, the Histogram constructor may raise TypeError or ValueError.
    - Invariant: callers should pass non-negative numeric durations.

- prefetch_time
    - Type: prometheus_client.Gauge
    - Metric name: 'flower_task_prefetch_time_seconds'
    - Label keys / order: ['worker', 'task']
    - Semantics: gauge that records time spent waiting at the worker (seconds) via .labels(...).set(value)
    - Valid values: non-negative numeric values in typical usage.

- number_of_prefetched_tasks
    - Type: prometheus_client.Gauge
    - Metric name: 'flower_worker_prefetched_tasks'
    - Label keys / order: ['worker', 'task']
    - Semantics: current number of prefetched tasks for a given worker and task type. Use .labels(...).set(integer) or .inc()/.dec().

- worker_online
    - Type: prometheus_client.Gauge
    - Metric name: 'flower_worker_online'
    - Label keys / order: ['worker']
    - Semantics: represents online status. Convention: set to 1 when online, 0 when offline (via .labels(...).set(0 or 1)).

- worker_number_of_currently_executing_tasks
    - Type: prometheus_client.Gauge
    - Metric name: 'flower_worker_number_of_currently_executing_tasks'
    - Label keys / order: ['worker']
    - Semantics: current count of executing tasks on a worker; set via .labels(...).set(integer).

Class invariants:
- After __init__, all listed attributes must exist and refer to valid prometheus_client metric objects (or to a PrometheusCounter-like wrapper for events).
- Label keys listed above are the canonical keys; callers must supply values for each key when calling .labels(...). Supplying fewer or extra label values will cause the prometheus_client child-metric access to raise an error.
- The metrics are registered in the default prometheus_client registry (collector registry). Creating a second PrometheusMetrics instance in the same process without using a separate CollectorRegistry will attempt to register metrics with the same names and may raise ValueError (duplicate metric registration).

## Lifecycle:
Creation:
- Instantiate without arguments:
    - metrics = PrometheusMetrics()
- Requirements before instantiation:
    - prometheus_client library must be importable.
    - options.task_runtime_metric_buckets must be defined (typically by Tornado options) and be an iterable of numeric bounds suitable for Histogram buckets.
    - PrometheusCounter must be available in the module scope. If PrometheusCounter is not available, replace events initialization with prometheus_client.Counter using the same name and label keys.

Usage:
- No particular ordering required. Typical usage patterns:
    - Increment an event counter:
        - metrics.events.labels(worker='w1', type='task-received', task='mytask').inc()
    - Observe task runtime:
        - metrics.runtime.labels(worker='w1', task='mytask').observe(1.23)
    - Set prefetch time:
        - metrics.prefetch_time.labels(worker='w1', task='mytask').set(0.45)
    - Update prefetched tasks count:
        - metrics.number_of_prefetched_tasks.labels(worker='w1', task='mytask').set(3)
    - Toggle worker online:
        - metrics.worker_online.labels(worker='w1').set(1)  # online
        - metrics.worker_online.labels(worker='w1').set(0)  # offline
    - Set number of executing tasks:
        - metrics.worker_number_of_currently_executing_tasks.labels(worker='w1').set(2)

Destruction / cleanup:
- PrometheusMetrics has no cleanup methods. Metrics are registered in prometheus_client's default registry. If your application needs to unregister metrics (for example, to reload components or avoid duplicate registrations in tests), callers must use the prometheus_client.CollectorRegistry API or other registry-management utilities to remove or isolate these metrics.
- Avoid creating multiple PrometheusMetrics instances in the same process unless you provide a custom registry to avoid duplicate registration errors.

## Method Map:
Mermaid diagram (method/attribute creation and typical usage flows)

flowchart LR
    A[__init__] --> B[events: PrometheusCounter('flower_events_total') labels: worker,type,task]
    A --> C[runtime: Histogram('flower_task_runtime_seconds') labels: worker,task]
    A --> D[prefetch_time: Gauge('flower_task_prefetch_time_seconds') labels: worker,task]
    A --> E[number_of_prefetched_tasks: Gauge('flower_worker_prefetched_tasks') labels: worker,task]
    A --> F[worker_online: Gauge('flower_worker_online') labels: worker]
    A --> G[worker_number_of_currently_executing_tasks: Gauge(...) labels: worker]

    B --> H[.labels(...).inc() -> increment events]
    C --> I[.labels(...).observe(duration) -> record runtime]
    D --> J[.labels(...).set(seconds) -> record prefetch time]
    E --> K[.labels(...).set(n) -> set prefetched tasks]
    F --> L[.labels(...).set(0/1) -> worker status]
    G --> M[.labels(...).set(n) -> executing tasks count]

## Raises:
PrometheusMetrics.__init__ does not explicitly raise exceptions in the source but will propagate exceptions from dependencies. Notable error conditions to guard for:

- NameError
    - Trigger: PrometheusCounter is not defined in the module scope at runtime.
    - When it occurs: immediately when __init__ attempts to reference PrometheusCounter.

- ImportError / ModuleNotFoundError
    - Trigger: prometheus_client is not importable at module import time.
    - When it occurs: before __init__ is called (during module import).

- AttributeError
    - Trigger: options.task_runtime_metric_buckets does not exist on tornado.options or options is not initialized.
    - When it occurs: when __init__ attempts to read options.task_runtime_metric_buckets to pass to Histogram.

- ValueError (duplicate metric registration)
    - Trigger: creating a metric with a name already registered in the default CollectorRegistry.
    - When it occurs: when prometheus_client tries to register a metric name already present (common if multiple PrometheusMetrics instances are created without custom registries).

- TypeError / ValueError (invalid constructor arguments)
    - Trigger: invalid type or value passed to Histogram/Gauge/Counter constructors (for example, an invalid buckets argument).
    - When it occurs: during metric object construction inside __init__.

Callers should catch or prevent these conditions by ensuring required imports are present, options.task_runtime_metric_buckets is configured correctly (iterable of increasing numeric bounds), and by creating only one PrometheusMetrics instance per process unless using a custom CollectorRegistry.

## Example:
Illustrative usage (no imports other than the class; errors may be raised if prometheus_client or PrometheusCounter are missing):

metrics = PrometheusMetrics()

# Increment event counter (must supply label values in the exact key order or as named args)
metrics.events.labels(worker='worker1', type='task-received', task='mytask').inc()

# Record runtime in seconds
metrics.runtime.labels(worker='worker1', task='mytask').observe(1.23)

# Record prefetch time
metrics.prefetch_time.labels(worker='worker1', task='mytask').set(0.45)

# Set number of prefetched tasks
metrics.number_of_prefetched_tasks.labels(worker='worker1', task='mytask').set(3)

# Mark worker online
metrics.worker_online.labels(worker='worker1').set(1)

# Set currently executing tasks
metrics.worker_number_of_currently_executing_tasks.labels(worker='worker1').set(2)

Implementation notes / migration guidance:
- If PrometheusCounter is unavailable, create events using prometheus_client.Counter:
    - Counter('flower_events_total', 'Number of events', ['worker', 'type', 'task'])
- Ensure options.task_runtime_metric_buckets is configured before instantiation; it should be an iterable such as [0.1, 0.5, 1.0, 5.0, 10.0] or similar, in ascending order.
- To avoid duplicate registration in tests, either reuse the same PrometheusMetrics instance or provide a custom CollectorRegistry when constructing metrics (requires changing construction calls to pass registry=... to prometheus_client constructors).

### `flower.events.PrometheusMetrics.__init__` · *method*

## Summary:
Creates and attaches a fixed set of Prometheus metric objects to the PrometheusMetrics instance so callers can consistently record events, task runtimes, prefetch timings, and worker statistics.

## Description:
This constructor instantiates and assigns ready-to-use prometheus metrics as attributes on the object. Typical callers and lifecycle stage:
- Called once during application startup or monitoring subsystem initialization (e.g., when the Flower server is initialized or when an events/monitoring factory is run).
- The created PrometheusMetrics instance is then shared with event handlers and monitoring code that record metric data (via .inc(), .observe(), .set(), etc).

Why this is a separate method:
- Centralizes metric name, label schema, and histogram bucket configuration in one location so all parts of the system use a consistent set of metrics.
- Keeps metric construction and registration separate from business logic that records metric values, preventing duplication and making testing / configuration easier.

## Args:
None.

## Returns:
None (constructor). Side-effect: the instance is mutated by creating metric attributes.

## Raises:
The constructor does not explicitly raise its own exceptions, but the following errors may be raised by dependencies and will propagate:
- NameError
    - Condition: PrometheusCounter is not defined in module scope when events is constructed.
    - Happens immediately when attempting to reference PrometheusCounter('flower_events_total', ...).
- AttributeError
    - Condition: options.task_runtime_metric_buckets is not set on tornado.options.options.
    - Happens when passing buckets=options.task_runtime_metric_buckets into Histogram.
- TypeError or ValueError
    - Condition: invalid argument types/values passed to prometheus_client constructors (for example, buckets is not an iterable of numbers or not monotonically increasing).
    - Happens during Histogram/Gauge/Counter construction.
- ValueError (duplicate metric registration)
    - Condition: a metric with the same name is already registered in the default prometheus_client CollectorRegistry (e.g., a second PrometheusMetrics instance in the same process without a custom registry).
    - Happens when prometheus_client attempts to register a duplicate metric name.

Callers should ensure imports and configuration (notably options.task_runtime_metric_buckets) are available and valid before instantiation to avoid these propagated exceptions.

## State Changes:
Attributes READ:
- None of the object's own attributes (no self.<attr> is read). The constructor does read module-level symbols:
    - options.task_runtime_metric_buckets (module-level global read)
    - PrometheusCounter (module-level symbol reference)
    - prometheus_client.Counter/Gauge/Histogram constructors (module-level classes)

Attributes WRITTEN (created / assigned on self):
- self.events
    - Type: PrometheusCounter (wrapper) or prometheus_client.Counter
    - Name: 'flower_events_total'
    - Labels: ['worker', 'type', 'task']
- self.runtime
    - Type: prometheus_client.Histogram
    - Name: 'flower_task_runtime_seconds'
    - Labels: ['worker', 'task']
    - Config: constructed with buckets=options.task_runtime_metric_buckets
- self.prefetch_time
    - Type: prometheus_client.Gauge
    - Name: 'flower_task_prefetch_time_seconds'
    - Labels: ['worker', 'task']
- self.number_of_prefetched_tasks
    - Type: prometheus_client.Gauge
    - Name: 'flower_worker_prefetched_tasks'
    - Labels: ['worker', 'task']
- self.worker_online
    - Type: prometheus_client.Gauge
    - Name: 'flower_worker_online'
    - Labels: ['worker']
- self.worker_number_of_currently_executing_tasks
    - Type: prometheus_client.Gauge
    - Name: 'flower_worker_number_of_currently_executing_tasks'
    - Labels: ['worker']

## Constraints:
Preconditions (what must be true before calling):
- prometheus_client library must be importable and its Counter, Gauge, Histogram types must be available.
- options.task_runtime_metric_buckets must exist and be a valid iterable of numeric bucket upper bounds appropriate for prometheus_client.Histogram (typically ascending numeric bounds).
- PrometheusCounter symbol (a module-level wrapper) should be defined if that wrapper is expected; otherwise client code must accept that replacing it with prometheus_client.Counter is acceptable.
- Avoid instantiating more than one PrometheusMetrics in the same process unless metrics are registered with separate CollectorRegistry instances, to prevent duplicate metric registration errors.

Postconditions (guarantees after the call):
- The instance will have the six attributes listed under "Attributes WRITTEN" and each will reference a constructed metric object that supports the prometheus_client API (e.g., .labels(...).inc(), .observe(), .set()).
- The constructed metrics are registered in the default CollectorRegistry by prometheus_client (unless a different registry is supplied externally in a modified implementation).
- Label key order is defined for each metric and callers must supply label values for all keys when accessing child metrics (using .labels(...) with positional or named args).

## Side Effects:
- Registers new metric collectors in prometheus_client's default CollectorRegistry; this is visible globally in the process.
- No network or filesystem I/O occurs in the constructor itself, but metric registration affects the global Prometheus registry state and may raise ValueError if names collide.
- No external services are called; however, other parts of the application that read the registry (e.g., an HTTP metrics endpoint) will observe the new metrics after construction.

## Implementation notes for re-implementation:
- Use prometheus_client.Counter/Gauge/Histogram constructors with the specified metric names and label lists.
- For events, if PrometheusCounter is unavailable, use:
    - Counter('flower_events_total', 'Number of events', ['worker', 'type', 'task'])
- Ensure options.task_runtime_metric_buckets provides valid bucket boundaries before passing to Histogram to avoid constructor errors.
- To prevent duplicate registration in tests or when reloading, either:
    - Create metrics with an explicit CollectorRegistry and use that registry for exposition, or
    - Reuse a single PrometheusMetrics instance across the process.

## `flower.events.EventsState` · *class*

## Summary:
Represents a Celery events state that augments the base celery.events.state.State with per-worker event counters and Prometheus metric updates for task and worker lifecycle events.

## Description:
EventsState is instantiated wherever the application needs to consume and maintain the Celery event stream while also recording operational metrics. It should be created in the event-consumption pipeline (for example, by the component that creates a celery.events.EventReceiver or elsewhere during the monitoring/collector startup). The class specializes the base State.event handler to perform two responsibilities:
- Maintain an in-memory nested counter of event types per worker.
- Update Prometheus metric collectors (counters, gauges, histograms) for task lifecycle and worker lifecycle events.

Rationale: separating metric logic into this subclass centralizes event-driven metric updates and keeps those concerns out of the generic base State or event dispatching loop.

Known callers/factories:
- Celery event processing code that dispatches events to a State object (e.g., an EventReceiver loop configured to pass events to this State).
- Application startup code that chooses which State implementation to attach to Celery event consumers.

## State:
Attributes (public, used by other parts or inherited):
- counter
  - Type: collections.defaultdict(collections.Counter)  (effectively dict[str, Counter[str, int]])
  - Description: nested mapping: counter[worker_name][event_type] -> int
  - Initialization: created in __init__ as collections.defaultdict(Counter)
  - Valid values: non-negative integers for each worker_name/event_type
  - Invariant: each inner Counter maps event_type (str) to int counts, incremented only by event(); counts never decrease except via external mutation (not present in EventsState)

- metrics
  - Type: PrometheusMetrics (module-level custom wrapper produced by get_prometheus_metrics())
  - Description: container exposing Prometheus metric collectors used by this class:
      * events (Counter-like) with labels (worker_name, event_type, task_name) supporting .labels(...).inc()
      * runtime (Histogram-like) with labels (worker_name, task_name) supporting .labels(...).observe()
      * number_of_prefetched_tasks (Gauge-like / Counter-like) with labels (worker_name, task_name) supporting .labels(...).inc() and .dec()
      * prefetch_time (Gauge-like) with labels (worker_name, task_name) supporting .labels(...).set()
      * worker_online (Gauge-like) with labels (worker_name) supporting .labels(...).set()
      * worker_number_of_currently_executing_tasks (Gauge-like) with labels (worker_name) supporting .labels(...).set()
  - Initialization: assigned by calling get_prometheus_metrics() in __init__
  - Constraints: get_prometheus_metrics may raise/propagate exceptions (metric registration, configuration). It is not synchronized; callers should be aware of concurrent initialization risks.

Inherited/External state used:
- self.tasks (inherited from celery.events.state.State)
  - Type: mapping: task_id (str) -> TaskState-like object (the base State implementation provides task objects)
  - Required task object attributes used by EventsState:
      * started (numeric timestamp or falsy)
      * received (numeric timestamp or falsy)
      * eta (truthy if task has an ETA; used as boolean guard)
      * name (str) used for metric labeling
  - Invariant: when a task_id is present in self.tasks, the mapped object must expose the above attributes; otherwise attribute access may raise AttributeError.

## Lifecycle:
Creation:
- Instantiate via EventsState(*args, **kwargs). The constructor delegates to the base State constructor with the same arguments, then sets up counter and metrics.
- Required args: none beyond what the base State requires. Callers must handle exceptions from get_prometheus_metrics() if metric construction fails.

Usage (typical):
- Sequence:
    1. Create an EventsState instance and attach it as the State target for Celery event consumption.
    2. For each incoming event, call EventsState.event(event).
       - The method first delegates to super().event(event) to update the base state.
       - It then updates internal counters and metrics according to the event contents (details below).
    3. The object is reused across many event calls; counters accumulate over the process lifetime.

- Recommended sequencing:
    * Initialize the Prometheus collector (i.e., call get_prometheus_metrics()) in single-threaded startup if possible to avoid race conditions in metric registration.
    * Do not assume any automatic reset of counter or metrics; the instance retains counts until explicitly reset or process restart.

Destruction / Cleanup:
- EventsState has no explicit cleanup API. Any cleanup of Prometheus registrations (if needed in tests) must be handled externally (e.g., by using a dedicated CollectorRegistry and passing or resetting it).
- No context manager or close() is provided by EventsState itself.

## Method behavior (event):
Summary of event(event: dict) behavior:
- Preconditions:
    * event must be a mapping with at least keys 'hostname' and 'type'.
    * If event['type'] starts with 'task-', the key 'uuid' is expected/used.
- Steps performed:
    1. Call super().event(event) to let the base State update stored tasks/workers.
    2. Extract worker_name = event['hostname'] and event_type = event['type'].
    3. Increment the nested counter: self.counter[worker_name][event_type] += 1.
    4. If event_type starts with 'task-':
        - Obtain task_id = event['uuid'] and task = self.tasks.get(task_id).
        - Determine task_name in order:
            a) event.get('name', '') — if present, use it;
            b) else if task_id in self.tasks: use task.name or ''.
        - Increment events metric: metrics.events.labels(worker_name, event_type, task_name).inc()
        - If runtime = event.get('runtime', 0) is truthy: metrics.runtime.labels(worker_name, task_name).observe(runtime)
        - Read task_started = task.started and task_received = task.received (may raise AttributeError if task is None or malformed)
        - If event_type == 'task-received' and not task.eta and task_received:
            * metrics.number_of_prefetched_tasks.labels(worker_name, task_name).inc()
        - If event_type == 'task-started' and not task.eta and task_started and task_received:
            * metrics.prefetch_time.labels(worker_name, task_name).set(task_started - task_received)
            * metrics.number_of_prefetched_tasks.labels(worker_name, task_name).dec()
        - If event_type in ['task-succeeded', 'task-failed'] and not task.eta and task_started and task_received:
            * metrics.prefetch_time.labels(worker_name, task_name).set(0)
    5. If event_type == 'worker-online':
        - metrics.worker_online.labels(worker_name).set(1)
    6. If event_type == 'worker-heartbeat':
        - metrics.worker_online.labels(worker_name).set(1)
        - If event contains 'active': metrics.worker_number_of_currently_executing_tasks.labels(worker_name).set(event['active'])
    7. If event_type == 'worker-offline':
        - metrics.worker_online.labels(worker_name).set(0)

Edge cases and constraints:
- Missing keys:
    * Missing 'hostname' or 'type' raises KeyError when event[...] is executed.
    * For task events missing 'uuid' will raise KeyError because event['uuid'] is used directly.
- Missing task object:
    * self.tasks.get(task_id) may return None; subsequent attribute accesses (task.started, task.received, etc.) will raise AttributeError. The implementation relies on the base State to keep task objects available; callers should expect attribute errors if events are out of order or tasks are pruned.
- Metric operations:
    * The code assumes metrics.* attributes implement .labels(...).inc()/dec()/set()/observe() as used above. If get_prometheus_metrics returned an incompatible object, AttributeError will be raised.
    * Prometheus metric registration may raise ValueError if duplicate metric names are registered; this can occur if PrometheusMetrics is constructed multiple times in the same process.

## Method Map:
flowchart LR
    A[event(event)] --> B[super().event(event)]
    B --> C[increment self.counter[worker_name][event_type]]
    C --> D{event_type startswith 'task-'}
    D -->|Yes| E[resolve task_id, task, task_name]
    E --> F[metrics.events.labels(...).inc()]
    E --> G{if runtime} -->|Yes| H[metrics.runtime.labels(...).observe(runtime)]
    E --> I[task timing & prefetch logic:
         - 'task-received' -> inc number_of_prefetched_tasks
         - 'task-started' -> set prefetch_time & dec number_of_prefetched_tasks
         - 'task-succeeded'/'task-failed' -> set prefetch_time to 0]
    C --> J{event_type == 'worker-online'} -->|Yes| K[metrics.worker_online.labels(...).set(1)]
    C --> L{event_type == 'worker-heartbeat'} -->|Yes| M[metrics.worker_online.labels(...).set(1)]
    M --> N{event contains 'active'} -->|Yes| O[metrics.worker_number_of_currently_executing_tasks.labels(...).set(active)]
    C --> P{event_type == 'worker-offline'} -->|Yes| Q[metrics.worker_online.labels(...).set(0)]

## Raises:
- KeyError
  - Trigger: event missing 'hostname' or 'type', or when a task event is missing 'uuid' (implementation uses event['uuid']).
- AttributeError
  - Trigger: when the code expects a task object from self.tasks and it is None or lacks attributes .started, .received, .eta, or .name.
  - Trigger: if metrics object returned from get_prometheus_metrics() does not expose expected metric attributes or their .labels returns objects lacking the methods used.
- Any exception raised by get_prometheus_metrics() during __init__
  - Trigger: metric construction/registration failures (ValueError for duplicate registration, configuration errors, import errors). These propagate from __init__.

## Example:
- Create an EventsState and process a single task-received event (illustrative):
  1) Instantiate:
     state = EventsState()
  2) Example event processed by the event loop:
     event = {
       'hostname': 'worker1',
       'type': 'task-received',
       'uuid': 'abcd-1234',
       'name': 'myapp.tasks.add',
       'runtime': 0.0,
       'active': 2
     }
     state.event(event)
  3) Effects:
     - state.counter['worker1']['task-received'] is incremented by 1
     - metrics.events.labels('worker1', 'task-received', 'myapp.tasks.add').inc() has been called
     - If the task object in state.tasks exists and has .received set, metrics.number_of_prefetched_tasks increment may have occurred

Implementation notes for reimplementation:
- Subclass celery.events.state.State and call super().__init__ with same signature.
- Initialize counter as a collections.defaultdict(Counter).
- Obtain metrics from a lazily-initialized get_prometheus_metrics() singleton function; if concurrency is expected, ensure safe initialization (module-level lock).
- Implement event(event: dict) to first call super().event(event) then perform the counter and metric updates described above, mirroring the conditional logic for task vs worker events and the prefetch timing logic.

### `flower.events.EventsState.__init__` · *method*

## Summary:
Initializes the EventsState instance by delegating to the parent State initializer, and then creates per-event counters and attaches a shared Prometheus metrics container to the object.

## Description:
This constructor is called when an EventsState object is instantiated (typically during application startup or when the component that tracks Celery events is created). Common callers are the application bootstrap code that creates or wires the event-processing/state object and any factory that wraps or subclasses EventsState.

Lifecycle context:
- Invoked at object construction time to set up in-memory counting structures and to obtain the process-wide Prometheus metrics object before event processing begins.
- The heavy lifting of base-state initialization is delegated to the superclass via super().__init__(*args, **kwargs); this method only adds event-specific fields.

Why this is a separate method:
- It is the canonical object initializer; grouping the setup (base state, counters, metrics) in __init__ keeps construction atomic and ensures the EventsState instance is ready for use immediately after instantiation.
- Obtaining the shared Prometheus metrics via get_prometheus_metrics() at construction centralizes metric attachment and exposes the metrics container on every EventsState instance.

## Args:
    *args: positional arguments forwarded unchanged to the parent class constructor (State.__init__). Valid values and meanings depend on the parent State implementation.
    **kwargs: keyword arguments forwarded unchanged to the parent class constructor (State.__init__). Valid keys and meanings depend on the parent State implementation.

Notes:
- This method does not interpret or validate the forwarded args/kwargs itself; callers must supply arguments appropriate for the superclass constructor.

## Returns:
    None

## Raises:
    Any exception raised by the parent constructor or by get_prometheus_metrics() will propagate out of this __init__. Common examples include:
    - TypeError: if the passed args/kwargs are incompatible with the parent State.__init__ signature.
    - Exception propagated from get_prometheus_metrics(), including:
        * ValueError or TypeError raised during Prometheus metric construction/registration.
        * Any other errors from PrometheusMetrics.__init__ or related code.
    - Any runtime error raised by the collections or underlying standard library used here (unlikely for the shown operations).

## State Changes:
Attributes READ:
    - None explicitly read from self by this method prior to assignment. The parent constructor (super().__init__) may read or initialize attributes; those are implementation details of the superclass and not enumerated here.

Attributes WRITTEN:
    - self.counter: set to a collections.defaultdict whose default factory is the module-level name Counter (i.e., collections.defaultdict(Counter)). The intended behavior is to provide a per-key counter object created on first access.
    - self.metrics: set to the object returned by get_prometheus_metrics(), typically a shared PrometheusMetrics instance.

Additional notes:
    - The parent constructor (super().__init__(*args, **kwargs)) may write additional self.<attr> fields to initialize base-state; those attributes are set by the superclass and are not modified further here.

## Constraints:
Preconditions:
    - The caller must provide args/kwargs suitable for the superclass State.__init__.
    - The module-level function get_prometheus_metrics must be importable/present and able to construct or return a PrometheusMetrics instance. If metric construction is expected to succeed, the Prometheus client must be available and any required configuration (e.g., options) must be valid.

Postconditions:
    - After successful return:
        * self.counter exists and is a collections.defaultdict whose default factory is the module-level Counter callable.
        * self.metrics references the shared PrometheusMetrics instance returned by get_prometheus_metrics().
        * The base class State has been initialized via its constructor.

Important implementation caveat (import/name shadowing):
    - The code sets self.counter = collections.defaultdict(Counter), where Counter resolves to the module-level name Counter. The effective callable used as the defaultdict factory depends on the module's imports at top-level. In the file where both "from collections import Counter" and "from prometheus_client import Counter" appear, the later import may rebind the name Counter to prometheus_client.Counter. To reproduce the intended behavior (per-key counting containers), ensure the defaultdict default factory is the collections.Counter callable (e.g., use collections.Counter or explicitly import/alias it) so that newly created per-key counters behave like Python collections.Counter objects.

## Side Effects:
    - Calls get_prometheus_metrics(), which may:
        * Mutate module-level global state by creating and caching a PrometheusMetrics instance (assigning PROMETHEUS_METRICS).
        * Register Prometheus metric objects in the global/default Prometheus registry (this registration can raise ValueError if duplicate metric names are registered).
        * Raise exceptions that propagate to callers (see Raises).
    - No file, network, or stdout I/O is performed directly by this method; any such side effects are due to PrometheusMetrics construction/registration.

## Usage and reimplementation guidance:
    - When reimplementing, forward all args and kwargs to the superclass __init__ exactly as provided.
    - Create a defaultdict for self.counter with a default factory that constructs an appropriate counter object (preferably collections.Counter to represent event counts).
    - Obtain a process-shared PrometheusMetrics instance via the module-level getter (or another agreed mechanism) and assign it to self.metrics.
    - Consider the concurrency implications of calling get_prometheus_metrics during construction in multi-threaded startup: protect metric initialization with a lock or ensure single-threaded initialization to avoid duplicate metric registration errors.

### `flower.events.EventsState.event` · *method*

## Summary:
Updates internal counters and Prometheus metrics in response to a single Celery event, and delegates basic state update to the base State.event implementation. This method mutates the object's counter mapping and records metrics that reflect worker and task lifecycle events.

## Description:
- Known callers and context:
    - Called by the Celery event processing pipeline whenever an event is received and dispatched to the State instance (i.e., via celery.events.State.event or the EventReceiver loop). It runs during the event-consumption phase of the monitoring pipeline for each incoming event.
- Role and rationale:
    - This method overrides the base event handler to augment the generic state update (performed by super().event(event)) with application-specific counting and Prometheus metric updates. Separating this logic into its own method keeps metric and counter bookkeeping centralized and avoids inlining these concerns in the base state handling or in the event dispatch loop.

## Args:
    event (dict): A mapping representing the event. Expected keys:
        - 'hostname' (str): Name of the worker; required.
        - 'type' (str): Event type string (e.g., 'task-received', 'task-started', 'task-succeeded', 'worker-online', 'worker-heartbeat', 'worker-offline'); required.
        - If event['type'] starts with 'task-':
            - 'uuid' (str): Task identifier; required for task events because the code accesses event['uuid'].
            - Optional keys used with .get(...): 'name' (task name), 'runtime' (float), 'active' (int).
    Notes:
        - Missing optional keys are handled via event.get(...) (defaults shown in the implementation).
        - The method expects event to behave like a dict; passing None or a non-mapping will raise an exception when indexed.

## Returns:
    None

## Raises:
    KeyError: If 'hostname' or 'type' keys are missing from event; or for task events, if 'uuid' is missing (because the implementation uses event['uuid'] directly).
    AttributeError: If event['type'] starts with 'task-' and the task lookup (self.tasks.get(task_id)) returns None, subsequent attribute access (e.g., task.started, task.received, task.eta, task.name) will raise AttributeError.
    TypeError: If event is not a mapping and indexing is attempted (e.g., event['hostname']), a TypeError may be raised by the caller's misuse.

## State Changes:
- Attributes READ:
    - self.counter: read to obtain the per-worker counter mapping (and then updated).
    - self.tasks: consulted with self.tasks.get(task_id) and membership testing (task_id in self.tasks).
    - self.metrics: read to access Prometheus metric collectors (events, runtime, number_of_prefetched_tasks, prefetch_time, worker_online, worker_number_of_currently_executing_tasks).
- Attributes WRITTEN / Mutated:
    - self.counter: increments the count at self.counter[worker_name][event_type] by 1.
    - self.metrics (external objects): mutated via labels(...).inc(), .dec(), .set(), .observe() calls (these are side-effect mutations on the metric collectors, not direct assignment to self.metrics).

## Constraints:
- Preconditions:
    - The object must have attributes:
        - self.counter: mapping-like (supports self.counter[worker_name][event_type] += 1 semantics; e.g., nested defaultdict(Counter) or similar).
        - self.tasks: mapping of task_id -> task object (task object exposes attributes .started, .received, .eta, .name).
        - self.metrics: an object with attributes (.events, .runtime, .number_of_prefetched_tasks, .prefetch_time, .worker_online, .worker_number_of_currently_executing_tasks) that support .labels(...).inc()/dec()/set()/observe() as appropriate.
    - The event argument must be a mapping containing at minimum 'hostname' and 'type'. If type starts with 'task-', 'uuid' must be present.
- Postconditions:
    - After a successful call:
        - self.counter[worker_name][event_type] has been incremented by 1.
        - For task-related events, corresponding Prometheus metrics have been incremented/observed/updated consistent with the event type and available fields:
            - events metric always incremented for task-* events with labels (worker_name, event_type, task_name).
            - runtime metric observed when runtime is present and truthy.
            - number_of_prefetched_tasks incremented for 'task-received' when task has no ETA and task.received is truthy.
            - prefetch_time set/cleared appropriately when a task moves from received -> started -> succeeded/failed without an ETA.
        - For worker lifecycle events, worker_online metric set to 1 (on online/heartbeat) or 0 (on offline); heartbeat may also set the currently executing tasks gauge when the event contains 'active'.

## Side Effects:
- Calls super().event(event): delegates to base class state update, which may mutate other parts of the State (not detailed here).
- Mutates in-memory counters (self.counter) and Prometheus metric objects via labels(...).inc(), .dec(), .set(), .observe().
- No file I/O or network calls are performed directly by this method; the only external interactions are through metric collector objects (which may expose their own I/O in other contexts).
- Possible exceptions (KeyError/AttributeError/TypeError) propagate to the caller if event lacks required keys or the expected task object is missing.

## `flower.events.Events` · *class*

*No documentation generated.*

### `flower.events.Events.__init__` · *method*

## Summary:
Initializes an Events thread instance: configures the background thread, attaches Tornado I/O loop and Celery app, optionally restores a saved EventsState from a shelve database, sets up periodic timers (state-saving and events-enable polling), and constructs an EventsState if none was restored. The call mutates the instance by setting runtime attributes used by the event-processing thread.

## Description:
This constructor is called during component creation/startup when the application prepares the events-consumption thread/worker monitoring component. Typical callers:
- The application or bootstrap code that creates and starts the Events monitoring thread during service startup (for example, code that monitors Celery workers and tasks).
- Any factory that instantiates Events to attach it to a Tornado I/O loop and a Celery app.

This logic is isolated in __init__ because:
- It performs setup work that must run once at object construction (thread base initialization, state restoration, timer creation).
- It performs potentially error-prone I/O (shelve) and object construction (EventsState) that should be clearly separated from the runtime event loop and from other methods that implement event processing or periodic work.
- It establishes instance attributes required by other methods (e.g., save_state, on_enable_events) and timers that should be created deterministically at construction.

## Args:
    capp (celery.Celery): The Celery application instance this Events object will monitor. Required.
    io_loop (tornado.ioloop.IOLoop or compatible): Tornado I/O loop used for PeriodicCallback scheduling. Required.
    db (str | None): Filesystem path to a shelve database file used for persistent state restore/save. Default: None (no persistence).
    persistent (bool): If True, attempt to load Events state from the shelve database at `db`. Default: False.
    enable_events (bool): Whether events are enabled. Stored on the instance for later use. Default: True.
    state_save_interval (int | float): If `persistent` is True and a positive value is provided, used as the PeriodicCallback interval for saving state. Passed as the callback interval argument to tornado.ioloop.PeriodicCallback. Default: 0 (no state-saving timer created).
    **kwargs: Arbitrary keyword arguments forwarded to EventsState when constructing an in-memory state (EventsState(**kwargs)) if no persisted state is restored.

## Returns:
    None

## Raises:
    AttributeError:
        - If self.save_state is not present and `persistent` is True and a state_save_interval truthy value is provided (attribute lookup occurs when creating a PeriodicCallback).
        - If self.on_enable_events or self.events_enable_interval are not defined on the instance or class when creating the events-enable PeriodicCallback (attribute lookup is performed).
    KeyError:
        - When `persistent` is True and the shelve database at `db` does not contain a key 'events', state['events'] will raise KeyError.
    OSError / IOError (or underlying shelve/dbm errors):
        - Any I/O error raised by shelve.open(self.db) (e.g., permission denied, invalid path) will propagate.
    Any exception raised by EventsState(**kwargs):
        - If constructing EventsState fails (for example, Prometheus metric registration errors propagated by EventsState.__init__), that exception propagates out of this constructor.

## State Changes:
Attributes READ:
    - self.db: read to open shelve when persistent is True (value set earlier in this same method).
    - self.persistent: read (checked in the conditional) after being assigned from the constructor arg.
    - self.state (read in the final conditional to decide whether to create an EventsState).
    - self.save_state: attribute lookup performed when creating a PeriodicCallback for state_save_timer (if needed).
    - self.on_enable_events: attribute lookup performed when creating the events-enable PeriodicCallback.
    - self.events_enable_interval: attribute lookup performed to obtain the timer interval for the events-enable PeriodicCallback.
    - module-level logger (used for debug logging when persistent is True)

Attributes WRITTEN:
    - self.daemon (bool): set to True (thread runs as daemon).
    - self.io_loop: assigned to the passed io_loop argument.
    - self.capp: assigned to the passed Celery app.
    - self.db: assigned to the passed db argument.
    - self.persistent: assigned to the passed persistent argument.
    - self.enable_events: assigned to the passed enable_events argument.
    - self.state: assigned either from the shelve ('events' key) when persistent OR to a freshly constructed EventsState(**kwargs).
    - self.state_save_timer: assigned to a tornado.ioloop.PeriodicCallback(self.save_state, state_save_interval) when persistent and state_save_interval is truthy; otherwise left as None.
    - self.timer: assigned to a tornado.ioloop.PeriodicCallback(self.on_enable_events, self.events_enable_interval)

## Constraints:
Preconditions (what must be true before calling):
    - `capp` must be a valid Celery application object suitable for later event consumption logic.
    - `io_loop` must be a compatible Tornado I/O loop (or at least acceptable to PeriodicCallback) because PeriodicCallback objects are constructed and later used with it.
    - If `persistent` is True, `db` should point to a shelve-compatible path that the process can open; otherwise shelve.open will raise an I/O error.
    - The instance (or its class) must define attributes/methods referenced later in __init__:
        * self.save_state (callable) if state_save_interval is truthy and persistent is True.
        * self.on_enable_events (callable).
        * self.events_enable_interval (numeric interval).
      If any of these are missing, __init__ raises AttributeError at attribute lookup time.
Postconditions (what is guaranteed after a successful call):
    - The instance is a daemon Thread with self.daemon == True.
    - self.io_loop and self.capp are set to the provided objects.
    - If a persisted state was successfully read from the shelve under key 'events', self.state references that object.
    - Otherwise, self.state is an EventsState instance constructed with **kwargs.
    - If persistent and state_save_interval truthy: self.state_save_timer is a PeriodicCallback configured to call self.save_state at the supplied interval (but not necessarily started).
    - self.timer is a PeriodicCallback configured to call self.on_enable_events at self.events_enable_interval (but not necessarily started).

## Side Effects:
    - I/O: If `persistent` is True, opens a shelve database file via shelve.open(self.db) (file I/O, possible creation of files).
    - Logging: Emits a debug log message ("Loading state from '%s'...") when persistent is True (module-level logger used).
    - Timer objects: Constructs tornado.ioloop.PeriodicCallback objects (for state save and for events-enable polling). Construction binds bound methods (self.save_state, self.on_enable_events) to callbacks; these objects exist after __init__ but are not started here.
    - Global/Process-level side effects via EventsState construction: if EventsState(**kwargs) executes, it may register Prometheus metrics or perform other global registrations; such side effects occur synchronously during construction and can raise exceptions that propagate.

### `flower.events.Events.start` · *method*

## Summary:
Starts the Events thread and any configured periodic timers, transitioning the Events instance from "not-running" to "running" state.

## Description:
This method performs the final startup steps after an Events instance has been constructed: it delegates to the standard threading.Thread.start to launch the thread (which will execute Events.run) and then starts configured PeriodicCallback timers that drive periodic behavior (enable-events polling and optional state persistence).

Known callers and lifecycle context:
- No explicit call sites are present in the provided class implementation. Typically it is called by the component that instantiates Events when the application or service is starting up and wants background event capture to begin.
- Lifecycle stage: application startup / service initialization — invoked immediately after creating an Events object to begin background event capturing and periodic tasks.

Why this logic is a separate method:
- Starting the thread and timers is a discrete lifecycle action (transitioning the object into active background operation). Keeping it in its own method centralizes startup logic and separates construction (which prepares timers and state) from execution (which actually launches the background processing).

## Args:
    None

## Returns:
    None

## Raises:
    RuntimeError: If threading.Thread.start raises RuntimeError (for example, when start() is called more than once on the same Events instance). This is the direct behavior of the underlying threading.Thread.start call.
    Any exception raised by underlying timer start operations: If self.timer.start() or self.state_save_timer.start() throw an exception, that exception is propagated to the caller (no internal handling is performed in this method).

## State Changes:
Attributes READ:
    self.enable_events
    self.timer
    self.state_save_timer

Attributes WRITTEN:
    None (this method does not assign to any self.<attr> attributes). Note: calling threading.Thread.start changes the internal thread lifecycle state managed by the Python threading module (from not-started to started), but no explicit self attribute is written by this method.

## Constraints:
Preconditions:
    - The Events instance must have been constructed (its __init__ has run), so self.timer is expected to exist (the class sets self.timer in __init__) and self.state_save_timer may be None or a PeriodicCallback.
    - The thread must not have been previously started; otherwise threading.Thread.start will raise RuntimeError.

Postconditions:
    - After successful return, the underlying thread has been started and will execute Events.run in the background.
    - If self.enable_events is truthy at call time, self.timer.start() has been invoked so the enable-events PeriodicCallback is running.
    - If self.state_save_timer is truthy at call time, its start() method has been invoked so state persistence periodic callbacks (if configured) are running.

## Side Effects:
    - Launches a background thread that executes Events.run (begins capturing events once run executes).
    - Starts tornado PeriodicCallback timers:
        - The enable-events timer (self.timer) will begin invoking on_enable_events periodically on the configured IOLoop.
        - The optional state-save timer (self.state_save_timer), if configured, will begin invoking save_state periodically.
    - Emits debug log messages via logger.debug when each timer is started.
    - Any exceptions thrown by the thread/timer startup sequence propagate to the caller.

### `flower.events.Events.stop` · *method*

## Summary:
Stops periodic timers used by the Events thread and persists in-memory state to disk when persistence is enabled. This transitions the Events object toward a stopped/shutdown state without terminating the thread itself.

## Description:
This method performs three coordinated shutdown steps:
1. If event polling is enabled (enable_events is True) it stops the enable-events PeriodicCallback timer so the on_enable_events callback is no longer scheduled.
2. If periodic state saving is configured (state_save_timer is not None) it stops that PeriodicCallback so periodic save_state calls cease.
3. If persistence is enabled (persistent is True) it synchronously writes the current in-memory state to the configured shelve database by calling save_state().

Known callers and context:
- There are no direct callers of stop found within the repository sources examined. It is intended to be invoked during shutdown or cleanup of the Events thread/manager (for example, by higher-level application shutdown logic, supervisor code, or a test harness) to ensure timers are stopped and persistent state is saved before process exit.
- Typical lifecycle placement: called when stopping or unloading the Events component after it has been started (after start() and possibly while run() is running or during application shutdown).

Why this is a separate method:
- Encapsulates the three distinct shutdown responsibilities (timer stop for enable_events, timer stop for state saves, and final state persistence) to make orderly cleanup atomic and reusable from multiple shutdown paths. Keeping this logic in one method avoids duplication and ensures the same shutdown sequence is used everywhere.

## Args:
This method takes no arguments.

## Returns:
None

## Raises:
- This method itself does not catch exceptions from save_state(); therefore any exception raised by save_state() will propagate to the caller when persistent is True. Typical exceptions that may propagate include I/O-related errors thrown by shelve (e.g., file access errors) or any unexpected exception during serialization of self.state.
- No exceptions are explicitly raised by this method when timers are absent; it conditions on attribute truthiness before calling stop().

## State Changes:
Attributes READ:
- self.enable_events — checked to decide whether to stop self.timer.
- self.timer — accessed and .stop() invoked when enable_events is True.
- self.state_save_timer — checked to decide whether to stop periodic saving; .stop() may be invoked.
- self.persistent — checked to decide whether to call save_state().
- self.state — read indirectly by save_state() when persisting (save_state reads self.state).

Attributes WRITTEN:
- None of the Events instance attributes are reassigned by this method. However:
  - Calling self.timer.stop() and self.state_save_timer.stop() may mutate the internal state of those PeriodicCallback objects (external objects reachable from self).
  - save_state() performs external persistence (writes to disk) but does not reassign Events attributes.

## Constraints:
Preconditions:
- The Events object should have been initialized so that:
  - self.timer is present (the __init__ unconditionally creates self.timer).
  - self.state_save_timer may be None or a PeriodicCallback (it will be created only if persistence and a nonzero state_save_interval were provided).
  - If persistent is True, self.db must be a valid path or shelve target such that save_state() can open it for writing; otherwise save_state() may raise.

Postconditions:
- If enable_events was True at call time, self.timer.stop() has been invoked so the enable-events PeriodicCallback will no longer schedule on_enable_events.
- If self.state_save_timer was set, its stop() method has been invoked so periodic state-saving is halted.
- If persistent was True, save_state() has been called and (assuming no exception) the Events state has been written to the shelve file at self.db.
- No Events-instance attributes are reassigned by stop(); callers should not expect attribute values to change other than side effects on referenced timer objects or on-disk state.

## Side Effects:
- Calls to PeriodicCallback.stop() — affects the Tornado I/O loop scheduling (stops future callbacks from being scheduled).
- If persistent is True, save_state() performs file I/O using the shelve module: it opens the shelve at self.db, writes self.state into it, and closes it. This produces persistent storage side effects visible outside the process.
- Exceptions raised during save_state() (e.g., due to file-system errors or serialization problems) will propagate to the caller unless handled externally.
- No network calls are made directly by stop(); however, stopping timers can indirectly affect when network-related callbacks (e.g., on_enable_events) are scheduled.

### `flower.events.Events.run` · *method*

## Summary:
Runs an indefinite event-capture loop that connects to the Celery broker, receives events via a Celery EventReceiver, and dispatches them to the instance's event handler(s); the call continuously tries to reconnect with exponential backoff on errors and only terminates when the process is interrupted.

## Description:
- Known callers and lifecycle stage:
    - Typically used as the main loop for the Events subsystem and invoked when starting the event listener, commonly as the target of a background thread or by an Events.start method during application initialization. It is the long-running work unit that keeps the event stream open and processing.
- Why this logic is a separate method:
    - The method encapsulates the lifecycle of an event-capturing loop: establishing connections, creating the EventReceiver, entering a blocking capture loop, handling disconnections and transient errors with exponential backoff, and managing interrupt behavior. Keeping this behavior in a dedicated method isolates the indefinite capture/reconnect semantics from setup/teardown and from the event-processing handler code (self.on_event), making it easier to run in a dedicated thread and to reason about reconnection/backoff policy.

## Args:
    None

## Returns:
    None
    - Under normal operation the method does not return because it executes a while True loop that repeatedly captures events.
    - The method may only terminate when the process exits (for example after thread.interrupt_main triggers a KeyboardInterrupt in the main thread and the process shuts down) or if the thread is otherwise killed by the runtime/environment. There is no explicit return value.

## Raises:
    None are propagated to callers by this method:
    - The method internally catches KeyboardInterrupt and SystemExit and uses thread.interrupt_main() to signal the main thread; it does not re-raise these exceptions.
    - All other exceptions raised while capturing events are caught, logged, and handled by sleeping for a backoff interval before retrying. Therefore, callers should not expect exceptions from ordinary transient capture failures.

## State Changes:
- Attributes READ:
    - self.capp: used to obtain a broker connection via self.capp.connection() context manager.
    - self.on_event: used as the handler for EventReceiver; EventReceiver will call this callable for incoming events.
- Attributes WRITTEN:
    - None of the method's assignments directly write attributes on self. The method does not assign to any self.<attr> fields.
    - Indirect modifications: calling self.on_event (the handler) may mutate the Events instance state or external objects; such mutations are not performed directly by this method but are side-effects of dispatching events.

## Constraints:
- Preconditions:
    - self.capp must be a Celery application-like object exposing a .connection() context manager that yields a connection usable by celery.events.EventReceiver.
    - self.on_event must be a callable that accepts event dicts as provided by EventReceiver.
    - The runtime environment must allow opening network connections to the message broker.
- Postconditions:
    - After successful invocation, the calling thread will be occupied running an endless event-capture loop until process shutdown or external thread termination.
    - While running, events received from the broker will be dispatched to self.on_event; logging will reflect capture start/failures and backoff behavior.

## Side Effects:
- I/O and network:
    - Opens and holds a connection to the Celery broker (via self.capp.connection()).
    - Uses celery.events.EventReceiver and its capture() method, which blocks while waiting for and consuming broker messages.
- Logging:
    - Emits debug-level and error-level logs describing capture start and failures.
- Thread/process interaction:
    - On KeyboardInterrupt or SystemExit caught inside the loop, the method calls thread.interrupt_main() (attempts to import _thread first, falls back to thread) which raises KeyboardInterrupt in the main thread. This is used to propagate an interrupt to the main thread; it does not raise in this thread.
- Sleep/backoff:
    - Implements exponential backoff on failure by doubling the retry delay (try_interval) after each failed attempt, sleeping for try_interval seconds before retrying, and resetting try_interval to 1 after a successful EventReceiver setup.
- Event dispatch side-effects:
    - The EventReceiver created here is configured with handlers={"*": self.on_event}. Each captured event will be passed to self.on_event, which may mutate internal state, update metrics, or perform I/O (depending on the handler implementation).

## Behavior notes and edge cases:
- Exponential backoff:
    - try_interval starts at 1 second, is doubled at the start of each loop iteration, and is reset to 1 second immediately after successfully constructing the EventReceiver and before calling capture().
    - On any Exception (other than KeyboardInterrupt/SystemExit), the exception is logged and the thread sleeps for try_interval seconds before retrying.
- Interrupt handling:
    - KeyboardInterrupt and SystemExit are caught and handled by calling thread.interrupt_main() to forward the interrupt to the main thread; the capture loop does not re-raise those exceptions itself.
- Blocking semantics:
    - EventReceiver.capture is invoked with limit=None, timeout=None, wakeup=True — it will block until interrupted or an error occurs. Because of this, the method only proceeds to the next loop iteration on capture termination or on exceptions.
- Termination:
    - The method contains an infinite loop and does not provide an internal clean shutdown mechanism; proper shutdown should be driven externally by terminating the process or by causing capture() to exit and the surrounding thread to be killed.

### `flower.events.Events.save_state` · *method*

## Summary:
Persist the in-memory events state to the configured shelve database on disk, overwriting the previous shelve file.

## Description:
Known callers and invocation contexts:
- Created as a PeriodicCallback in Events.__init__ when state_save_interval is provided. In that case the Tornado I/O loop invokes this method periodically to persist state.
- Called from Events.stop() when the Events thread is being stopped and persistence is enabled (self.persistent is True).
- May be invoked directly by other shutdown or maintenance code that wants to persist current state.

Lifecycle stage:
- Invoked during normal runtime on a periodic schedule to create checkpoints of the in-memory state, and during shutdown to ensure a final persisted copy exists.

Why this is its own method:
- The persistence operation is used from multiple places (periodic timer and stop path) and involves multiple steps (open, write, close) and side effects (I/O). Extracting it into a single method avoids duplication, centralizes error handling and semantics (e.g., shelve flag usage), and makes scheduling and testing simpler.

## Args:
This method takes no arguments.

## Returns:
None.

## Raises:
- TypeError: If self.db is None or not an acceptable path-like object; shelve.open will raise a TypeError when given an invalid filename argument.
- OSError / IOError: Propagated when underlying filesystem operations fail (unable to create/open files, permission issues, disk full, etc.).
- pickle.PicklingError (or other exceptions raised by the pickling machinery): If the object assigned to the shelve ('events') cannot be serialized.
- dbm.error or other DB backend errors: Errors propagated from the dbm backend used by shelve when the underlying database cannot be created or written.
Note: The method does not catch exceptions; any exception raised while opening, writing, or closing the shelve will propagate to the caller.

## State Changes:
Attributes READ:
- self.db: path to the shelve database file used as the filename argument to shelve.open.
- self.state: the in-memory EventsState (or whatever object is stored) that will be serialized and stored under the 'events' key.

Attributes WRITTEN:
- None of the object's attributes are modified by this method.

External write:
- The method writes to external storage: it creates/overwrites the shelve database at self.db and writes the key 'events' with the current value of self.state.

## Constraints:
Preconditions:
- self.db must be set to a valid filesystem path (string or path-like) that the process can create/write. If self.db is unset or invalid, shelve.open will raise.
- self.state should be serializable with Python's pickle (i.e., picklable). Non-picklable objects will cause serialization errors.
- Caller should ensure any needed coordination with other threads or the I/O loop to avoid concurrent mutations of self.state during serialization if atomicity is required.

Postconditions:
- On successful return, a shelve database file identified by self.db exists (created or replaced) and contains an entry with key 'events' whose value is a pickled snapshot equal to the value of self.state at the time of assignment.
- Because shelve.open is called with flag='n', the shelve created is a new, empty database; any previous contents at that path are discarded and replaced with the new database containing at least the 'events' key.

## Side Effects:
- Performs synchronous disk I/O: opens a shelve DB, writes data, and closes it. This may block the calling thread while I/O completes.
- Overwrites any existing shelve/database at self.db due to the 'n' flag; previous persisted data will be lost.
- No explicit locking or synchronization is performed; callers are responsible for ensuring thread-safety if other threads or the I/O loop may mutate self.state concurrently.
- Exceptions from I/O or pickling propagate to the caller; there is no internal retry logic or exception swallowing.

## Implementation notes for re-implementation:
- Use shelve.open(self.db, flag='n') to create a fresh database each time, assign the current state object to the 'events' key, and ensure the shelve is closed after writing.
- Keep the method synchronous (no asynchronous constructs) so it can be used both from a periodic callback and from synchronous shutdown code.
- Consider adding external synchronization (locks) around reading self.state if consistent on-disk snapshots are required while other threads may mutate the state.

### `flower.events.Events.on_enable_events` · *method*

## Summary:
Schedules the Celery app's control.enable_events callable to run asynchronously via the object's I/O loop executor; does not modify the Events object's state.

## Description:
This method calls the Events instance's I/O loop method run_in_executor with two arguments: None and self.capp.control.enable_events. It performs no synchronous work besides scheduling that callable and returns immediately.

Known callers and lifecycle stage:
- Registered as the callback for a tornado.ioloop.PeriodicCallback in Events.__init__: the timer is created with PeriodicCallback(self.on_enable_events, self.events_enable_interval).
- The PeriodicCallback is started from Events.start() when self.enable_events is True. Therefore this method is invoked periodically while the Events thread is running and event-enabling is enabled.

Why this logic is a separate method:
- Keeps the PeriodicCallback handler minimal and testable.
- Centralizes the scheduling call (run_in_executor) so executor usage is explicit and easy to modify.

## Args:
    None

## Returns:
    None
    - The method does not return a value; it only schedules the callable. Any result or exception produced when enable_events runs will be handled by the executor/future and does not synchronously propagate through this method.

## Raises:
    - AttributeError or other exceptions raised by attribute access: if self.io_loop or self.capp (or self.capp.control) is not present, attribute access will raise.
    - Any exception raised directly by io_loop.run_in_executor: if the I/O loop implementation raises synchronously when scheduling, that exception will propagate from this call.

Note: Exceptions raised when the scheduled enable_events callable executes in the executor occur asynchronously and are not raised by this method.

## State Changes:
Attributes READ:
    - self.io_loop
    - self.capp
    - self.capp.control
Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - self.io_loop must provide a run_in_executor method that accepts the arguments used here.
    - self.capp must be initialized and have a control attribute exposing an enable_events callable (callable-ness is required for successful scheduling).

Postconditions:
    - A task has been scheduled on the I/O loop's executor to invoke self.capp.control.enable_events with no arguments.
    - No attributes of the Events instance are modified by this method.

## Side Effects:
    - Asynchronously triggers whatever effects control.enable_events produces (for example, requesting that Celery workers send events). Those effects and any I/O/network interactions occur when the scheduled callable runs in the executor, outside the current call frame.

### `flower.events.Events.on_event` · *method*

## Summary:
Schedules the given Celery event to be handled on the Tornado I/O loop by enqueuing a callback that will call the Events' state.event handler, without blocking the caller thread.

## Description:
Known callers and context:
    - EventReceiver (from celery.events) configured in Events.run:
        handlers={"*": self.on_event}
      When the EventReceiver captures an event while the Events thread is running, it invokes this method for each incoming event.
    - Lifecycle: called repeatedly during the background event-capture loop inside Events.run; runs in the Events thread (a background threading.Thread), not on the Tornado I/O loop thread.
Why this is a separate method:
    - Marshals cross-thread execution: it isolates the logic that transfers an event from the background capture thread into the Tornado I/O loop where the shared State is updated.
    - Keeps the EventReceiver handler minimal and non-blocking (avoids performing state mutations directly on the capturing thread).
    - Makes the scheduling behavior easy to override or mock in tests.

## Args:
    event (dict-like):
        - The event payload produced by Celery's EventReceiver (typically a mapping with keys like 'type', 'timestamp', 'uuid', etc.).
        - The method does not validate the event contents; it forwards the object to state.event.

## Returns:
    None
    - The method does not return a value; it only schedules a callback on the I/O loop.

## Raises:
    - AttributeError: If self.io_loop or self.state is not set, or if they lack the expected methods (self.io_loop.add_callback or self.state.event), attribute access will raise AttributeError.
    - Any exception raised synchronously by self.io_loop.add_callback will propagate to the caller. (The method itself does not catch exceptions.)

## State Changes:
    Attributes READ:
        - self.io_loop
        - self.state
    Attributes WRITTEN:
        - None (no attributes of self are modified by this method)

## Constraints:
    Preconditions:
        - self.io_loop must be a valid Tornado I/O loop (or compatible object) exposing an add_callback(callable) method.
        - self.state must be set and must expose an event method that accepts a single argument (the event).
        - Calls are expected to come from the background Events thread (as configured in Events.run), but the method itself does not enforce caller thread.
    Postconditions:
        - A callback is enqueued on the I/O loop that will later invoke self.state.event(event).
        - The Events instance and its attributes remain unchanged immediately after calling this method.

## Side Effects:
    - Schedules execution of state.event(event) on the Tornado I/O loop (cross-thread scheduling). The actual mutation of the EventsState or other side effects occur when that callback runs.
    - No file/network I/O or persistence performed directly by this method.
    - Because execution is deferred to the I/O loop, exceptions raised by state.event will occur asynchronously on the I/O loop thread (unless the I/O loop or callback wrapper surfaces them).

