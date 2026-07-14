# Tenant Management System for Alinaitwe Joseph

## Features

- **Add/View/Update/Delete Tenants** - Complete tenant management
- **Payment Tracking** - Record payments and track balances
- **Automatic Reminders** - Get alerts for due and overdue payments
- **SMS Reminders** - Send payment reminders via SMS (Africa's Talking)
- **WhatsApp Reminders** - Send payment reminders via WhatsApp (Africa's Talking)
- **Monthly Summary** - View collection statistics
- **Search Functionality** - Find tenants by name

## How to Run

```bash
cd C:\Users\THINKPAD\tenant_management
python tenant_manager.py
```

## System Requirements

- Python 3.x
- Install Africa's Talking SDK: `pip install africastalking`

## Main Menu Options

1. **Add New Tenant** - Register a new tenant with name, phone, rent amount, and due date
2. **View All Tenants** - See all tenants with their payment status
3. **Search Tenant** - Find a tenant by name
4. **Update Tenant** - Modify tenant information
5. **Delete Tenant** - Remove a tenant from the system
6. **Record Payment** - Log a payment from a tenant
7. **View Tenant Payments** - See payment history for a specific tenant
8. **Check Reminders** - View all payment reminders (overdue, due today, upcoming)
9. **Send Reminder (SMS/WhatsApp)** - Send reminder to a specific tenant
10. **Send Bulk Reminders** - Send reminders to all tenants with due payments
11. **Monthly Summary** - See collection statistics for a given month
12. **Setup Messaging** - Configure Africa's Talking credentials
13. **Exit** - Close the application

## Setup SMS and WhatsApp (Africa's Talking)

### Step 1: Create Account
1. Go to https://account.africastalking.com
2. Sign up for a free account
3. Verify your email and phone number

### Step 2: Get API Key
1. Log in to the dashboard
2. Go to **Settings** > **API Key**
3. Copy your API key

### Step 3: Configure in the System
1. Run the application
2. Select option **12. Setup Messaging**
3. Enter your credentials:
   - Username: Use `sandbox` for testing (or your app username for production)
   - API Key: Paste your API key from Step 2
   - WhatsApp Number: Your WhatsApp-enabled phone number (e.g., +2567XXXXXXXX)

### Step 4: Test with Sandbox
- In sandbox mode, use test phone numbers provided by Africa's Talking
- Sandbox numbers: +254711XXXYYY (use your sandbox test numbers)
- No real airtime is charged in sandbox mode

### Step 5: Go Production
1. Add airtime to your Africa's Talking account
2. Change username from `sandbox` to your production app username
3. Register a Sender ID (brand name) with MTN/Airtel (~UGX 300,000 one-time)

## SMS Pricing (Uganda)

| Provider | Per SMS | Notes |
|----------|---------|-------|
| Africa's Talking | ~UGX 25-32 | USD-tied, developer-friendly |
| Local Providers | UGX 25-35 | Wesendall, EgoSMS, MegaSMS |
| Twilio | ~UGX 900-1,100 | Expensive for Uganda |

## Reminder Types

The system sends reminders for:
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

- `tenant_manager.py` - Main application
- `database.py` - Database operations
- `reminders.py` - Reminder logic
- `messaging.py` - SMS/WhatsApp integration
- `messaging_config.json` - Saved credentials (auto-created)

## For Landlord Alinaitwe Joseph

This system is designed specifically for you as the sole user. All tenant data, payment records, and reminders are stored locally on your computer.
