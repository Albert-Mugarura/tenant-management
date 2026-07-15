from datetime import datetime, timedelta
from database import get_tenants_due_soon, get_overdue_tenants
import os

REMINDER_LOG_FILE = "reminders.log"

def log_reminder(message):
    try:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), REMINDER_LOG_FILE)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception:
        pass

def generate_payment_reminder(tenant):
    today = datetime.now().date()
    due_date = datetime.strptime(tenant['date_to_pay'], '%Y-%m-%d').date()
    days_until_due = (due_date - today).days

    if days_until_due < 0:
        urgency = "OVERDUE"
        message = f"URGENT: {tenant['name']} has an OVERDUE payment of {tenant['amount_to_pay']} UGX (was due {abs(days_until_due)} days ago). Balance: {tenant['balance']} UGX"
    elif days_until_due == 0:
        urgency = "DUE TODAY"
        message = f"REMINDER: {tenant['name']} payment of {tenant['amount_to_pay']} UGX is DUE TODAY. Balance: {tenant['balance']} UGX"
    elif days_until_due == 1:
        urgency = "DUE TOMORROW"
        message = f"REMINDER: {tenant['name']} payment of {tenant['amount_to_pay']} UGX is due TOMORROW. Balance: {tenant['balance']} UGX"
    elif days_until_due <= 3:
        urgency = "APPROACHING"
        message = f"NOTICE: {tenant['name']} payment of {tenant['amount_to_pay']} UGX is due in {days_until_due} days. Balance: {tenant['balance']} UGX"
    else:
        urgency = "UPCOMING"
        message = f"INFO: {tenant['name']} payment of {tenant['amount_to_pay']} UGX is due in {days_until_due} days. Balance: {tenant['balance']} UGX"

    return urgency, message

def check_and_generate_reminders():
    reminders = []

    overdue_tenants = get_overdue_tenants()
    for tenant in overdue_tenants:
        urgency, message = generate_payment_reminder(tenant)
        reminders.append({
            'tenant_id': tenant['id'],
            'tenant_name': tenant['name'],
            'urgency': urgency,
            'message': message,
            'phone': tenant['phone'],
            'reminder_days': tenant['reminder_days'] if 'reminder_days' in tenant.keys() else 3
        })
        log_reminder(message)

    due_soon_tenants = get_tenants_due_soon(days_before=30)
    for tenant in due_soon_tenants:
        if not any(r['tenant_id'] == tenant['id'] for r in reminders):
            days_until = (datetime.strptime(tenant['date_to_pay'], '%Y-%m-%d').date() - datetime.now().date()).days
            reminder_days = tenant['reminder_days'] if 'reminder_days' in tenant.keys() else 3
            if days_until <= reminder_days:
                urgency, message = generate_payment_reminder(tenant)
                reminders.append({
                    'tenant_id': tenant['id'],
                    'tenant_name': tenant['name'],
                    'urgency': urgency,
                    'message': message,
                    'phone': tenant['phone'],
                    'reminder_days': reminder_days
                })
                log_reminder(message)

    return reminders

def format_sms_message(tenant_name, amount, due_date, balance, days_until):
    if days_until <= 0:
        return f"Dear {tenant_name}, your rent payment of {amount} UGX is overdue. Please pay immediately. Outstanding balance: {balance} UGX. - Landlord Alinaitwe Joseph"
    elif days_until == 1:
        return f"Dear {tenant_name}, reminder: your rent payment of {amount} UGX is due TOMORROW. Balance: {balance} UGX. - Landlord Alinaitwe Joseph"
    elif days_until <= 3:
        return f"Dear {tenant_name}, reminder: your rent payment of {amount} UGX is due in {days_until} days ({due_date}). Balance: {balance} UGX. - Landlord Alinaitwe Joseph"
    else:
        return f"Dear {tenant_name}, friendly reminder: your rent payment of {amount} UGX is due on {due_date}. Balance: {balance} UGX. - Landlord Alinaitwe Joseph"

def display_reminders(reminders):
    if not reminders:
        print("\n[OK] No reminders needed at this time.")
        return

    print("\n" + "="*70)
    print("PAYMENT REMINDERS")
    print("="*70)

    urgency_order = {"OVERDUE": 0, "DUE TODAY": 1, "DUE TOMORROW": 2, "APPROACHING": 3, "UPCOMING": 4}
    sorted_reminders = sorted(reminders, key=lambda x: urgency_order.get(x['urgency'], 5))

    for reminder in sorted_reminders:
        print(f"\n[{reminder['urgency']}]")
        print(f"  Tenant: {reminder['tenant_name']}")
        print(f"  Phone: {reminder['phone']}")
        print(f"  Message: {reminder['message']}")
        print(f"  SMS Preview: {format_sms_message(reminder['tenant_name'], 0, '', 0, 0)}")

    print("\n" + "="*70)
    print(f"Total reminders: {len(reminders)}")
    print("="*70)
