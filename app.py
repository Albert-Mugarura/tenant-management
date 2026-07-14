from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from database import (
    initialize_database, add_tenant, get_all_tenants, get_tenant_by_id,
    update_tenant, delete_tenant, record_payment, get_tenant_payments,
    search_tenants, get_monthly_summary, get_tenants_due_soon, get_overdue_tenants
)
from reminders import check_and_generate_reminders

app = Flask(__name__)
app.secret_key = 'tenant_management_secret_key_2026'

initialize_database()

@app.route('/')
def index():
    tenants = get_all_tenants()
    overdue = get_overdue_tenants()
    due_soon = get_tenants_due_soon(3)
    reminders = check_and_generate_reminders()

    total_expected = sum(t['amount_to_pay'] for t in tenants)
    total_collected = sum(t['amount_to_pay'] - t['balance'] for t in tenants)
    total_outstanding = sum(t['balance'] for t in tenants)

    return render_template('index.html',
        tenants=tenants,
        overdue=overdue,
        due_soon=due_soon,
        reminders=reminders,
        total_expected=total_expected,
        total_collected=total_collected,
        total_outstanding=total_outstanding,
        tenant_count=len(tenants)
    )

@app.route('/tenants')
def tenants_list():
    tenants = get_all_tenants()
    return render_template('tenants.html', tenants=tenants)

@app.route('/tenants/add', methods=['GET', 'POST'])
def add_tenant_view():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        amount = float(request.form['amount'])
        date_to_pay = request.form['date_to_pay']
        month = request.form['month']
        reminder_days = int(request.form.get('reminder_days', 3))
        preferred_channel = request.form.get('preferred_channel', 'both')

        add_tenant(name, phone, amount, date_to_pay, month, reminder_days, preferred_channel)
        flash(f'Tenant "{name}" added successfully!', 'success')
        return redirect(url_for('tenants_list'))

    return render_template('add_tenant.html')

@app.route('/tenants/<int:tenant_id>')
def tenant_detail(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenants_list'))

    payments = get_tenant_payments(tenant_id)
    return render_template('tenant_detail.html', tenant=tenant, payments=payments)

@app.route('/tenants/<int:tenant_id>/edit', methods=['GET', 'POST'])
def edit_tenant(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenants_list'))

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        amount = float(request.form['amount'])
        date_to_pay = request.form['date_to_pay']
        month = request.form['month']
        reminder_days = int(request.form.get('reminder_days', 3))
        preferred_channel = request.form.get('preferred_channel', 'both')

        update_tenant(tenant_id, name, phone, amount, date_to_pay, month, reminder_days, preferred_channel)
        flash(f'Tenant "{name}" updated successfully!', 'success')
        return redirect(url_for('tenant_detail', tenant_id=tenant_id))

    return render_template('edit_tenant.html', tenant=tenant)

@app.route('/tenants/<int:tenant_id>/delete', methods=['POST'])
def delete_tenant_view(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if tenant:
        delete_tenant(tenant_id)
        flash(f'Tenant "{tenant["name"]}" deleted.', 'success')
    return redirect(url_for('tenants_list'))

@app.route('/tenants/<int:tenant_id>/pay', methods=['GET', 'POST'])
def make_payment(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenants_list'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        payment_date = request.form.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        month = tenant['month']

        record_payment(tenant_id, amount, payment_date, month)
        flash(f'Payment of {amount:,.0f} UGX recorded!', 'success')
        return redirect(url_for('tenant_detail', tenant_id=tenant_id))

    return render_template('make_payment.html', tenant=tenant, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/reminders')
def reminders_view():
    reminders = check_and_generate_reminders()
    return render_template('reminders.html', reminders=reminders)

@app.route('/search', methods=['GET', 'POST'])
def search_view():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '')
        if query:
            results = search_tenants(query)
    return render_template('search.html', results=results, query=query)

@app.route('/summary')
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
    app.run(debug=True, host='0.0.0.0', port=5000)
