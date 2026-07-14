import sys
import os
from datetime import datetime
from database import (
    initialize_database, add_tenant, get_all_tenants, get_tenant_by_id,
    update_tenant, delete_tenant, record_payment, get_tenant_payments,
    search_tenants, get_monthly_summary
)
from reminders import check_and_generate_reminders, display_reminders


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("\n" + "="*70)
    print("     TENANT MANAGEMENT SYSTEM - ALINAITWE JOSEPH")
    print("     Landlord: Alinaitwe Joseph")
    print("="*70)

def print_menu():
    print("\n--- MAIN MENU ---")
    print("1.  Add New Tenant")
    print("2.  View All Tenants")
    print("3.  Search Tenant")
    print("4.  Update Tenant")
    print("5.  Delete Tenant")
    print("6.  Record Payment")
    print("7.  View Tenant Payments")
    print("8.  Check Reminders")
    print("9.  Monthly Summary")
    print("10. Exit")
    print("-"*40)

def get_month_name():
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[datetime.now().month - 1]

def add_new_tenant():
    print("\n--- ADD NEW TENANT ---")
    name = input("Tenant Name: ").strip()
    phone = input("Phone Number: ").strip()
    amount = float(input("Monthly Rent (UGX): "))
    date_str = input("Next Payment Date (YYYY-MM-DD): ").strip()
    month = get_month_name()

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print("[ERROR] Invalid date format. Use YYYY-MM-DD")
        return

    tenant_id = add_tenant(name, phone, amount, date_str, month)
    print(f"\n[OK] Tenant '{name}' added successfully! (ID: {tenant_id})")

def view_all_tenants():
    tenants = get_all_tenants()
    if not tenants:
        print("\n[INFO] No tenants found.")
        return

    print("\n" + "="*100)
    print(f"{'ID':<5} {'Name':<25} {'Phone':<15} {'Rent':<12} {'Due Date':<12} {'Balance':<12} {'Month':<12}")
    print("="*100)

    for t in tenants:
        balance_indicator = "[!]" if t['balance'] > 0 else "[OK]"
        print(f"{t['id']:<5} {t['name']:<25} {t['phone']:<15} {t['amount_to_pay']:>10,.0f} {t['date_to_pay']:<12} {t['balance']:>10,.0f} {balance_indicator} {t['month']:<12}")

    print("="*100)
    print(f"Total tenants: {len(tenants)}")

def search_tenant():
    print("\n--- SEARCH TENANT ---")
    search_term = input("Enter name to search: ").strip()

    tenants = search_tenants(search_term)
    if not tenants:
        print(f"[INFO] No tenants found matching '{search_term}'")
        return

    print(f"\nFound {len(tenants)} tenant(s):")
    print("-"*80)
    for t in tenants:
        print(f"  ID: {t['id']} | Name: {t['name']} | Phone: {t['phone']}")
        print(f"  Rent: {t['amount_to_pay']:,.0f} UGX | Due: {t['date_to_pay']} | Balance: {t['balance']:,.0f} UGX")
        print("-"*80)

def update_existing_tenant():
    print("\n--- UPDATE TENANT ---")
    tenant_id = int(input("Enter Tenant ID to update: "))

    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        print("[ERROR] Tenant not found!")
        return

    print(f"\nCurrent Details:")
    print(f"  Name: {tenant['name']}")
    print(f"  Phone: {tenant['phone']}")
    print(f"  Amount: {tenant['amount_to_pay']:,.0f} UGX")
    print(f"  Due Date: {tenant['date_to_pay']}")
    print(f"  Month: {tenant['month']}")

    print("\nLeave blank to keep current value.")
    name = input(f"New Name [{tenant['name']}]: ").strip() or tenant['name']
    phone = input(f"New Phone [{tenant['phone']}]: ").strip() or tenant['phone']
    amount = input(f"New Amount [{tenant['amount_to_pay']}]: ").strip()
    amount = float(amount) if amount else tenant['amount_to_pay']
    date_str = input(f"New Due Date [{tenant['date_to_pay']}]: ").strip() or tenant['date_to_pay']
    month = input(f"New Month [{tenant['month']}]: ").strip() or tenant['month']

    update_tenant(tenant_id, name, phone, amount, date_str, month)
    print("\n[OK] Tenant updated successfully!")

def delete_existing_tenant():
    print("\n--- DELETE TENANT ---")
    tenant_id = int(input("Enter Tenant ID to delete: "))

    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        print("[ERROR] Tenant not found!")
        return

    print(f"\nTenant to delete: {tenant['name']}")
    confirm = input("Are you sure? (yes/no): ").strip().lower()

    if confirm == 'yes':
        delete_tenant(tenant_id)
        print("[OK] Tenant deleted successfully!")
    else:
        print("[INFO] Deletion cancelled.")

def record_payment_for_tenant():
    print("\n--- RECORD PAYMENT ---")
    tenant_id = int(input("Enter Tenant ID: "))

    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        print("[ERROR] Tenant not found!")
        return

    print(f"\nTenant: {tenant['name']}")
    print(f"Current Balance: {tenant['balance']:,.0f} UGX")

    amount = float(input("Amount Paid (UGX): "))
    payment_date = input("Payment Date (YYYY-MM-DD) or press Enter for today: ").strip()
    if not payment_date:
        payment_date = datetime.now().strftime('%Y-%m-%d')

    month = tenant['month']
    record_payment(tenant_id, amount, payment_date, month)

    updated_tenant = get_tenant_by_id(tenant_id)
    print(f"\n[OK] Payment of {amount:,.0f} UGX recorded!")
    print(f"Remaining Balance: {updated_tenant['balance']:,.0f} UGX")

def view_tenant_payments():
    print("\n--- VIEW TENANT PAYMENTS ---")
    tenant_id = int(input("Enter Tenant ID: "))

    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        print("[ERROR] Tenant not found!")
        return

    payments = get_tenant_payments(tenant_id)

    print(f"\nPayment History for: {tenant['name']}")
    print(f"Phone: {tenant['phone']}")
    print(f"Monthly Rent: {tenant['amount_to_pay']:,.0f} UGX")
    print(f"Current Balance: {tenant['balance']:,.0f} UGX")
    print("-"*60)

    if not payments:
        print("[INFO] No payments recorded yet.")
        return

    total_paid = 0
    for p in payments:
        total_paid += p['amount_paid']
        print(f"  Date: {p['payment_date']} | Amount: {p['amount_paid']:>10,.0f} UGX | Month: {p['month']}")

    print("-"*60)
    print(f"  Total Paid: {total_paid:>10,.0f} UGX")

def check_reminders():
    print("\n--- CHECKING REMINDERS ---")
    reminders = check_and_generate_reminders()
    display_reminders(reminders)

def view_monthly_summary():
    print("\n--- MONTHLY SUMMARY ---")
    month = input(f"Enter month name (e.g., {get_month_name()}): ").strip()

    summary = get_monthly_summary(month)
    if summary and summary['total_tenants'] > 0:
        print(f"\nSummary for {month}:")
        print(f"  Total Tenants: {summary['total_tenants']}")
        print(f"  Expected Revenue: {summary['total_expected']:,.0f} UGX")
        print(f"  Collected: {summary['total_collected']:,.0f} UGX")
        print(f"  Outstanding: {summary['total_outstanding']:,.0f} UGX")
        if summary['total_expected'] > 0:
            collection_rate = (summary['total_collected'] / summary['total_expected']) * 100
            print(f"  Collection Rate: {collection_rate:.1f}%")
    else:
        print(f"[INFO] No data found for {month}")

def main():
    initialize_database()

    while True:
        print_header()
        print_menu()

        try:
            choice = input("Select option (1-10): ").strip()

            if choice == '1':
                add_new_tenant()
            elif choice == '2':
                view_all_tenants()
            elif choice == '3':
                search_tenant()
            elif choice == '4':
                update_existing_tenant()
            elif choice == '5':
                delete_existing_tenant()
            elif choice == '6':
                record_payment_for_tenant()
            elif choice == '7':
                view_tenant_payments()
            elif choice == '8':
                check_reminders()
            elif choice == '9':
                view_monthly_summary()
            elif choice == '10':
                print("\n[GOODBYE] Thank you for using Tenant Management System!")
                sys.exit(0)
            else:
                print("[ERROR] Invalid option. Please try again.")

        except KeyboardInterrupt:
            print("\n\n[EXIT] Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] {e}")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
