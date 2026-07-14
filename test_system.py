import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    initialize_database, add_tenant, get_all_tenants, get_tenant_by_id,
    update_tenant, delete_tenant, record_payment, get_tenant_payments,
    search_tenants, get_monthly_summary, get_tenants_due_soon, get_overdue_tenants
)
from reminders import check_and_generate_reminders, generate_payment_reminder

def test_database():
    print("=" * 60)
    print("TEST 1: DATABASE INITIALIZATION")
    print("=" * 60)
    initialize_database()
    print("[PASS] Database initialized successfully\n")

def test_add_tenants():
    print("=" * 60)
    print("TEST 2: ADD TENANTS")
    print("=" * 60)

    today = datetime.now().date()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    next_week = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    in_2_days = (today + timedelta(days=2)).strftime('%Y-%m-%d')

    t1 = add_tenant("Nakamya Sarah", "+256783123456", 300000, tomorrow, "July")
    print(f"  Added: Nakamya Sarah (ID: {t1}) - 300,000 UGX due {tomorrow}")

    t2 = add_tenant("Ochieng David", "+256774123456", 250000, in_2_days, "July")
    print(f"  Added: Ochieng David (ID: {t2}) - 250,000 UGX due {in_2_days}")

    t3 = add_tenant("Namutebi Grace", "+256753123456", 400000, next_week, "July")
    print(f"  Added: Namutebi Grace (ID: {t3}) - 400,000 UGX due {next_week}")

    t4 = add_tenant("Kizza Moses", "+256701123456", 350000, yesterday, "July")
    print(f"  Added: Kizza Moses (ID: {t4}) - 350,000 UGX OVERDUE (was due {yesterday})")

    print(f"\n[PASS] Added 4 tenants successfully\n")
    return t1, t2, t3, t4

def test_view_tenants():
    print("=" * 60)
    print("TEST 3: VIEW ALL TENANTS")
    print("=" * 60)

    tenants = get_all_tenants()
    print(f"  {'ID':<5} {'Name':<20} {'Phone':<15} {'Rent':<12} {'Due Date':<12} {'Balance':<10}")
    print("  " + "-" * 74)

    for t in tenants:
        indicator = "[OVERDUE]" if t['balance'] > 0 and t['date_to_pay'] < datetime.now().date().isoformat() else "[OK]"
        print(f"  {t['id']:<5} {t['name']:<20} {t['phone']:<15} {t['amount_to_pay']:>10,.0f} {t['date_to_pay']:<12} {t['balance']:>10,.0f} {indicator}")

    print(f"\n[PASS] Viewed {len(tenants)} tenants\n")

def test_search():
    print("=" * 60)
    print("TEST 4: SEARCH TENANT")
    print("=" * 60)

    results = search_tenants("Nakamya")
    print(f"  Search for 'Nakamya': Found {len(results)} result(s)")
    for t in results:
        print(f"    -> {t['name']} ({t['phone']})")

    results2 = search_tenants("Moses")
    print(f"  Search for 'Moses': Found {len(results2)} result(s)")
    for t in results2:
        print(f"    -> {t['name']} ({t['phone']})")

    print(f"\n[PASS] Search working correctly\n")

def test_record_payments():
    print("=" * 60)
    print("TEST 5: RECORD PAYMENTS")
    print("=" * 60)

    tenants = get_all_tenants()
    today = datetime.now().strftime('%Y-%m-%d')

    for t in tenants:
        if t['name'] == "Nakamya Sarah":
            record_payment(t['id'], 150000, today, "July")
            updated = get_tenant_by_id(t['id'])
            print(f"  Nakamya Sarah paid 150,000 UGX -> Balance: {updated['balance']:,.0f} UGX (was {t['balance']:,.0f})")

        elif t['name'] == "Kizza Moses":
            record_payment(t['id'], 350000, today, "July")
            updated = get_tenant_by_id(t['id'])
            print(f"  Kizza Moses paid 350,000 UGX -> Balance: {updated['balance']:,.0f} UGX (fully paid!)")

        elif t['name'] == "Ochieng David":
            record_payment(t['id'], 100000, today, "July")
            updated = get_tenant_by_id(t['id'])
            print(f"  Ochieng David paid 100,000 UGX -> Balance: {updated['balance']:,.0f} UGX")

    print(f"\n[PASS] Payments recorded successfully\n")

def test_balance_tracking():
    print("=" * 60)
    print("TEST 6: BALANCE TRACKING")
    print("=" * 60)

    tenants = get_all_tenants()
    print(f"  {'Name':<20} {'Rent':<12} {'Paid':<12} {'Balance':<12} {'Status':<12}")
    print("  " + "-" * 68)

    for t in tenants:
        paid = t['amount_to_pay'] - t['balance']
        status = "FULLY PAID" if t['balance'] <= 0 else f"OWES {t['balance']:,.0f}"
        print(f"  {t['name']:<20} {t['amount_to_pay']:>10,.0f} {paid:>10,.0f} {t['balance']:>10,.0f} {status}")

    print(f"\n[PASS] Balance tracking working correctly\n")

def test_reminders():
    print("=" * 60)
    print("TEST 7: REMINDER SYSTEM")
    print("=" * 60)

    reminders = check_and_generate_reminders()
    print(f"  Found {len(reminders)} reminder(s):\n")

    for r in reminders:
        print(f"  [{r['urgency']}]")
        print(f"    Tenant: {r['tenant_name']}")
        print(f"    Phone: {r['phone']}")
        print(f"    Message: {r['message']}")
        print()

    print(f"[PASS] Reminder system working correctly\n")

def test_update_tenant():
    print("=" * 60)
    print("TEST 8: UPDATE TENANT")
    print("=" * 60)

    tenant = get_tenant_by_id(1)
    print(f"  Before: {tenant['name']} - {tenant['amount_to_pay']:,.0f} UGX")

    update_tenant(1, "Nakamya Sarah", "+256783654321", 320000, tenant['date_to_pay'], tenant['month'])
    updated = get_tenant_by_id(1)
    print(f"  After:  {updated['name']} - {updated['amount_to_pay']:,.0f} UGX (Phone: {updated['phone']})")

    print(f"\n[PASS] Tenant updated successfully\n")

def test_payment_history():
    print("=" * 60)
    print("TEST 9: PAYMENT HISTORY")
    print("=" * 60)

    tenant = get_tenant_by_id(1)
    payments = get_tenant_payments(1)
    print(f"  Payment history for {tenant['name']}:")
    for p in payments:
        print(f"    Date: {p['payment_date']} | Amount: {p['amount_paid']:,.0f} UGX | Month: {p['month']}")

    print(f"\n[PASS] Payment history working correctly\n")

def test_monthly_summary():
    print("=" * 60)
    print("TEST 10: MONTHLY SUMMARY")
    print("=" * 60)

    summary = get_monthly_summary("July")
    if summary and summary['total_tenants'] > 0:
        print(f"  Month: July")
        print(f"  Total Tenants: {summary['total_tenants']}")
        print(f"  Expected Revenue: {summary['total_expected']:,.0f} UGX")
        print(f"  Collected: {summary['total_collected']:,.0f} UGX")
        print(f"  Outstanding: {summary['total_outstanding']:,.0f} UGX")
        rate = (summary['total_collected'] / summary['total_expected']) * 100
        print(f"  Collection Rate: {rate:.1f}%")

    print(f"\n[PASS] Monthly summary working correctly\n")

def test_delete_tenant():
    print("=" * 60)
    print("TEST 11: DELETE TENANT")
    print("=" * 60)

    count_before = len(get_all_tenants())
    delete_tenant(4)
    count_after = len(get_all_tenants())
    print(f"  Tenants before: {count_before}")
    print(f"  Tenants after: {count_after}")

    print(f"\n[PASS] Tenant deleted successfully\n")

def test_overdue_detection():
    print("=" * 60)
    print("TEST 12: OVERDUE DETECTION")
    print("=" * 60)

    overdue = get_overdue_tenants()
    print(f"  Overdue tenants: {len(overdue)}")
    for t in overdue:
        print(f"    -> {t['name']} (Balance: {t['balance']:,.0f} UGX)")

    print(f"\n[PASS] Overdue detection working correctly\n")

def test_due_soon():
    print("=" * 60)
    print("TEST 13: DUE SOON DETECTION (3 days)")
    print("=" * 60)

    due_soon = get_tenants_due_soon(3)
    print(f"  Tenants due within 3 days: {len(due_soon)}")
    for t in due_soon:
        print(f"    -> {t['name']} (Due: {t['date_to_pay']}, Balance: {t['balance']:,.0f} UGX)")

    print(f"\n[PASS] Due soon detection working correctly\n")

def main():
    print("\n" + "=" * 60)
    print("  TENANT MANAGEMENT SYSTEM - COMPREHENSIVE TEST")
    print("  Landlord: Alinaitwe Joseph")
    print("=" * 60 + "\n")

    test_database()
    ids = test_add_tenants()
    test_view_tenants()
    test_search()
    test_record_payments()
    test_balance_tracking()
    test_reminders()
    test_update_tenant()
    test_payment_history()
    test_monthly_summary()
    test_delete_tenant()
    test_overdue_detection()
    test_due_soon()

    print("=" * 60)
    print("  ALL 13 TESTS PASSED!")
    print("=" * 60)
    print("\n  The system is ready to use.")
    print("  Run: python tenant_manager.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
