import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
import os


load_dotenv()


DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(**DB_CONFIG)
    
    async with app.state.pool.acquire() as conn:

    

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                doctor_id UUID NOT NULL,
                patient_id UUID NOT NULL,
                therapist_id UUID NOT NULL,

                urgency_level TEXT NOT NULL CHECK (
                    urgency_level IN ('Low','Medium','High','Emergency')
                ),

                preferred_modality TEXT NOT NULL CHECK (
                    preferred_modality IN (
                        'Therapy',
                        'Psychiatric Assessment',
                        'Both'
                    )
                ),

                clinical_presentation TEXT NOT NULL,
                chief_complaint TEXT NOT NULL,
                additional_requirements TEXT,

                status TEXT NOT NULL DEFAULT 'pending' CHECK (
                    status IN (
                        'pending',
                        'accepted',
                        'rejected',
                        'in_progress',
                        'completed'
                    )
                ),

                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

                CONSTRAINT fk_doctor
                    FOREIGN KEY (doctor_id)
                    REFERENCES app_user(id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_patient
                    FOREIGN KEY (patient_id)
                    REFERENCES app_user(id)
                    ON DELETE CASCADE,

                CONSTRAINT fk_therapist
                    FOREIGN KEY (therapist_id)
                    REFERENCES app_user(id)
                    ON DELETE CASCADE
            );
    """)


        
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS doctor_profile (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            doctor_id UUID UNIQUE NOT NULL,

            full_name TEXT NOT NULL,
            license_number TEXT NOT NULL,
            registration TEXT NOT NULL,

            clinic_name TEXT,
            medical_field TEXT NOT NULL,

            address TEXT NOT NULL,
            phone TEXT NOT NULL,

            gender TEXT CHECK (
                gender IN ('male','female','other')
            ),

            dob DATE NOT NULL,

            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT fk_doctor_user
                FOREIGN KEY (doctor_id)
                REFERENCES app_user(id)
                ON DELETE CASCADE
        );
    """)  


    yield
    await app.state.pool.close()
