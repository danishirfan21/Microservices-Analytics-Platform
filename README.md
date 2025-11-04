# Microservices Analytics Platform

A production-ready microservices platform built with FastAPI for backend services, React for visualization, and Docker/Kubernetes for orchestration. The platform simulates a small-scale analytics system with separate microservices communicating over REST.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                  Analytics Dashboard (Port 3000)                 │
└────────────────┬────────────────────────────────┬───────────────┘
                 │                                │
                 │                                │
                 ▼                                ▼
┌────────────────────────────────┐  ┌───────────────────────────────┐
│     User Service (FastAPI)     │  │  Analytics Service (FastAPI)  │
│          Port 8000              │◄─┤         Port 8001             │
│                                 │  │                               │
│  - User Registration            │  │  - Event Tracking             │
│  - JWT Authentication           │  │  - Analytics Aggregation      │
│  - CRUD Operations              │  │  - Summary Reports            │
│  - Profile Management           │  │  - Date Range Filtering       │
└────────────┬───────────────────┘  └──────────┬────────────────────┘
             │                                   │
             ▼                                   ▼
┌────────────────────────────────┐  ┌───────────────────────────────┐
│   PostgreSQL (User DB)         │  │  PostgreSQL (Analytics DB)    │
│         Port 5432               │  │         Port 5433             │
└────────────────────────────────┘  └───────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                             │
│                                                                   │
│  Prometheus (Port 9090)  ──►  Grafana (Port 3001)               │
│  - Metrics Collection         - Visualization                    │
│  - Time-series Database       - Dashboards                       │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### User Service
- User registration and authentication
- JWT-based authentication with secure password hashing
- CRUD operations for user profiles
- Input validation with Pydantic
- Event tracking integration with Analytics Service
- PostgreSQL database with SQLAlchemy ORM

### Analytics Service
- User activity event tracking
- Real-time analytics aggregation:
  - Total users count
  - Active users (last 24 hours)
  - Event type distribution
  - Date range filtering
- REST endpoints for analytics summaries
- Integration with User Service

### Frontend Dashboard
- Modern React-based UI
- User authentication (login/register)
- Real-time analytics visualization with Recharts:
  - Pie charts for event distribution
  - Bar charts for event counts
  - Statistical cards for key metrics
- Date range filtering
- Responsive design for mobile and desktop

### Infrastructure
- Docker containers for all services
- Docker Compose for local orchestration
- Kubernetes manifests for production deployment
- Prometheus for metrics collection
- Grafana for monitoring dashboards
- Comprehensive unit tests with pytest

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Relational database
- **Pydantic**: Data validation
- **Python-Jose**: JWT token handling
- **Passlib**: Password hashing
- **Pytest**: Testing framework

### Frontend
- **React 18**: UI framework
- **Recharts**: Charting library
- **Axios**: HTTP client
- **date-fns**: Date manipulation

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Kubernetes**: Container orchestration
- **Prometheus**: Metrics and monitoring
- **Grafana**: Visualization and dashboards

## Prerequisites

- Docker and Docker Compose (for local development)
- Node.js 18+ and npm (for frontend development)
- Python 3.11+ (for backend development)
- kubectl and Kubernetes cluster (for Kubernetes deployment)

## Local Setup with Docker Compose

### 1. Clone the repository

```bash
cd "Microservices Analytics Platform"
```

### 2. Start all services

```bash
docker-compose up --build
```

This will start:
- User Service: http://localhost:8000
- Analytics Service: http://localhost:8001
- Frontend: http://localhost:3000
- PostgreSQL databases (ports 5432 and 5433)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

### 3. Access the services

- **Frontend Dashboard**: http://localhost:3000
- **User Service API Docs**: http://localhost:8000/docs
- **Analytics Service API Docs**: http://localhost:8001/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### 4. Test the platform

1. Open http://localhost:3000
2. Register a new user account
3. Login with your credentials
4. View the analytics dashboard with charts and metrics

## Development Setup

### User Service

```bash
cd user-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run tests
pytest

# Run the service
uvicorn app.main:app --reload --port 8000
```

### Analytics Service

```bash
cd analytics-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run tests
pytest

# Run the service
uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Run development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Running Tests

### User Service Tests

```bash
cd user-service
pytest -v
```

Test coverage includes:
- Authentication (password hashing, JWT tokens)
- User CRUD operations
- Authorization checks
- Input validation

### Analytics Service Tests

```bash
cd analytics-service
pytest -v
```

Test coverage includes:
- Event creation and retrieval
- Analytics aggregation
- Filtering and pagination
- Date range queries

## Kubernetes Deployment

### 1. Create namespace

```bash
kubectl apply -f kubernetes/namespace.yaml
```

### 2. Deploy using Kustomize

```bash
kubectl apply -k kubernetes/
```

### 3. Verify deployment

```bash
kubectl get all -n microservices-analytics
```

### 4. Access services

```bash
# Get external IPs
kubectl get services -n microservices-analytics

# User Service
kubectl port-forward -n microservices-analytics svc/user-service 8000:8000

# Analytics Service
kubectl port-forward -n microservices-analytics svc/analytics-service 8001:8001

# Frontend
kubectl port-forward -n microservices-analytics svc/frontend 3000:80
```

## API Documentation

### User Service Endpoints

#### Authentication
- `POST /token` - Get JWT token (OAuth2 password flow)
- `POST /login` - Login with JSON body

#### Users
- `POST /users/` - Register new user
- `GET /users/` - Get all users (authenticated)
- `GET /users/me` - Get current user profile
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user profile
- `DELETE /users/{user_id}` - Delete user

#### Health
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

### Analytics Service Endpoints

#### Events
- `POST /analytics/events` - Create new event
- `GET /analytics/events` - Get all events (with filters)
- `GET /analytics/events/by-type` - Get event counts by type
- `GET /analytics/events/date-range` - Get analytics for date range
- `GET /analytics/users/{user_id}/events` - Get events for specific user

#### Analytics
- `GET /analytics/summary` - Get overall analytics summary

#### Health
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Monitoring

### Prometheus

Access Prometheus at http://localhost:9090

Available metrics:
- HTTP request duration
- Request count by endpoint
- Active requests
- System metrics (CPU, memory)

### Grafana

Access Grafana at http://localhost:3001
- Username: `admin`
- Password: `admin`

Pre-configured dashboards show:
- Service health and uptime
- Request rates and latencies
- Error rates
- Database connections

## Environment Variables

### User Service

```env
DATABASE_URL=postgresql://user:password@postgres:5432/userdb
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ANALYTICS_SERVICE_URL=http://analytics-service:8001
```

### Analytics Service

```env
DATABASE_URL=postgresql://user:password@postgres:5432/analyticsdb
USER_SERVICE_URL=http://user-service:8000
```

### Frontend

```env
REACT_APP_USER_SERVICE_URL=http://localhost:8000
REACT_APP_ANALYTICS_SERVICE_URL=http://localhost:8001
```

## Security Considerations

1. **JWT Authentication**: Secure token-based authentication
2. **Password Hashing**: Bcrypt hashing for user passwords
3. **Input Validation**: Pydantic models for request validation
4. **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
5. **CORS**: Configured CORS middleware for API security
6. **Environment Variables**: Sensitive data stored in environment variables
7. **Secrets Management**: Kubernetes secrets for production credentials

## Project Structure

```
Microservices Analytics Platform/
├── user-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── routers/
│   │       └── users.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── analytics-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── routers/
│   │       └── analytics.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── Dockerfile
├── kubernetes/
│   ├── user-service/
│   ├── analytics-service/
│   ├── frontend/
│   ├── databases/
│   ├── kustomization.yaml
│   └── namespace.yaml
├── monitoring/
│   ├── prometheus/
│   └── grafana/
├── docker-compose.yml
└── README.md
```

## Troubleshooting

### Services won't start

1. Check if ports are already in use:
   ```bash
   # Windows
   netstat -ano | findstr "8000"
   netstat -ano | findstr "8001"
   netstat -ano | findstr "3000"

   # Linux/Mac
   lsof -i :8000
   lsof -i :8001
   lsof -i :3000
   ```

2. Verify Docker is running:
   ```bash
   docker ps
   ```

### Database connection errors

1. Wait for databases to be ready (health checks)
2. Verify database credentials in environment variables
3. Check database logs:
   ```bash
   docker-compose logs user-db
   docker-compose logs analytics-db
   ```

### Frontend can't connect to backend

1. Verify backend services are running
2. Check CORS configuration in backend services
3. Verify environment variables in frontend

## Future Enhancements

- [ ] Implement rate limiting
- [ ] Add Redis caching layer
- [ ] Implement message queue (RabbitMQ/Kafka)
- [ ] Add API Gateway (Kong/Traefik)
- [ ] Implement Circuit Breaker pattern
- [ ] Add distributed tracing (Jaeger)
- [ ] Implement log aggregation (ELK Stack)
- [ ] Add automated backup system
- [ ] Implement A/B testing framework
- [ ] Add real-time WebSocket updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue in the repository.
