# `broker.py`

## `flower.views.broker.BrokerView` · *class*

## Summary:
Handle HTTP GET requests for the broker status page: construct a utils.broker.Broker helper from application configuration, asynchronously fetch metadata for active queues, and render the "broker.html" template with broker connection URL and fetched queue data.

## Description:
BrokerView is a Tornado request handler method (the GET handler) responsible for producing the broker overview page in the web UI. Tornado instantiates the handler and calls this async get() method when an authenticated client requests the route mapped to this view.

Typical scenario:
- Tornado routes an incoming GET /broker (or equivalent) request to BrokerView.
- Tornado's authentication machinery (web.authenticated) runs first; only authenticated requests execute the method body.
- The handler inspects the application configuration to determine whether to provide an HTTP broker API URL to the Broker helper (only when transport == 'amqp' and app.options.broker_api is truthy).
- The handler creates a Broker instance using app.capp.connection(...).as_uri(include_password=True) and other capp configuration values.
- It awaits broker.queues(names) to obtain queue metadata for active queues (names obtained from self.get_active_queue_names()).
- Finally it calls self.render("broker.html", broker_url=..., queues=...) to produce the HTTP response.

Responsibility boundary:
- BrokerView glues Tornado request handling, Broker factory usage, and template rendering. It does not implement broker protocol details (delegated to utils.broker.Broker and its concrete backends), nor does it manage long-lived broker connections or explicit broker cleanup.

Known callers / instantiation:
- Tornado web framework: instantiated per-request by Tornado and called as part of request handling.
- The get() method is a coroutine invoked by Tornado; it is decorated with tornado.web.authenticated so callers must be authenticated.

## State:
BrokerView does not declare instance attributes of its own. It depends on attributes provided by BaseHandler/Tornado:

- self.application (object, required)
    - transport (str): e.g., 'amqp', 'redis', etc. Used to decide whether to use broker HTTP API settings.
    - options (object): must have broker_api attribute (string or falsy).
    - capp (object): application-level Celery/AMQP helper used below.

- self.capp (object, required)
    - connection(connect_timeout: float = ...) -> connection_obj: connection_obj must implement as_uri(include_password: bool = ...) -> str.
    - conf (object): must have attributes:
        - broker_transport_options: passed to Broker(...) as broker_options (opaque mapping/structure forwarded to broker implementations).
        - broker_use_ssl: boolean or config forwarded to Broker as broker_use_ssl.

- self.get_active_queue_names() (callable, required)
    - Called without arguments; must return an iterable/list of queue names acceptable to Broker.queues(names).

- utils.broker.Broker (factory/class, required)
    - Broker(broker_url: str, http_api: Optional[str] = None, broker_options: Any = None, broker_use_ssl: Any = None)
        - May raise NotImplementedError if the URL scheme is unsupported.
    - The instance returned must implement:
        - async def queues(self, names): awaitable returning queue metadata (iterable/sequence). The exact metadata shape depends on concrete broker backend.

- logger (module-level logger)
    - Used for error logging when Broker.queues raises an exception: logger.error("Unable to get queues: '%s'", e)

Invariants and constraints:
- self.application and self.capp must be present and consistent; the code assumes app.capp and self.capp refer to valid objects exposing the described methods/attributes.
- The Broker constructor must accept a URI that can include a password when include_password=True is passed to as_uri.
- The template "broker.html" must accept context variables:
    - broker_url (str)
    - queues (iterable/sequence or None)

## Lifecycle:
Creation:
- BrokerView is not constructed manually in application code; Tornado creates instances per-request using BaseHandler's constructor. BrokerView defines no __init__ and therefore inherits BaseHandler construction semantics.

Usage (typical call sequence):
1. Tornado authenticates the request due to @web.authenticated.
2. BrokerView.get(self) is invoked (async coroutine).
3. Local variable app = self.application is read.
4. Determine http_api:
    - If app.transport == 'amqp' and app.options.broker_api is truthy, set http_api = app.options.broker_api
    - Else http_api = None
5. Construct Broker instance:
    - broker = Broker(app.capp.connection(connect_timeout=1.0).as_uri(include_password=True), http_api=http_api, broker_options=self.capp.conf.broker_transport_options, broker_use_ssl=self.capp.conf.broker_use_ssl)
    - If Broker(...) raises NotImplementedError, translate to tornado.web.HTTPError(404, "'<transport>' broker is not supported") and abort processing.
6. Fetch queues:
    - queues = await broker.queues(self.get_active_queue_names())
    - If broker.queues raises any exception, it is caught, logged, and the code continues to rendering (see "Known issue" below).
7. Render template:
    - self.render("broker.html", broker_url=app.capp.connection().as_uri(), queues=queues)

Destruction / cleanup:
- BrokerView itself has no cleanup logic. If the concrete Broker implementation requires explicit cleanup (close/disconnect), BrokerView does not call it — it delegates lifecycle management to callers or expects short-lived helpers.

Sequencing requirements:
- get() is an async coroutine and must be awaited by Tornado — developers must not call it from synchronous contexts without awaiting.
- Authentication must succeed before get() body runs due to web.authenticated decorator.

## Method Map:
graph TD
    G[Incoming GET request] --> A[web.authenticated decorator verifies auth]
    A --> B[BrokerView.get()]
    B --> C{determine http_api from app.transport & app.options.broker_api}
    C --> D[Create Broker(...) using app.capp.connection(...).as_uri(include_password=True)]
    D --> E{Broker.__new__ may raise NotImplementedError}
    E -->|NotImplementedError| F[raise tornado.web.HTTPError(404, "'<transport>' broker is not supported")]
    E -->|OK| H[await broker.queues(self.get_active_queue_names())]
    H -->|exception| I[logger.error("Unable to get queues: '%s'", e)] --> J[self.render("broker.html", broker_url=..., queues=queues?) (queues may be undefined)]
    H -->|success| J[self.render("broker.html", broker_url=..., queues=queues)]

Notes:
- The diagram highlights the call dependency: get() -> Broker(...) -> broker.queues(...) -> render(...).
- The path where broker.queues raises an exception leads to logging then rendering; because queues may not be set in that path, rendering can raise UnboundLocalError.

## Raises:
- tornado.web.HTTPError(404)
    - Triggered when Broker(...) construction raises NotImplementedError indicating the configured app.transport is unsupported. Message is "'<transport>' broker is not supported".
- UnboundLocalError (possible runtime bug)
    - If broker.queues(...) raises an exception, the code logs the error but does not set a fallback for queues; the subsequent self.render(...) call will reference queues and may raise UnboundLocalError. This is a defect in the method as written.
- Other exceptions from Broker(...) construction (other than NotImplementedError), Broker.queues(...), self.capp.connection().as_uri(), or self.render(...) are not caught here and will propagate; in Tornado they generally result in a 500 response unless handled upstream.

## Example (behavioral, step-by-step):
1. A user visits the broker UI route:
   - Tornado routes the request to BrokerView and ensures the request is authenticated due to @web.authenticated.
2. The handler executes get():
   - app = self.application
   - If app.transport == 'amqp' and app.options.broker_api: http_api is set to that value; otherwise http_api = None.
   - Broker is constructed with the full connection URI including password retrieved from app.capp.connection(connect_timeout=1.0).as_uri(include_password=True) and with broker options taken from self.capp.conf.
   - If the transport is unsupported, a 404 HTTPError is raised.
3. The handler awaits broker.queues(self.get_active_queue_names()):
   - On success: queues receives the returned metadata, and the handler calls self.render("broker.html", broker_url=app.capp.connection().as_uri(), queues=queues) to produce the page.
   - On failure (broker.queues raises): the failure is logged; unless the calling code is changed to provide a fallback value for queues, rendering may raise UnboundLocalError.

Implementation notes / Recommendations:
- Initialize queues to a safe default (e.g., an empty list) before the try/except that awaits broker.queues to avoid UnboundLocalError and to present a sensible UI when queue metadata retrieval fails.
- Consider closing or disconnecting the broker instance if the concrete implementation opens connections that should be cleaned up; currently BrokerView makes no attempt to clean up broker objects.
- Prefer consistent use of app.capp vs self.capp; the code reads capp from both app.capp and self.capp — ensure they refer to the same object in the runtime environment or standardize to one to avoid subtle bugs.
- If exposing the broker URI in the UI is sensitive, verify whether app.capp.connection().as_uri() (without include_password) hides credentials; the Broker helper is intentionally given an as_uri with include_password=True — ensure this is acceptable for your deployment.

### `flower.views.broker.BrokerView.get` · *method*

## Summary:
Handle an incoming HTTP GET request for the broker status page: create a Broker helper using application configuration, asynchronously fetch metadata for the active queues, and render the "broker.html" template with the broker URL and queue data. This method does not mutate handler state; it produces an HTTP response.

## Description:
- Known callers and invocation context:
    - Invoked by the Tornado web framework when a GET request is routed to the BrokerView handler. This occurs during the request-handling phase of the web UI (when a user visits the broker page).
    - Execution lifecycle: request arrival → build Broker helper → await Broker.queues(...) → render response or propagate/handle errors.

- Why this is a dedicated method:
    - It implements the HTTP GET handler for the BrokerView. Tornado expects a method named get to handle GET requests, so the logic is placed here to keep request handling, asynchronous I/O, error translation (to HTTP errors), and template rendering together in the canonical handler method.

## Args:
- None (method signature only uses self).

## Returns:
- None (no Python return value).
    - Observable result: writes an HTTP response by calling self.render("broker.html", broker_url=..., queues=...).
    - broker_url (context passed to template): a string produced by calling app.capp.connection().as_uri() — expected to be a URI (string).
    - queues (context passed to template): value returned by Broker.queues(...); expected to be an iterable/sequence of queue metadata objects (exact shape depends on utils.broker.Broker).

## Raises:
- tornado.web.HTTPError(404)
    - Triggered when constructing Broker(...) raises NotImplementedError. The HTTPError message is "'<transport>' broker is not supported" where <transport> is app.transport.
- Uncaught exceptions from Broker(...) construction (other than NotImplementedError)
    - These are not caught here and will propagate (typically resulting in a 500 error from Tornado).
- Potential UnboundLocalError (runtime)
    - If Broker.queues(...) raises an exception, the code logs the error but does not assign a fallback value to queues; the later reference to queues in self.render may raise UnboundLocalError. This is an implementation bug/risk present in the method.
- Any exceptions raised by self.render(...) or self.capp.connection().as_uri() may propagate (not explicitly handled here).

## State Changes:
- Attributes READ:
    - self.application (aliased to local app):
        - app.transport: used to decide whether to use broker API settings.
        - app.options.broker_api: checked to set http_api when app.transport == 'amqp'.
        - app.capp: used to call connection(connect_timeout=1.0).as_uri(include_password=True) for Broker construction and later app.capp.connection().as_uri() for template context.
    - self.capp:
        - self.capp.conf.broker_transport_options: passed into Broker(...) as broker_options.
        - self.capp.conf.broker_use_ssl: passed into Broker(...) as broker_use_ssl.
        - self.capp.connection().as_uri(): used to populate broker_url for the template.
    - self.get_active_queue_names(): invoked to obtain the list/iterable of active queue names passed to Broker.queues(...).
    - Broker.queues(...): awaited to retrieve queue metadata (external async I/O).
    - self.render(...): called to render and write the HTTP response.
- Attributes WRITTEN:
    - None. The method does not assign to any self.<attr> attributes.

## Constraints:
- Preconditions (requirements before calling):
    - self.application must exist and provide:
        - transport (string-like) and options with attribute broker_api (truthy/falsy) accessible.
        - a capp object with a connection(...) method and conf attributes.
    - self.capp must exist and provide:
        - connection(connect_timeout=...) that returns an object with as_uri(include_password=...) method returning a string.
        - conf with attributes broker_transport_options and broker_use_ssl.
    - utils.broker.Broker must be importable and implement:
        - __init__(uri, http_api=..., broker_options=..., broker_use_ssl=...) — may raise NotImplementedError for unsupported transports.
        - async def queues(names): an awaitable method returning queue metadata.
    - The template "broker.html" must exist and accept context variables broker_url and queues.
- Postconditions (guarantees after call if no exceptions):
    - On successful Broker construction and queue retrieval: the HTTP response has been rendered with "broker.html" and includes broker_url (string) and queues (the value returned by Broker.queues).
    - On NotImplementedError from Broker construction: the method raises tornado.web.HTTPError(404) and does not render the template.
    - If Broker.queues raises an exception: the exception is logged and rendering may fail (UnboundLocalError) unless the implementation is changed to supply a fallback queues value.

## Side Effects:
- Network/IO:
    - Broker(...) construction may perform initialization that touches the network or prepares clients; Broker.queues(...) is awaited and will perform external I/O (e.g., HTTP calls or AMQP queries) to retrieve queue metadata.
    - The method calls as_uri(include_password=True) when constructing the Broker — this intentionally includes credentials in the URI passed to the Broker helper.
    - The broker_url passed to the template is produced by app.capp.connection().as_uri() (called without include_password in the second call), which may hide credentials depending on the as_uri default behavior.
- Logging:
    - On exception while fetching queues, the method logs an error via logger.error("Unable to get queues: '%s'", e).
- HTTP response:
    - Calls self.render("broker.html", ...) which writes the rendered HTML to the HTTP response body.

## Implementation notes, issues, and recommendations:
- http_api selection:
    - http_api is set only when app.transport == 'amqp' AND app.options.broker_api is truthy. In all other cases http_api remains None. The value of app.options.broker_api is likely a URL string for a broker HTTP API.
- Mixed use of app.capp and self.capp:
    - The code reads the capp object via both app.capp (for Broker construction) and self.capp (for conf access). If app.capp and self.capp differ, behavior may be inconsistent. Ensure they reference the same application component or standardize usage to one.
- UnboundLocalError risk:
    - Because queues is only assigned inside the try block that awaits broker.queues(...), if that await raises an exception the except only logs the error and does not set queues to a fallback value. The subsequent self.render(...) unconditionally references queues and may raise UnboundLocalError. Fix by initializing queues to a safe default (e.g., queues = []) before the try/except or by setting queues = None in the except handler.
- Error handling policy:
    - Only NotImplementedError from Broker construction is translated to HTTP 404. Other errors during Broker construction or rendering propagate as 500s. If you want more graceful error pages, catch and map other exceptions to appropriate HTTPError responses.
- Example failure behaviors (observed from code):
    - Unsupported transport: Broker(...) raises NotImplementedError → method raises tornado.web.HTTPError(404) with message "'<transport>' broker is not supported".
    - Broker.queues raises exception: logs error and likely raises UnboundLocalError at render time unless code is updated to set a fallback queues value.

