# Online Production Deployment Guide

## 1. Overview
This guide provides complete instructions to deploy the **Student Performance Predictor** to public hosting platforms.

Supported hosting targets:
- **Option A**: Render.com (Recommended for beginners with free tier web service and managed MySQL)
- **Option B**: PythonAnywhere (Simple WSGI configuration with native MySQL)
- **Option C**: AWS EC2 / DigitalOcean Ubuntu Droplet (Full production control with Nginx + Gunicorn)

---

## 2. Option A: Render.com Deployment (Recommended)

### Step 1: Push Repository to GitHub
1. Initialize git in the workspace:
   ```bash
   git init
   git add .
   git commit -m "Complete Student Performance Predictor application"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Student-Performance-Predictor.git
   git push -u origin main
   ```

### Step 2: Provision a Managed MySQL Database
1. In your Render dashboard, click **New +** -> **MySQL** (or use PlanetScale / Aiven for free cloud MySQL).
2. Copy the external connection URL or individual credentials:
   - Host, Port (3306), Database Name, Username, and Password.

### Step 3: Create a Web Service on Render
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the build & start commands:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python model_training/train_model.py`
   - **Start Command**: `gunicorn deployment.wsgi:app`
4. Add the Environment Variables in the Render Settings tab:
   - `SECRET_KEY`: `[Generate a secure 32+ character random string]`
   - `DB_ENGINE`: `mysql`
   - `DB_HOST`: `[Your Cloud MySQL Host]`
   - `DB_PORT`: `3306`
   - `DB_USER`: `[Your Cloud MySQL Username]`
   - `DB_PASSWORD`: `[Your Cloud MySQL Password]`
   - `DB_NAME`: `[Your Cloud MySQL Database Name]`
   - `SQLITE_FALLBACK`: `False` (for strict cloud MySQL operation)
   - `ADMIN_USERNAME`: `admin`
   - `ADMIN_PASSWORD`: `[A strong administrator password]`

---

## 3. Option B: PythonAnywhere Deployment

1. Register an account on [PythonAnywhere.com](https://www.pythonanywhere.com/).
2. Open a Bash console and clone your repository or upload the project ZIP.
3. Set up a virtual environment and install dependencies:
   ```bash
   mkvirtualenv --python=python3.10 student-env
   pip install -r requirements.txt
   python model_training/train_model.py
   ```
4. Enable the **MySQL** tab on PythonAnywhere and create a database named `student_predictor_db`.
5. In the **Web** tab:
   - Set Python version to 3.10+.
   - Set Virtualenv path to `~/.virtualenvs/student-env`.
   - Edit the **WSGI configuration file**:
     ```python
     import sys
     import os

     path = '/home/yourusername/Student-Performance-Predictor'
     if path not in sys.path:
         sys.path.append(path)

     from dotenv import load_dotenv
     load_dotenv(os.path.join(path, '.env'))

     from app import app as application
     ```
6. Click **Reload yourusername.pythonanywhere.com**.

---

## 4. Production Security & Best Practices
1. **Never commit `.env` files**: All sensitive passwords and API keys must remain in server environment variables.
2. **HTTPS**: Cloud providers like Render and PythonAnywhere provide automated SSL/TLS certificates by default.
3. **Session Cookies**: In production, ensure `SESSION_COOKIE_SECURE = True` and `SESSION_COOKIE_HTTPONLY = True`.
4. **Database Backups**: Schedule regular automated `mysqldump` snapshots of the `predictions` and `users` tables.
