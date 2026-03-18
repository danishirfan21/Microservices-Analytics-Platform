# Free Deployment Guide

This guide provides instructions for deploying the Microservices Analytics Platform for free using modern cloud platforms.

## Overview of the Free Stack

To host this platform without costs, we will use the following services:
- **Databases**: [Neon](https://neon.tech) (Serverless PostgreSQL)
- **Backend Services**: [Render](https://render.com) (Free Web Services)
- **Frontend**: [Vercel](https://vercel.com) or [Render](https://render.com) (Static Site Hosting)

---

## 1. Database Setup (Neon)

You need two separate databases: one for the User Service and one for the Analytics Service.

1.  Sign up for a free account at [neon.tech](https://neon.tech).
2.  Create a new project.
3.  In your project dashboard, create two databases:
    -   `user_db`
    -   `analytics_db`
4.  Copy the connection strings (External Connection) for both. They should look like:
    `postgresql://[user]:[password]@[host]/[dbname]?sslmode=require`

---

## 2. Backend Services Setup (Render)

### User Service

1.  Sign up at [render.com](https://render.com).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub/GitLab repository.
4.  Select the project root and set the following:
    -   **Name**: `user-service`
    -   **Root Directory**: `user-service`
    -   **Environment**: `Python 3`
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5.  In the **Environment** tab, add the variables (see [Environment Variables](#environment-variables) section).
6.  Click **Create Web Service**.

### Analytics Service

1.  Click **New +** and select **Web Service**.
2.  Connect the same repository.
3.  Set the following:
    -   **Name**: `analytics-service`
    -   **Root Directory**: `analytics-service`
    -   **Environment**: `Python 3`
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8001`
4.  In the **Environment** tab, add the variables.
5.  Click **Create Web Service**.

---

## 3. Frontend Setup (Vercel or Render)

### Option A: Vercel (Recommended)

1.  Sign up at [vercel.com](https://vercel.com).
2.  Click **Add New...** -> **Project**.
3.  Import your repository.
4.  Set the following:
    -   **Root Directory**: `frontend`
    -   **Framework Preset**: `Create React App`
5.  In **Environment Variables**, add:
    -   `REACT_APP_USER_SERVICE_URL`: URL of your deployed `user-service`
    -   `REACT_APP_ANALYTICS_SERVICE_URL`: URL of your deployed `analytics-service`
6.  Click **Deploy**.

### Option B: Render

1.  Click **New +** and select **Static Site**.
2.  Set **Root Directory** to `frontend`.
3.  **Build Command**: `npm run build`
4.  **Publish Directory**: `build`
5.  Add environment variables as above.
6.  Click **Create Static Site**.

---

## 4. Environment Variables

### User Service (`user-service`)
- `DATABASE_URL`: Your Neon connection string for `user_db`
- `SECRET_KEY`: A random long string for JWT
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `60`
- `ANALYTICS_SERVICE_URL`: The URL of your deployed `analytics-service`
- `ALLOWED_ORIGINS`: The URL of your deployed frontend (e.g., `https://your-app.vercel.app`)

### Analytics Service (`analytics-service`)
- `DATABASE_URL`: Your Neon connection string for `analytics_db`
- `USER_SERVICE_URL`: The URL of your deployed `user-service`
- `ALLOWED_ORIGINS`: The URL of your deployed frontend

---

## 5. Verification

1.  Wait for all services to deploy successfully.
2.  Open your frontend URL.
3.  Try to **Register** a new user.
4.  **Login** and check if the dashboard displays data.
5.  If something fails, check the logs in the Render/Vercel dashboard.

---

## Important Notes on Free Tiers

- **Render Free Tier**: Services will "spin down" after 15 minutes of inactivity. The first request after a spin-down may take 30+ seconds to respond.
- **Neon Free Tier**: Includes 0.5 GiB of storage and shared compute, which is plenty for this project.
- **SSL/HTTPS**: All these providers provide automatic SSL. Ensure your URLs in environment variables start with `https://`.
