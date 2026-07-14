import os
import json

CONFIG_FILE = "messaging_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def setup_credentials():
    print("\n--- MESSAGING SETUP (Africa's Talking) ---")
    print("\n1. Go to https://account.africastalking.com and create an account")
    print("2. Get your API key from the dashboard")
    print("3. For sandbox testing, username is always 'sandbox'")
    print("4. For production, use your app username\n")

    config = load_config()

    username = input(f"Username [{config.get('username', 'sandbox')}]: ").strip()
    if username:
        config['username'] = username
    elif 'username' not in config:
        config['username'] = 'sandbox'

    api_key = input(f"API Key [{config.get('api_key', '')}]: ").strip()
    if api_key:
        config['api_key'] = api_key
    elif 'api_key' not in config:
        print("[ERROR] API Key is required!")
        return None

    whatsapp_number = input(f"WhatsApp Number (e.g., +2567XXXXXXXX) [{config.get('whatsapp_number', '')}]: ").strip()
    if whatsapp_number:
        config['whatsapp_number'] = whatsapp_number

    save_config(config)
    print("\n[OK] Credentials saved!")
    return config

def get_at_services():
    config = load_config()
    if not config or 'api_key' not in config:
        print("[ERROR] Messaging not configured. Run setup first.")
        return None, None, None

    try:
        import africastalking
        africastalking.initialize(config['username'], config['api_key'])
        sms = africastalking.SMS
        whatsapp = africastalking.Whatsapp
        return sms, whatsapp, config
    except ImportError:
        print("[ERROR] africastalking package not installed. Run: pip install africastalking")
        return None, None, None
    except Exception as e:
        print(f"[ERROR] Failed to initialize Africa's Talking: {e}")
        return None, None, None

def send_sms(phone_number, message):
    sms, _, config = get_at_services()
    if not sms:
        return False

    try:
        response = sms.send(message, [phone_number])
        if response['SMSMessageData']['Recipients'][0]['status'] == 'Success':
            print(f"[SMS OK] Message sent to {phone_number}")
            return True
        else:
            print(f"[SMS FAILED] {response['SMSMessageData']['Recipients'][0]['status']}")
            return False
    except Exception as e:
        print(f"[SMS ERROR] {e}")
        return False

def send_whatsapp(phone_number, message):
    _, whatsapp, config = get_at_services()
    if not whatsapp or not config.get('whatsapp_number'):
        print("[ERROR] WhatsApp not configured")
        return False

    try:
        body = {"message": message}
        response = whatsapp.send(body, config['whatsapp_number'], phone_number)
        print(f"[WHATSAPP OK] Message sent to {phone_number}")
        return True
    except Exception as e:
        print(f"[WHATSAPP ERROR] {e}")
        return False

def send_reminder_sms(tenant_name, phone, amount, due_date, balance, days_until):
    message = format_sms_message(tenant_name, amount, due_date, balance, days_until)
    return send_sms(phone, message)

def send_reminder_whatsapp(tenant_name, phone, amount, due_date, balance, days_until):
    message = format_sms_message(tenant_name, amount, due_date, balance, days_until)
    return send_whatsapp(phone, message)

def format_sms_message(tenant_name, amount, due_date, balance, days_until):
    if days_until <= 0:
        return f"Dear {tenant_name}, your rent of {amount:,.0f} UGX is OVERDUE. Please pay immediately. Balance: {balance:,.0f} UGX. - Landlord Joseph"
    elif days_until == 1:
        return f"Dear {tenant_name}, reminder: your rent of {amount:,.0f} UGX is due TOMORROW. Balance: {balance:,.0f} UGX. - Landlord Joseph"
    elif days_until <= 3:
        return f"Dear {tenant_name}, your rent of {amount:,.0f} UGX is due in {days_until} days ({due_date}). Balance: {balance:,.0f} UGX. - Landlord Joseph"
    else:
        return f"Dear {tenant_name}, friendly reminder: your rent of {amount:,.0f} UGX is due on {due_date}. Balance: {balance:,.0f} UGX. - Landlord Joseph"

def send_reminder_to_tenant(tenant, method=None):
    from datetime import datetime
    today = datetime.now().date()
    due_date = datetime.strptime(tenant['date_to_pay'], '%Y-%m-%d').date()
    days_until = (due_date - today).days

    if method is None:
        method = tenant.get('preferred_channel', 'both')

    results = {'sms': False, 'whatsapp': False}

    if method == "both":
        results['whatsapp'] = send_reminder_whatsapp(
            tenant['name'], tenant['phone'],
            tenant['amount_to_pay'], tenant['date_to_pay'],
            tenant['balance'], days_until
        )
        if not results['whatsapp']:
            results['sms'] = send_reminder_sms(
                tenant['name'], tenant['phone'],
                tenant['amount_to_pay'], tenant['date_to_pay'],
                tenant['balance'], days_until
            )
    elif method == "sms":
        results['sms'] = send_reminder_sms(
            tenant['name'], tenant['phone'],
            tenant['amount_to_pay'], tenant['date_to_pay'],
            tenant['balance'], days_until
        )
    elif method == "whatsapp":
        results['whatsapp'] = send_reminder_whatsapp(
            tenant['name'], tenant['phone'],
            tenant['amount_to_pay'], tenant['date_to_pay'],
            tenant['balance'], days_until
        )

    return results

def send_bulk_reminders(tenants, method="both"):
    print(f"\n--- SENDING REMINDERS ({method.upper()}) ---")
    success_count = 0
    fail_count = 0

    for tenant in tenants:
        print(f"\nSending to {tenant['name']} ({tenant['phone']})...")
        results = send_reminder_to_tenant(tenant, method)

        if method == "both":
            if results['sms'] or results['whatsapp']:
                success_count += 1
            else:
                fail_count += 1
        elif method == "sms":
            if results['sms']:
                success_count += 1
            else:
                fail_count += 1
        elif method == "whatsapp":
            if results['whatsapp']:
                success_count += 1
            else:
                fail_count += 1

    print(f"\n--- SUMMARY ---")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {len(tenants)}")
