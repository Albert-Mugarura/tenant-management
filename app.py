from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime
from database import (
    initialize_database, add_tenant, get_all_tenants, get_tenant_by_id,
    update_tenant, delete_tenant, record_payment, get_tenant_payments,
    search_tenants, get_monthly_summary, get_tenants_due_soon, get_overdue_tenants,
    calc_balance
)
from reminders import check_and_generate_reminders

app = Flask(__name__)
app.secret_key = 'tenant_management_secret_key_2026'

USERNAME = 'joezy'
PASSWORD = 'joezy@2026'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

initialize_database()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        flash('Invalid username or password!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    tenants = get_all_tenants()
    for t in tenants:
        t['balance'] = calc_balance(t)
    overdue = [t for t in get_overdue_tenants() if calc_balance(t) > 0]
    for t in overdue:
        t['balance'] = calc_balance(t)
    due_soon = [t for t in get_tenants_due_soon(3) if calc_balance(t) > 0]
    for t in due_soon:
        t['balance'] = calc_balance(t)
    reminders = check_and_generate_reminders()

    total_outstanding = sum(t['balance'] for t in tenants)

    return render_template('index.html',
        tenants=tenants,
        overdue=overdue,
        due_soon=due_soon,
        reminders=reminders,
        total_outstanding=total_outstanding,
        tenant_count=len(tenants)
    )

@app.route('/tenants')
@login_required
def tenants_list():
    tenants = get_all_tenants()
    for t in tenants:
        t['balance'] = calc_balance(t)
    return render_template('tenants.html', tenants=tenants)

@app.route('/tenants/add', methods=['GET', 'POST'])
@login_required
def add_tenant_view():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form.get('phone', '')
        amount = float(request.form['amount'])
        date_to_pay = request.form['date_to_pay']
        month = request.form['month']
        reminder_days = int(request.form.get('reminder_days', 3))
        preferred_channel = request.form.get('preferred_channel', 'both')
        starting_balance = 0
        balance_months = request.form.getlist('balance_month[]')
        balance_amounts = request.form.getlist('balance_amount[]')
        balance_details = []
        month_list = []
        for bm, ba in zip(balance_months, balance_amounts):
            if bm and ba:
                amt = float(ba)
                starting_balance += amt
                balance_details.append(f"{bm}:{amt}")
                month_list.append(bm)
        starting_balance_month = ', '.join(month_list)
        starting_balance_details = '|'.join(balance_details)

        add_tenant(name, phone, amount, date_to_pay, month, reminder_days, preferred_channel, starting_balance, starting_balance_month, starting_balance_details)
        flash(f'Tenant "{name}" added successfully!', 'success')
        return redirect(url_for('tenants_list'))

    return render_template('add_tenant.html')

@app.route('/tenants/<int:tenant_id>')
@login_required
def tenant_detail(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenants_list'))

    tenant['balance'] = calc_balance(tenant)
    payments = get_tenant_payments(tenant_id)
    return render_template('tenant_detail.html', tenant=tenant, payments=payments)

@app.route('/tenants/<int:tenant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tenant(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenants_list'))

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form.get('phone', '')
        amount = float(request.form['amount'])
        date_to_pay = request.form['date_to_pay']
        month = request.form['month']
        reminder_days = int(request.form.get('reminder_days', 3))
        preferred_channel = request.form.get('preferred_channel', 'both')
        starting_balance = 0
        balance_months = request.form.getlist('balance_month[]')
        balance_amounts = request.form.getlist('balance_amount[]')
        balance_details = []
        month_list = []
        for bm, ba in zip(balance_months, balance_amounts):
            if bm and ba:
                amt = float(ba)
                starting_balance += amt
                balance_details.append(f"{bm}:{amt}")
                month_list.append(bm)
        starting_balance_month = ', '.join(month_list)
        starting_balance_details = '|'.join(balance_details)

        update_tenant(tenant_id, name, phone, amount, date_to_pay, month, reminder_days, preferred_channel, starting_balance, starting_balance_month, starting_balance_details)
        flash(f'Tenant "{name}" updated successfully!', 'success')
        return redirect(url_for('tenant_detail', tenant_id=tenant_id))

    return render_template('edit_tenant.html', tenant=tenant)

@app.route('/tenants/<int:tenant_id>/delete', methods=['POST'])
@login_required
def delete_tenant_view(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if tenant:
        delete_tenant(tenant_id)
        flash(f'Tenant "{tenant["name"]}" deleted.', 'success')
    return redirect(url_for('tenants_list'))

@app.route('/tenants/<int:tenant_id>/pay', methods=['GET', 'POST'])
@login_required
def make_payment(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenants_list'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        payment_date = request.form.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        pay_months = request.form.getlist('pay_months')

        if not pay_months:
            pay_months = [tenant['month']]

        per_month = amount / len(pay_months)
        for m in pay_months:
            record_payment(tenant_id, per_month, payment_date, m)

        month_names = ', '.join(pay_months)
        flash(f'Payment of {amount:,.0f} UGX recorded for {month_names} ({per_month:,.0f} UGX each)!', 'success')
        return redirect(url_for('tenant_detail', tenant_id=tenant_id))

    return render_template('make_payment.html', tenant=tenant, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/reminders')
@login_required
def reminders_view():
    reminders = check_and_generate_reminders()
    return render_template('reminders.html', reminders=reminders)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_view():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '')
        if query:
            results = search_tenants(query)
            for t in results:
                t['balance'] = calc_balance(t)
    return render_template('search.html', results=results, query=query)

@app.route('/summary')
@login_required
def summary_view():
    month = request.args.get('month', datetime.now().strftime('%B'))
    summary = get_monthly_summary(month)
    return render_template('summary.html', summary=summary, month=month)

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  TENANT MANAGEMENT SYSTEM")
    print("  Open your browser and go to:")
    print("  http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
