"""
Seed database with sample data for testing
Creates 4-5 entries in each table
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import (
    User, Admin, Client, AdminClientMap, Document, Payment, Notification,
    ChatMessage, T1ReturnFlat, TaxReturn, TaxSection
)
from backend.app.auth.password import hash_password
from backend.app.database import engine

# Load environment variables
env_path = project_root / ".env"
load_dotenv(env_path)

# Sample data
SAMPLE_FIRST_NAMES = ["John", "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Amanda"]
SAMPLE_LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
SAMPLE_ADMIN_NAMES = ["Priya Patel", "Amit Singh", "Lisa Chen", "James Wilson"]
SAMPLE_STATUSES = ["documents_pending", "under_review", "awaiting_payment", "in_preparation", "filed", "completed"]
SAMPLE_PAYMENT_STATUSES = ["pending", "partial", "paid"]
SAMPLE_DOC_TYPES = ["receipt", "form", "statement", "certificate", "invoice"]
SAMPLE_DOC_NAMES = [
    "T4 Slip", "T5 Slip", "RRSP Statement", "Medical Receipts", "Charitable Donation Receipt",
    "Rental Income Statement", "Employment Contract", "Bank Statement", "Investment Statement",
    "Property Tax Receipt", "Moving Expenses Receipt", "Childcare Receipt", "Union Dues Receipt"
]
SAMPLE_SECTIONS = [
    "personal_info", "foreign_property", "medical_expenses", "charitable_donations",
    "moving_expenses", "self_employment", "rental_income", "work_from_home",
    "student", "union_member", "daycare", "professional_dues", "rrsp_fhsa"
]

def seed_database():
    """Seed all tables with sample data"""
    db = Session(engine)
    
    try:
        print("🌱 Starting database seeding...")
        
        # 1. Create Users (5 users)
        print("\n1. Creating Users...")
        users = []
        timestamp = int(datetime.now().timestamp())
        for i in range(5):
            first_name = random.choice(SAMPLE_FIRST_NAMES)
            last_name = random.choice(SAMPLE_LAST_NAMES)
            email = f"{first_name.lower()}.{last_name.lower()}.{timestamp}{i}@example.com"
            
            # Check if user already exists
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"   ⚠️  User {email} already exists, skipping...")
                users.append(existing)
                continue
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=f"+1-416-555-{1000 + i}",
                password_hash=hash_password("Password123!"),
                email_verified=True,
                is_active=True,
            )
            db.add(user)
            users.append(user)
        db.commit()
        print(f"   ✅ Created/Found {len(users)} users")
        
        # 2. Create Admins (3 admins: 2 admin, 1 superadmin)
        print("\n2. Creating Admins...")
        admins = []
        admin_roles = ["admin", "admin", "superadmin"]
        timestamp = int(datetime.now().timestamp())
        for i, role in enumerate(admin_roles):
            name = SAMPLE_ADMIN_NAMES[i]
            email = f"{name.lower().replace(' ', '.')}.{timestamp}@taxease.com"
            
            # Check if admin already exists
            existing = db.query(Admin).filter(Admin.email == email).first()
            if existing:
                print(f"   ⚠️  Admin {email} already exists, skipping...")
                admins.append(existing)
                continue
            
            admin = Admin(
                email=email,
                name=name,
                password_hash=hash_password("Admin123!"),
                role=role,
                permissions=["view_clients", "edit_clients", "view_documents", "edit_documents"] if role == "admin" else ["*"],
                is_active=True,
            )
            db.add(admin)
            admins.append(admin)
        db.commit()
        print(f"   ✅ Created/Found {len(admins)} admins")
        
        # 3. Create Clients (5 clients, one per user)
        print("\n3. Creating Clients...")
        clients = []
        for i, user in enumerate(users):
            # Check if client already exists for this user
            existing = db.query(Client).filter(Client.user_id == user.id).first()
            if existing:
                print(f"   ⚠️  Client for user {user.email} already exists, skipping...")
                clients.append(existing)
                continue
            
            filing_year = random.choice([2023, 2024, 2025])
            status = random.choice(SAMPLE_STATUSES)
            payment_status = random.choice(SAMPLE_PAYMENT_STATUSES)
            total_amount = random.uniform(1000, 5000)
            paid_amount = total_amount * random.uniform(0, 1) if payment_status != "pending" else 0
            
            client = Client(
                user_id=user.id,
                name=f"{user.first_name} {user.last_name}",
                email=user.email,
                phone=user.phone,
                filing_year=filing_year,
                status=status,
                payment_status=payment_status,
                total_amount=round(total_amount, 2),
                paid_amount=round(paid_amount, 2),
            )
            db.add(client)
            clients.append(client)
        db.commit()
        print(f"   ✅ Created/Found {len(clients)} clients")
        
        # 4. Create AdminClientMap (assign admins to clients)
        print("\n4. Creating Admin-Client Assignments...")
        assignments = []
        for i, client in enumerate(clients):
            # Assign first 2 clients to first admin, next 2 to second admin, last one to first admin
            admin = admins[i % 2] if len(admins) > 1 else admins[0]
            
            # Check if assignment already exists
            existing = db.query(AdminClientMap).filter(
                AdminClientMap.admin_id == admin.id,
                AdminClientMap.client_id == client.id
            ).first()
            if existing:
                print(f"   ⚠️  Assignment for client {client.name} already exists, skipping...")
                assignments.append(existing)
                continue
            
            assignment = AdminClientMap(
                admin_id=admin.id,
                client_id=client.id,
            )
            db.add(assignment)
            assignments.append(assignment)
        db.commit()
        print(f"   ✅ Created/Found {len(assignments)} admin-client assignments")
        
        # 5. Create Documents (5 per client = 25 documents)
        print("\n5. Creating Documents...")
        documents = []
        for client in clients:
            for j in range(5):
                doc_type = random.choice(SAMPLE_DOC_TYPES)
                doc_name = random.choice(SAMPLE_DOC_NAMES)
                section = random.choice(SAMPLE_SECTIONS) if j < 3 else None
                status = random.choice(["pending", "complete", "approved", "missing"])
                
                document = Document(
                    client_id=client.id,
                    name=f"{doc_name} - {client.name}",
                    original_filename=f"{doc_name.lower().replace(' ', '_')}.pdf",
                    file_type="pdf",
                    file_size=random.randint(50000, 500000),
                    file_path=f"./storage/uploads/{client.id}_{j}.pdf.enc",
                    encrypted=True,
                    encryption_key_hash="sample_hash",
                    section_name=section,
                    document_type=doc_type,
                    status=status,
                    version=1,
                    uploaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                )
                db.add(document)
                documents.append(document)
        db.commit()
        print(f"   ✅ Created {len(documents)} documents")
        
        # 6. Create Payments (4-5 per client = 20-25 payments)
        print("\n6. Creating Payments...")
        payments = []
        for client in clients:
            num_payments = random.randint(4, 5)
            for j in range(num_payments):
                is_request = j == 0  # First payment is a request
                amount = random.uniform(100, 1000)
                method = random.choice(["E-Transfer", "Credit Card", "Debit", "Bank Transfer"])
                status = "received" if not is_request else "requested"
                
                payment = Payment(
                    client_id=client.id,
                    created_by_id=admins[0].id,  # First admin creates all payments
                    amount=round(amount, 2),
                    method=method,
                    note=f"Payment for {client.filing_year} tax filing" if not is_request else f"Payment request for {client.filing_year}",
                    status=status,
                    is_request=is_request,
                )
                db.add(payment)
                payments.append(payment)
        db.commit()
        print(f"   ✅ Created {len(payments)} payments")
        
        # 7. Create Notifications (5 per client = 25 notifications)
        print("\n7. Creating Notifications...")
        notifications = []
        notification_types = ["status_update", "document_request", "payment_reminder", "message", "filing_complete"]
        for client in clients:
            for j in range(5):
                notif_type = random.choice(notification_types)
                titles = {
                    "status_update": "Status Updated",
                    "document_request": "Document Request",
                    "payment_reminder": "Payment Reminder",
                    "message": "New Message",
                    "filing_complete": "Filing Complete"
                }
                messages = {
                    "status_update": f"Your {client.filing_year} tax return status has been updated to {client.status}",
                    "document_request": "Please upload your T4 slip",
                    "payment_reminder": f"Payment of ${client.total_amount - client.paid_amount:.2f} is pending",
                    "message": "You have a new message from your tax preparer",
                    "filing_complete": f"Your {client.filing_year} tax return has been filed successfully"
                }
                
                notification = Notification(
                    client_id=client.id,
                    type=notif_type,
                    title=titles[notif_type],
                    message=messages[notif_type],
                    is_read=random.choice([True, False]),
                    created_by_id=admins[0].id,
                )
                db.add(notification)
                notifications.append(notification)
        db.commit()
        print(f"   ✅ Created {len(notifications)} notifications")
        
        # 8. Create ChatMessages (5 per client = 25 messages)
        print("\n8. Creating Chat Messages...")
        chat_messages = []
        sample_messages = [
            "Hello, I have a question about my tax return.",
            "When will my documents be reviewed?",
            "I've uploaded all required documents.",
            "Thank you for your help!",
            "Can you clarify the medical expense deduction?",
            "I've made the payment as requested.",
            "The status shows under review. What's next?",
            "All documents have been approved. Great!",
        ]
        for client in clients:
            for j in range(5):
                sender_role = "admin" if j % 2 == 0 else "client"
                message = random.choice(sample_messages)
                
                chat_message = ChatMessage(
                    user_id=client.user_id,
                    sender_role=sender_role,
                    message=message,
                    read_by_client=sender_role == "admin" and random.choice([True, False]),
                    read_by_admin=sender_role == "client" and random.choice([True, False]),
                )
                db.add(chat_message)
                chat_messages.append(chat_message)
        db.commit()
        print(f"   ✅ Created {len(chat_messages)} chat messages")
        
        # 9. Create T1ReturnFlat (5 returns)
        print("\n9. Creating T1 Returns (Flat)...")
        t1_returns = []
        for i, client in enumerate(clients):
            name_parts = client.name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else "John"
            last_name = name_parts[-1] if len(name_parts) > 1 else "Doe"
            has_children_val = random.choice([True, False])
            
            t1_return = T1ReturnFlat(
                client_id=client.id,
                filing_year=client.filing_year,
                status=client.status,
                payment_status=client.payment_status,
                first_name=first_name,
                last_name=last_name,
                sin=f"12345678{i}",  # 9 characters max
                date_of_birth=datetime(1980 + i, 1, 1).date(),
                marital_status=random.choice(["single", "married", "common_law"]),
                has_children=has_children_val,
                children_count=random.randint(1, 3) if has_children_val else None,
                has_foreign_property=random.choice([True, False]),
                has_medical_expenses=random.choice([True, False]),
                has_work_from_home=random.choice([True, False]),
                has_daycare_expenses=random.choice([True, False]),
                is_first_time_filer=random.choice([True, False]),
                sold_property_short_term=random.choice([True, False]),
                was_student=random.choice([True, False]),
                is_union_member=random.choice([True, False]),
                has_other_income=random.choice([True, False]),
                has_professional_dues=random.choice([True, False]),
                has_rrsp_fhsa=random.choice([True, False]),
                has_child_art_sport=random.choice([True, False]),
                has_disability_tax_credit=random.choice([True, False]),
                is_province_filer=random.choice([True, False]),
                has_self_employment=random.choice([True, False]),
                form_data={
                    "personalInfo": {
                        "firstName": first_name,
                        "lastName": last_name,
                        "sin": f"12345678{i}",
                    },
                    "filingYear": client.filing_year,
                },
            )
            db.add(t1_return)
            t1_returns.append(t1_return)
        db.commit()
        print(f"   ✅ Created {len(t1_returns)} T1 returns (flat)")
        
        # 10. Create TaxReturns (5 returns)
        print("\n10. Creating Tax Returns...")
        tax_returns = []
        for client in clients:
            tax_return = TaxReturn(
                client_id=client.id,
                filing_year=client.filing_year,
                status=client.status,
                form_data={
                    "personalInfo": {
                        "firstName": client.name.split()[0],
                        "lastName": client.name.split()[-1] if len(client.name.split()) > 1 else "Doe",
                    },
                    "filingYear": client.filing_year,
                },
                has_foreign_property=random.choice([True, False]),
                has_medical_expenses=random.choice([True, False]),
                has_charitable_donations=random.choice([True, False]),
                has_moving_expenses=random.choice([True, False]),
                is_self_employed=random.choice([True, False]),
                is_first_home_buyer=random.choice([True, False]),
                was_student=random.choice([True, False]),
                is_union_member=random.choice([True, False]),
                has_daycare_expenses=random.choice([True, False]),
            )
            db.add(tax_return)
            tax_returns.append(tax_return)
        db.commit()
        print(f"   ✅ Created {len(tax_returns)} tax returns")
        
        # 11. Create TaxSections (3-4 per tax return = 15-20 sections)
        print("\n11. Creating Tax Sections...")
        tax_sections = []
        for tax_return in tax_returns:
            num_sections = random.randint(3, 4)
            selected_sections = random.sample(SAMPLE_SECTIONS, min(num_sections, len(SAMPLE_SECTIONS)))
            for section_name in selected_sections:
                tax_section = TaxSection(
                    tax_return_id=tax_return.id,
                    section_name=section_name,
                    section_data={
                        "completed": random.choice([True, False]),
                        "notes": f"Section {section_name} data",
                    },
                    is_complete=random.choice([True, False]),
                    notes=f"Notes for {section_name} section",
                )
                db.add(tax_section)
                tax_sections.append(tax_section)
        db.commit()
        print(f"   ✅ Created {len(tax_sections)} tax sections")
        
        print("\n" + "="*50)
        print("✅ Database seeding completed successfully!")
        print("="*50)
        print(f"\nSummary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Admins: {len(admins)}")
        print(f"  - Clients: {len(clients)}")
        print(f"  - Admin-Client Assignments: {len(assignments)}")
        print(f"  - Documents: {len(documents)}")
        print(f"  - Payments: {len(payments)}")
        print(f"  - Notifications: {len(notifications)}")
        print(f"  - Chat Messages: {len(chat_messages)}")
        print(f"  - T1 Returns (Flat): {len(t1_returns)}")
        print(f"  - Tax Returns: {len(tax_returns)}")
        print(f"  - Tax Sections: {len(tax_sections)}")
        print(f"\nTotal records created: {len(users) + len(admins) + len(clients) + len(assignments) + len(documents) + len(payments) + len(notifications) + len(chat_messages) + len(t1_returns) + len(tax_returns) + len(tax_sections)}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

