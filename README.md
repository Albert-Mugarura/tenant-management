# Tenant Management System for Alinaitwe Joseph

## Features

- **Add/View/Update/Delete Tenants** - Complete tenant management
- **Payment Tracking** - Record payments and track balances
- **Automatic Reminders** - Get alerts for due and overdue payments
- **Monthly Summary** - View collection statistics
- **Search Functionality** - Find tenants by name
- **Manual Reminders** - Copy payment messages and send via WhatsApp or SMS manually

## How to Run

```bash
cd C:\Users\THINKPAD\tenant_management
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

## Deploy to Phone (PythonAnywhere - Free)

Your landlord can access the system from any phone browser, anywhere.

### Step 1: Create Account
1. Go to **https://www.pythonanywhere.com**
2. Sign up for a **free account** (no credit card needed)

### Step 2: Upload Files
1. Log in and go to **Dashboard** > **Files**
2. Click **Upload a file** and upload every file from this project:
   - `app.py`
   - `database.py`
   - `reminders.py`
   - `tenant_manager.py`
   - `passenger_wsgi.py`
   - `requirements.txt`
   - All files in `templates/` folder
3. Or use **Git**: In the **Bash console** at the bottom:
   ```
   git clone https://github.com/Albert-Mugarura/tenant-management.git
   ```

### Step 3: Install Dependencies
Open the **Bash console** and run:
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Web App
1. Go to **Web** tab > **Add a new web app**
2. Choose **Manual configuration** > **Python 3.13**
3. Under **WSGI configuration file**, click the file path and replace contents with:
   ```python
   import sys
   import os
   project_home = os.path.dirname(os.path.abspath(__file__))
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   from app import app as application
   ```
4. Under **Working directory**, set to your project folder name (e.g., `tenant-management`)
5. Under **Source code**, set the same project folder
6. Click **Reload**

### Step 5: Access on Phone
- Your app URL: **https://yourusername.pythonanywhere.com**
- Open it on any phone browser
- **Add to Home Screen** for app-like experience:
  - **iPhone Safari**: Tap Share > Add to Home Screen
  - **Android Chrome**: Tap menu > Add to Home Screen

### Important Notes
- Database (`tenants.db`) is created automatically on first run
- Data persists between restarts on PythonAnywhere
- Free tier: App sleeps after 30 min of no visits (wakes up in ~5 seconds when accessed)

## Reminder Types

The system shows reminders for:
- **OVERDUE** - Payments past due date (URGENT)
- **DUE TODAY** - Payment due on current day
- **DUE TOMORROW** - Payment due next day
- **APPROACHING** - Payment due within 3 days

## Message Format

```
Dear [Tenant Name], your rent of [Amount] UGX is due on [Date].
Balance: [Balance] UGX. - Landlord Joseph
```

## Database

Data is stored in `tenants.db` (SQLite). This file is created automatically on first run.

## Files

- `app.py` - Flask web application
- `passenger_wsgi.py` - PythonAnywhere WSGI entry point
- `tenant_manager.py` - CLI application
- `database.py` - Database operations
- `reminders.py` - Reminder logic
- `requirements.txt` - Python dependencies
- `templates/` - HTML templates for the web interface

## For Landlord Alinaitwe Joseph

This system is designed specifically for you as the sole user. All tenant data, payment records, and reminders are stored locally on your computer or PythonAnywhere server.
