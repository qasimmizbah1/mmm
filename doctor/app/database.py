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

        await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

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


        


    yield
    await app.state.pool.close()
