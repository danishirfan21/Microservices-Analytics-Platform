# Quick Setup Guide

## Local Development with Docker Compose (Recommended)

### Step 1: Prerequisites
Ensure you have installed:
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose (included with Docker Desktop)

### Step 2: Start the Platform

Open a terminal in the project directory and run:

```bash
docker-compose up --build
```

Wait for all services to start (approximately 2-3 minutes on first run).

### Step 3: Access the Dashboard

1. Open your browser and go to: http://localhost:3000
2. Click "Register" to create a new account
3. Fill in the registration form:
   - Email: your@email.com
   - Username: testuser
   - Password: password123
   - Full Name: Test User
4. You'll be automatically logged in

### Step 4: Explore the Dashboard

The dashboard displays:
- **Total Users**: Count of all registered users
- **Active Users (24h)**: Users active in the last 24 hours
- **Total Events**: All tracked events
- **Event Distribution**: Pie chart showing event type breakdown
- **Event Counts**: Bar chart of event counts by type

### Step 5: Generate Test Data

To see more interesting analytics:

1. Register multiple user accounts
2. Login/logout several times
3. Update user profiles
4. Refresh the dashboard to see updated analytics

### Step 6: Explore the APIs

Visit the interactive API documentation:
- User Service: http://localhost:8000/docs
- Analytics Service: http://localhost:8001/docs

### Step 7: View Monitoring

Access the monitoring tools:
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### Step 8: Stop the Platform

When finished, press `Ctrl+C` in the terminal, then run:

```bash
docker-compose down
```

To also remove all data:

```bash
docker-compose down -v
```

## Manual Development Setup (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Step 1: Setup Databases

Create two PostgreSQL databases:

```sql
CREATE DATABASE userdb;
CREATE DATABASE analyticsdb;
```

### Step 2: Setup User Service

```bash
cd user-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
uvicorn app.main:app --reload --port 8000
```

### Step 3: Setup Analytics Service

Open a new terminal:

```bash
cd analytics-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
uvicorn app.main:app --reload --port 8001
```

### Step 4: Setup Frontend

Open a new terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

The frontend will open at http://localhost:3000

## Kubernetes Deployment

### Prerequisites
- kubectl installed
- Access to a Kubernetes cluster (minikube, kind, or cloud provider)

### Step 1: Create Namespace

```bash
kubectl apply -f kubernetes/namespace.yaml
```

### Step 2: Deploy All Services

```bash
kubectl apply -k kubernetes/
```

### Step 3: Verify Deployment

```bash
kubectl get all -n microservices-analytics
```

### Step 4: Access Services

```bash
# Port forward to access services locally
kubectl port-forward -n microservices-analytics svc/frontend 3000:80
kubectl port-forward -n microservices-analytics svc/user-service 8000:8000
kubectl port-forward -n microservices-analytics svc/analytics-service 8001:8001
```

## Common Issues and Solutions

### Issue: Port already in use

**Solution**: Stop the service using that port or change the port in docker-compose.yml

### Issue: Database connection failed

**Solution**: Wait 30 seconds for databases to initialize, or check database credentials

### Issue: Frontend can't connect to backend

**Solution**: Verify backend services are running and CORS is properly configured

### Issue: Docker build fails

**Solution**:
- Ensure Docker has enough memory (at least 4GB)
- Clear Docker cache: `docker system prune -a`
- Rebuild: `docker-compose build --no-cache`

## Running Tests

### All Tests
```bash
make test
```

### User Service Tests Only
```bash
cd user-service
pytest -v
```

### Analytics Service Tests Only
```bash
cd analytics-service
pytest -v
```

## Next Steps

1. Explore the API documentation at `/docs` endpoints
2. Set up Grafana dashboards for monitoring
3. Customize the frontend styling
4. Add more analytics features
5. Deploy to a cloud provider (AWS, GCP, Azure)

## Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs [service-name]`
2. Review the troubleshooting section in README.md
3. Open an issue in the repository
