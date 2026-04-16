# Free Deployment Guide (Complete & Simple)

This guide explains how to deploy this microservices analytics platform **100% FREE**, specifically optimized for simplicity and ease of use (especially from regions like Pakistan).

## 1. The Easiest Free Path: "The Monolith Shortcut"

Deploying multiple microservices on free tiers can be painful because of "spin-down" (sleep mode) and resource limits. We have simplified this by providing a `monolith.py` entry point that runs both services as one.

### Recommended Stack:
- **Database**: [Neon](https://neon.tech) (Free PostgreSQL, no credit card required)
- **Backend**: [Render](https://render.com) (Free Web Services)
- **Frontend**: [Vercel](https://vercel.com) (Free Static Hosting)

---

## 2. Step-by-Step Instructions

### Step 1: Database (Neon.tech)
1. Sign up at [Neon.tech](https://neon.tech).
2. Create a new project named `analytics-platform`.
3. You will get a connection string like: `postgresql://user:pass@host/neondb?sslmode=require`.
4. (Optional but better) Create two databases in the Neon dashboard: `user_db` and `analytics_db`.
5. Copy your connection string(s).

### Step 2: Backend (Render.com)
1. Sign up at [Render.com](https://render.com) (GitHub login recommended).
2. Click **New +** -> **Web Service**.
3. Connect your repository.
4. Use these settings:
   - **Name**: `analytics-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn monolith:app --host 0.0.0.0 --port 8000`
5. Add **Environment Variables**:
   - `USER_DATABASE_URL`: (Your Neon connection string)
   - `ANALYTICS_DATABASE_URL`: (Your Neon connection string)
   - `SECRET_KEY`: (A random string, e.g., `mysecret123`)
   - `ANALYTICS_SERVICE_URL`: `https://analytics-backend.onrender.com/analytics-service`
   - `ALLOWED_ORIGINS`: `https://your-frontend.vercel.app` (Add this later)
6. Click **Deploy**.

### Step 3: Frontend (Vercel)
1. Sign up at [Vercel.com](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Import your repository.
4. Set **Root Directory** to `frontend`.
5. Add **Environment Variables**:
   - `REACT_APP_USER_SERVICE_URL`: `https://analytics-backend.onrender.com/user-service`
   - `REACT_APP_ANALYTICS_SERVICE_URL`: `https://analytics-backend.onrender.com/analytics-service`
6. Click **Deploy**.

---

## 3. Limitations of Free Tier

- **Cold Starts (Sleep Mode)**: On Render, if nobody visits your site for 15 minutes, the backend "goes to sleep". The first person to visit after that will wait 30-50 seconds for it to start.
- **Resource Limits**: Render gives you 750 free hours per month (enough for 1 service to run 24/7). If you deploy 2 services, you will run out of hours halfway through the month. **Use the monolith approach to stay free!**
- **Neon Storage**: Free tier includes 0.5 GB, which is plenty for thousands of users/events.

---

## 4. Pakistan-Specific Tips

- **No Credit Card?**: Neon, Render, and Vercel all have generous free tiers that **do not require a credit card** to start.
- **Speed**: If Render is slow, try [Railway.app](https://railway.app) (they offer a trial but it's not permanently free like Render).
- **GitHub**: Always keep your code on GitHub; it makes connecting these services much easier.

---

## 5. FAQs

### Can I still deploy as microservices?
Yes. Just create two separate Web Services on Render:
- One for `user_service` (Start: `uvicorn user_service.app.main:app --port 8000`)
- One for `analytics_service` (Start: `uvicorn analytics_service.app.main:app --port 8001`)
*Note: This will use up your free hours 2x faster.*

### How do I connect the services?
In monolith mode, the services communicate internally or via the mounted paths. The frontend simply needs to know the base URL + the prefix (`/user-service` or `/analytics-service`).

### What about SSL?
All suggested platforms (Neon, Render, Vercel) provide SSL (HTTPS) automatically for free.
