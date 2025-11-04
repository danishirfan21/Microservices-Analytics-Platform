# Architecture Documentation

## Overview

This microservices platform follows a distributed architecture pattern with separate services for user management and analytics, enabling independent scaling and deployment.

## Core Principles

1. **Separation of Concerns**: Each service has a single responsibility
2. **Service Independence**: Services can be deployed and scaled independently
3. **API-First Design**: All communication happens through well-defined REST APIs
4. **Database per Service**: Each service owns its database
5. **Observability**: Built-in monitoring and metrics collection

## Service Architecture

### User Service

**Purpose**: Manages user authentication, authorization, and profile data

**Key Components**:
- **FastAPI Application**: Main application server
- **JWT Authentication**: Stateless authentication using JSON Web Tokens
- **PostgreSQL Database**: Stores user data with proper indexing
- **Password Hashing**: Bcrypt for secure password storage
- **Event Publishing**: Sends events to Analytics Service

**API Endpoints**:
- Authentication: `/token`, `/login`
- User Management: `/users/*`
- Health Check: `/health`
- Metrics: `/metrics`

**Database Schema**:
```sql
users (
    id: INTEGER PRIMARY KEY,
    email: VARCHAR UNIQUE,
    username: VARCHAR UNIQUE,
    hashed_password: VARCHAR,
    full_name: VARCHAR,
    is_active: BOOLEAN,
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)
```

### Analytics Service

**Purpose**: Tracks user events and provides analytics summaries

**Key Components**:
- **FastAPI Application**: Main application server
- **PostgreSQL Database**: Stores event data
- **Aggregation Engine**: Real-time analytics computation
- **Date Range Filtering**: Flexible time-based queries

**API Endpoints**:
- Event Tracking: `/analytics/events`
- Analytics: `/analytics/summary`, `/analytics/events/by-type`
- Date Range: `/analytics/events/date-range`
- User Events: `/analytics/users/{user_id}/events`

**Database Schema**:
```sql
events (
    id: INTEGER PRIMARY KEY,
    event_type: VARCHAR,
    user_id: INTEGER,
    metadata: JSON,
    created_at: TIMESTAMP
)
```

### Frontend Dashboard

**Purpose**: User interface for authentication and analytics visualization

**Key Components**:
- **React Application**: Single-page application
- **Authentication Module**: Login/register with JWT token storage
- **Dashboard Component**: Analytics visualization
- **Chart Library**: Recharts for data visualization
- **HTTP Client**: Axios for API communication

**Features**:
- User registration and login
- Real-time analytics display
- Interactive charts (pie, bar)
- Date range filtering
- Responsive design

## Communication Patterns

### Synchronous Communication (REST)

1. **Frontend → User Service**
   - User registration
   - Authentication
   - Profile management

2. **Frontend → Analytics Service**
   - Fetch analytics data
   - View event history

3. **User Service → Analytics Service**
   - Send user events (fire-and-forget)
   - Non-blocking HTTP requests

### Event Flow

```
User Action → User Service → Analytics Service → Database → Dashboard
```

Example: User Login
1. User submits login credentials to Frontend
2. Frontend sends POST to User Service `/login`
3. User Service validates credentials
4. User Service sends event to Analytics Service
5. Analytics Service stores event
6. User Service returns JWT to Frontend
7. Dashboard fetches updated analytics

## Data Flow

### Write Path

```
Client Request → API Gateway → Service → Database → Response
```

1. Request validation (Pydantic schemas)
2. Business logic processing
3. Database transaction
4. Event emission (async)
5. Response serialization

### Read Path

```
Client Request → Service → Database Query → Aggregation → Response
```

1. Query parameter validation
2. Database query with filters
3. In-memory aggregation
4. Response caching (optional)
5. JSON serialization

## Security Architecture

### Authentication Flow

```
1. User → POST /login → User Service
2. User Service validates credentials
3. User Service generates JWT token
4. JWT returned to client
5. Client includes JWT in Authorization header
6. User Service validates JWT for protected routes
```

### Security Layers

1. **Transport Security**: HTTPS in production
2. **Authentication**: JWT tokens with expiration
3. **Authorization**: Route-level access control
4. **Input Validation**: Pydantic schemas
5. **SQL Injection Protection**: SQLAlchemy ORM
6. **Password Security**: Bcrypt hashing
7. **CORS**: Configured middleware

## Scalability

### Horizontal Scaling

Each service can scale independently:

```
Load Balancer
    ├─ User Service Instance 1
    ├─ User Service Instance 2
    └─ User Service Instance N

Load Balancer
    ├─ Analytics Service Instance 1
    ├─ Analytics Service Instance 2
    └─ Analytics Service Instance N
```

### Database Scaling

- **Read Replicas**: For analytics queries
- **Connection Pooling**: SQLAlchemy manages connections
- **Indexing**: Proper indexes on frequently queried columns

### Caching Strategy (Future)

- **Application Cache**: Redis for session data
- **Query Cache**: Cache analytics results
- **CDN**: Static assets for frontend

## Monitoring and Observability

### Metrics Collection

Prometheus scrapes metrics from:
- User Service: Request rates, latencies, errors
- Analytics Service: Event processing rates, query performance
- System Metrics: CPU, memory, disk usage

### Logging

Structured logging with:
- Service name
- Request ID
- User ID
- Timestamp
- Log level
- Message

### Health Checks

Each service exposes:
- `/health`: Service health status
- `/metrics`: Prometheus metrics

## Deployment Architecture

### Docker Compose (Development)

```
┌─────────────────────────────────────┐
│      Docker Compose Network         │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │ User DB  │  │Analytics │       │
│  │          │  │   DB     │       │
│  └────┬─────┘  └─────┬────┘       │
│       │              │             │
│  ┌────▼─────┐  ┌────▼──────┐     │
│  │  User    │  │Analytics  │     │
│  │ Service  │◄─┤  Service  │     │
│  └────┬─────┘  └─────┬─────┘     │
│       │              │             │
│       └──────┬───────┘             │
│              │                     │
│         ┌────▼────┐                │
│         │Frontend │                │
│         └─────────┘                │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │Prometheus│  │ Grafana  │       │
│  └──────────┘  └──────────┘       │
└─────────────────────────────────────┘
```

### Kubernetes (Production)

```
Namespace: microservices-analytics

StatefulSets:
  - user-db (PostgreSQL)
  - analytics-db (PostgreSQL)

Deployments (Replicas: 2):
  - user-service
  - analytics-service
  - frontend

Services:
  - user-service (LoadBalancer)
  - analytics-service (LoadBalancer)
  - frontend (LoadBalancer)
  - user-db (ClusterIP)
  - analytics-db (ClusterIP)

ConfigMaps & Secrets:
  - Service configuration
  - Database credentials
  - JWT secrets
```

## Design Decisions

### Why Separate Services?

1. **Independent Scaling**: Analytics can scale separately from user management
2. **Fault Isolation**: User service remains operational if analytics fails
3. **Technology Flexibility**: Each service can use different tech stack
4. **Team Autonomy**: Different teams can own different services

### Why PostgreSQL?

1. **ACID Compliance**: Data integrity for user data
2. **Rich Querying**: Complex analytics queries with SQL
3. **JSON Support**: Flexible metadata storage
4. **Proven Technology**: Battle-tested in production

### Why JWT?

1. **Stateless**: No server-side session storage
2. **Scalable**: Works across multiple service instances
3. **Standard**: Industry-standard authentication
4. **Self-contained**: Contains all necessary user info

### Why REST over gRPC?

1. **Simplicity**: Easier to debug and test
2. **Browser Support**: Direct frontend integration
3. **Tooling**: Rich ecosystem of tools
4. **Human Readable**: JSON responses easy to understand

## Future Architecture Enhancements

1. **API Gateway**: Single entry point with Kong/Traefik
2. **Service Mesh**: Istio for advanced traffic management
3. **Message Queue**: RabbitMQ/Kafka for async communication
4. **Distributed Tracing**: Jaeger for request tracing
5. **Circuit Breaker**: Resilience patterns with Hystrix
6. **Rate Limiting**: API throttling per user/IP
7. **Caching Layer**: Redis for session and query caching
8. **GraphQL**: Flexible data fetching for frontend

## Performance Considerations

### Database Optimization

- Indexes on frequently queried columns
- Connection pooling (SQLAlchemy)
- Query optimization with EXPLAIN ANALYZE
- Pagination for large result sets

### API Performance

- Response compression (gzip)
- Field selection (sparse fieldsets)
- Async I/O (FastAPI with uvicorn)
- Request batching for bulk operations

### Frontend Performance

- Code splitting (React lazy loading)
- Asset optimization (minification, compression)
- CDN for static assets
- Client-side caching

## Testing Strategy

### Unit Tests

- Service logic without external dependencies
- Use in-memory SQLite for database tests
- Mock external service calls

### Integration Tests

- Test service-to-service communication
- Use test databases
- Test with Docker Compose

### End-to-End Tests

- Test complete user flows
- Browser automation with Selenium
- Test in staging environment

## Disaster Recovery

### Backup Strategy

1. **Database Backups**: Automated PostgreSQL backups
2. **Point-in-Time Recovery**: Transaction log archiving
3. **Configuration Backup**: Git repository for all configs

### Recovery Procedures

1. **Service Failure**: Kubernetes auto-restart
2. **Database Failure**: Restore from backup
3. **Complete Outage**: Deploy to new cluster from manifests

## Conclusion

This architecture provides a solid foundation for a scalable, maintainable microservices platform while remaining simple enough for small teams to manage effectively.
