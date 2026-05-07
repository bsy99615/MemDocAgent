# `flower`

## Repository Overview

### Tree Structure
```
flower/
├── docs/
│   └── tasks.py
├── examples/
│   └── tasks.py
└── flower/
    ├── api/
    │   ├── __init__.py
    │   ├── control.py
    │   ├── tasks.py
    │   └── workers.py
    ├── utils/
    │   ├── __init__.py
    │   ├── broker.py
    │   ├── search.py
    │   ├── tasks.py
    │   └── template.py
    ├── views/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── broker.py
    │   ├── error.py
    │   ├── monitor.py
    │   ├── tasks.py
    │   └── workers.py
    ├── __main__.py
    ├── app.py
    ├── command.py
    ├── events.py
    ├── inspector.py
    └── ...
```

### Purpose
Flower is a web-based monitoring tool for Celery distributed task queues. It provides real-time monitoring of worker status, task execution, and broker information through both a web interface and RESTful API endpoints. The tool helps developers and system administrators track and debug distributed task processing workflows.

Target users include:
- Developers working with Celery task queues
- System administrators monitoring distributed systems
- DevOps engineers managing task infrastructure

Flower positions itself as a standalone monitoring service that integrates seamlessly with existing Celery deployments, offering both visual dashboards and programmatic access to monitoring data.

### Architecture
```mermaid
flowchart TD
    A[Celery Workers] --> B[Broker (Redis/RabbitMQ)]
    B --> C[Flower Monitor]
    C --> D[Web Interface]
    C --> E[REST API]
    C --> F[Prometheus Metrics]
    G[External Tools] --> H[Flower API]
    H --> F
```

Key architectural patterns:
- **Event-driven architecture**: Uses Celery's event system for real-time monitoring
- **Separation of concerns**: Clear division between web interface, API, and backend services
- **Plugin-like structure**: Modular components that can be extended or replaced
- **Observability-first design**: Built-in Prometheus metrics for monitoring and alerting

### Entry Points
1. **CLI Command**: `flower` - Launches the monitoring web server with default settings
2. **Importable API**: `from flower import Flower` - Programmatic access to monitoring features
3. **Web Interface**: Accessible via browser at `http://localhost:5555` by default
4. **REST API**: Available at `/api/` endpoints for programmatic monitoring

### Core Features
- Real-time worker monitoring and status tracking
- Task execution visualization and performance metrics
- Broker information and queue monitoring
- Web-based dashboard with interactive charts
- RESTful API for programmatic access
- Prometheus metrics export for advanced monitoring
- Authentication and authorization support
- Task filtering and search capabilities

### Dependencies
- **Celery**: Core integration with distributed task queues
- **Tornado**: Web framework for serving HTTP requests
- **Prometheus Client**: Metrics collection and exposition
- **Redis**: Optional broker connectivity (when using Redis)
- **Humanize**: Human-readable time formatting
- **Python Standard Library**: Core utilities and networking

### Configuration
Flower supports configuration through:
- Command-line arguments
- Environment variables
- Configuration files (YAML/JSON)
- Celery configuration integration

### Extension Points
- **API Extensions**: Add custom endpoints in `flower/api/`
- **View Customization**: Extend web interface in `flower/views/`
- **Utility Functions**: Add new utilities in `flower/utils/`
- **Event Processing**: Customize event handling in `flower/events.py`
- **Inspector Plugins**: Extend worker information collection

### Module Responsibilities
- **flower.api**: RESTful API endpoints for controlling and monitoring Celery workers and tasks
- **flower.utils**: Supporting utilities for broker connectivity, task filtering, and data formatting
- **flower.views**: Web interface components for displaying monitoring information
- **flower.events**: Background thread that captures and processes Celery events for real-time monitoring
- **flower.inspector**: Worker information collector that queries Celery workers for status and statistics
- **flower.app**: Main application controller coordinating Celery integration, event monitoring, and web server hosting
- **docs/**: Example computational tasks for demonstrating task execution patterns
- **examples/**: Fundamental utility functions for distributed task processing and simulation

---

## Modules

- [`docs`](docs.md)
- [`examples`](examples.md)
- [`flower`](flower.md)
- [`flower/api`](flower/api.md)
- [`flower/utils`](flower/utils.md)
- [`flower/views`](flower/views.md)

