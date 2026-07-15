import sqlite3
from datetime import datetime, timedelta

DB_NAME = "tenants.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = lambda cursor, row: dict([d[0], row[i]] for i, d in enumerate(cursor.description))
    return conn

def months_between(date1, date2):
    d1 = datetime.strptime(date1, '%Y-%m-%d')
    d2 = datetime.strptime(date2, '%Y-%m-%d')
    months = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    if d2.day > d1.day:
        months += 1
    return max(months, 0)

def calc_balance(tenant):
    today = datetime.now().strftime('%Y-%m-%d')
    months_owed = months_between(tenant['created_at'][:10], today)
    total_owed = (tenant['starting_balance'] or 0) + (months_owed * tenant['amount_to_pay'])
    total_paid = 0
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COALESCE(SUM(amount_paid), 0) as total FROM payments WHERE tenant_id = ?', (tenant['id'],))
    row = cursor.fetchone()
    conn.close()
    total_paid = row['total']
    return max(total_owed - total_paid, 0)

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
