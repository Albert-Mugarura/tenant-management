import sqlite3
from datetime import datetime, timedelta

DB_NAME = "tenants.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = lambda cursor, row: dict([d[0], row[i]] for i, d in enumerate(cursor.description))
    return conn

def calc_balance(tenant):
    prev_balance = tenant.get('starting_balance') or 0

    current_month = datetime.now().strftime('%B')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COALESCE(SUM(amount_paid), 0) as total FROM payments WHERE tenant_id = ? AND month = ?', (tenant['id'], current_month))
    row = cursor.fetchone()
    conn.close()
    current_paid = row['total'] or 0
    current_owed = max(tenant['amount_to_pay'] - current_paid, 0)

    return prev_balance + current_owed

def remove_paid_month(tenant_id, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT starting_balance, starting_balance_details FROM tenants WHERE id = ?', (tenant_id,))
    tenant = cursor.fetchone()
    if not tenant or not tenant.get('starting_balance_details'):
        conn.close()
        return

    details = tenant['starting_balance_details']
    parts = []
    remaining_parts = []
    for item in details.split('|'):
        segs = item.split(':')
        if len(segs) == 2:
            m, a = segs[0], float(segs[1])
            parts.append((m, a))
            if m != month:
                remaining_parts.append(item)

    new_details = '|'.join(remaining_parts)
    new_balance = sum(float(item.split(':')[1]) for item in remaining_parts if len(item.split(':')) == 2)

    cursor.execute('UPDATE tenants SET starting_balance = ?, starting_balance_details = ? WHERE id = ?', (new_balance, new_details, tenant_id))
    conn.commit()
    conn.close()

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            amount_to_pay REAL NOT NULL,
            date_to_pay TEXT NOT NULL,
            balance REAL DEFAULT 0,
            month TEXT NOT NULL,
            reminder_days INTEGER DEFAULT 3,
            preferred_channel TEXT DEFAULT 'both',
            starting_balance REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    try:
        cursor.execute('ALTER TABLE tenants ADD COLUMN starting_balance REAL DEFAULT 0')
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE tenants ADD COLUMN starting_balance_month TEXT DEFAULT ''")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE tenants ADD COLUMN starting_balance_details TEXT DEFAULT ''")
    except Exception:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            amount_paid REAL NOT NULL,
            payment_date TEXT NOT NULL,
            month TEXT NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )
    ''')

    conn.commit()
    conn.close()

def add_tenant(name, phone, amount_to_pay, date_to_pay, month, reminder_days=3, preferred_channel='both', starting_balance=0, starting_balance_month='', starting_balance_details=''):
    balance = amount_to_pay + starting_balance
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tenants (name, phone, amount_to_pay, date_to_pay, balance, month, reminder_days, preferred_channel, starting_balance, starting_balance_month, starting_balance_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, amount_to_pay, date_to_pay, balance, month, reminder_days, preferred_channel, starting_balance, starting_balance_month, starting_balance_details))
    conn.commit()
    tenant_id = cursor.lastrowid
    conn.close()
    return tenant_id

def get_all_tenants():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tenants ORDER BY date_to_pay')
    tenants = cursor.fetchall()
    conn.close()
    return tenants

def get_tenant_by_id(tenant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tenants WHERE id = ?', (tenant_id,))
    tenant = cursor.fetchone()
    conn.close()
    return tenant

def update_tenant(tenant_id, name, phone, amount_to_pay, date_to_pay, month, reminder_days=3, preferred_channel='both', starting_balance=0, starting_balance_month='', starting_balance_details=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tenants 
        SET name = ?, phone = ?, amount_to_pay = ?, date_to_pay = ?, month = ?, reminder_days = ?, preferred_channel = ?, starting_balance = ?, starting_balance_month = ?, starting_balance_details = ?
        WHERE id = ?
    ''', (name, phone, amount_to_pay, date_to_pay, month, reminder_days, preferred_channel, starting_balance, starting_balance_month, starting_balance_details, tenant_id))
    conn.commit()
    conn.close()

def delete_tenant(tenant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM payments WHERE tenant_id = ?', (tenant_id,))
    cursor.execute('DELETE FROM tenants WHERE id = ?', (tenant_id,))
    conn.commit()
    conn.close()

def record_payment(tenant_id, amount_paid, payment_date, month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO payments (tenant_id, amount_paid, payment_date, month)
        VALUES (?, ?, ?, ?)
    ''', (tenant_id, amount_paid, payment_date, month))

    conn.commit()
    conn.close()

def get_tenant_payments(tenant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM payments 
        WHERE tenant_id = ? 
        ORDER BY payment_date DESC
    ''', (tenant_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments

def get_tenants_due_soon(days_before=3):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()
    upcoming_date = today + timedelta(days=days_before)

    cursor.execute('''
        SELECT * FROM tenants 
        WHERE date(date_to_pay) <= date(?) 
        AND date(date_to_pay) >= date(?)
    ''', (upcoming_date.isoformat(), today.isoformat()))

    tenants = cursor.fetchall()
    conn.close()
    return tenants

def get_overdue_tenants():
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()

    cursor.execute('''
        SELECT * FROM tenants 
        WHERE date(date_to_pay) < date(?)
    ''', (today.isoformat(),))

    tenants = cursor.fetchall()
    conn.close()
    return tenants

def search_tenants(search_term):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tenants 
        WHERE name LIKE ?
        ORDER BY date_to_pay
    ''', (f'%{search_term}%',))
    tenants = cursor.fetchall()
    conn.close()
    return tenants

def get_monthly_summary(month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            COUNT(*) as total_tenants,
            SUM(amount_to_pay) as total_expected,
            SUM(amount_to_pay - balance) as total_collected,
            SUM(balance) as total_outstanding
        FROM tenants 
        WHERE month = ?
    ''', (month,))

    summary = cursor.fetchone()
    conn.close()
    return summary
