import sqlite3
from datetime import datetime, timedelta

DB_NAME = "tenants.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            amount_to_pay REAL NOT NULL,
            date_to_pay TEXT NOT NULL,
            balance REAL DEFAULT 0,
            month TEXT NOT NULL,
            reminder_days INTEGER DEFAULT 3,
            preferred_channel TEXT DEFAULT 'both',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

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

def add_tenant(name, phone, amount_to_pay, date_to_pay, month, reminder_days=3, preferred_channel='both'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tenants (name, phone, amount_to_pay, date_to_pay, balance, month, reminder_days, preferred_channel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, amount_to_pay, date_to_pay, amount_to_pay, month, reminder_days, preferred_channel))
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

def update_tenant(tenant_id, name, phone, amount_to_pay, date_to_pay, month, reminder_days=3, preferred_channel='both'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tenants 
        SET name = ?, phone = ?, amount_to_pay = ?, date_to_pay = ?, month = ?, reminder_days = ?, preferred_channel = ?
        WHERE id = ?
    ''', (name, phone, amount_to_pay, date_to_pay, month, reminder_days, preferred_channel, tenant_id))
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

    cursor.execute('''
        UPDATE tenants 
        SET balance = balance - ?
        WHERE id = ?
    ''', (amount_paid, tenant_id))

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
        AND balance > 0
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
        AND balance > 0
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
