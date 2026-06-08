"""Seed script for development environment."""
import sys
import os

# Guard: only run in development mode
if os.getenv("APP_ENV", "development") != "development":
    raise SystemExit("seed_dev.py must only be run in development mode")

from datetime import datetime, timedelta

# Add parent directory to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.models import Tenant, User, Patient, Episode
from app.core.security import get_password_hash

def seed():
    # Ensure tables exist (Alembic should handle this usually, but safe for dev)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Create Default Tenant
        tenant = db.query(Tenant).filter(Tenant.slug == "medflow-dev").first()
        if not tenant:
            tenant = Tenant(
                name="MedFlow Development Center",
                slug="medflow-dev",
                specialty="Multidisciplinaire",
                address="123 Rue de la Sante, Paris",
                phone="0140506070",
                email="contact@medflow.fr"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"Tenant created: {tenant.name}")
        else:
            print("Tenant already exists")

        # 2. Create Users
        password = "medflow2026"
        hashed_pw = get_password_hash(password)
        
        users_data = [
            {"email": "admin@medflow.fr", "name": "Admin MedFlow", "role": "admin"},
            {"email": "doctor@medflow.fr", "name": "Dr. Jean Dupont", "role": "doctor", "specialty": "Urgentiste"},
            {"email": "ipa@medflow.fr", "name": "Marie IPA", "role": "ipa"},
            {"email": "sec@medflow.fr", "name": "Sophie Secretaire", "role": "sec"},
        ]
        
        for u_info in users_data:
            user = db.query(User).filter(User.email == u_info["email"]).first()
            if not user:
                user = User(
                    tenant_id=tenant.id,
                    email=u_info["email"],
                    hashed_password=hashed_pw,
                    full_name=u_info["name"],
                    role=u_info["role"],
                    specialty=u_info.get("specialty")
                )
                db.add(user)
                print(f"User created: {u_info['email']} (role: {u_info['role']})")
        
        db.commit()

        # 3. Create Sample Data (Patients & Episodes)
        if db.query(Patient).filter(Patient.tenant_id == tenant.id).count() == 0:
            p1 = Patient(
                tenant_id=tenant.id,
                last_name="Martin",
                first_name="Lucas",
                gender="M",
                date_of_birth=datetime(1985, 5, 20),
                phone="0611223344"
            )
            p2 = Patient(
                tenant_id=tenant.id,
                last_name="Bernard",
                first_name="Julie",
                gender="F",
                date_of_birth=datetime(1992, 11, 10),
                phone="0622334455"
            )
            db.add_all([p1, p2])
            db.commit()
            db.refresh(p1)
            db.refresh(p2)
            
            # Episodes
            ep1 = Episode(
                tenant_id=tenant.id,
                patient_id=p1.id,
                status="collecting",
                chief_complaint="Douleur thoracique aigue",
                intake_method="field"
            )
            ep2 = Episode(
                tenant_id=tenant.id,
                patient_id=p2.id,
                status="pending",
                chief_complaint="Fievre et courbatures",
                intake_method="digital"
            )
            db.add_all([ep1, ep2])
            db.commit()
            print("Sample patients and episodes created.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
