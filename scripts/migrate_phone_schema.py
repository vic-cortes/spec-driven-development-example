#!/usr/bin/env python3
"""
Database migration script for adding international phone support.

This script adds the country_code field to patient records with backward compatibility.
Supports both in-memory store and future SQLite implementations.
"""

import sqlite3
import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.logger import logger
from src.services.store import store


class PhoneMigration:
    """Migration handler for international phone support."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize migration handler.

        Args:
            db_path: Path to SQLite database file (optional, for future use)
        """
        self.db_path = db_path
        self.default_country_code = "+1"  # Default to US for existing records

    def migrate_sqlite(self) -> bool:
        """
        Migrate SQLite database to add country_code column.

        Returns:
            bool: True if migration successful, False otherwise
        """
        if not self.db_path:
            logger.warning(
                "No SQLite database path provided, skipping SQLite migration"
            )
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if country_code column already exists
                cursor.execute("PRAGMA table_info(patients)")
                columns = [col[1] for col in cursor.fetchall()]

                if "country_code" in columns:
                    logger.info("country_code column already exists in patients table")
                    return True

                # Add country_code column with default value
                logger.info("Adding country_code column to patients table")
                cursor.execute(
                    """
                    ALTER TABLE patients 
                    ADD COLUMN country_code TEXT DEFAULT '+1'
                """
                )

                # Update any existing NULL values to default US
                cursor.execute(
                    """
                    UPDATE patients 
                    SET country_code = '+1' 
                    WHERE country_code IS NULL
                """
                )

                # Add index for phone lookups with country code
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_patients_phone_country 
                    ON patients(phone, country_code)
                """
                )

                # Add constraints for country code validation
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS patients_new (
                        id TEXT PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        country_code TEXT NOT NULL DEFAULT '+1',
                        email TEXT,
                        birth_date DATE,
                        address TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                        CONSTRAINT check_country_code CHECK (country_code IN ('+1', '+52')),
                        CONSTRAINT check_phone_format CHECK (phone GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
                        CONSTRAINT check_phone_length CHECK (length(phone) = 10)
                    )
                """
                )

                conn.commit()
                logger.info("SQLite migration completed successfully")
                return True

        except sqlite3.Error as e:
            logger.error(f"SQLite migration failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during SQLite migration: {e}")
            return False

    def migrate_memory_store(self) -> bool:
        """
        Migrate in-memory store to support country_code field.

        This adds country_code field to existing Patient objects in the store.

        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            logger.info(
                "Starting in-memory store migration for international phone support"
            )

            # Get all patients from the store
            all_patients = []
            for patient_id in store._patients.keys():
                patient = store.get_patient(patient_id)
                if patient:
                    all_patients.append(patient)

            if not all_patients:
                logger.info("No existing patients found, migration not needed")
                return True

            logger.info(f"Found {len(all_patients)} existing patients to migrate")

            # For each patient, add country_code field if it doesn't exist
            migrated_count = 0
            for patient in all_patients:
                # Check if patient already has country_code attribute
                if not hasattr(patient, "country_code") or patient.country_code is None:
                    # Add default country code for US numbers
                    patient.country_code = self.default_country_code

                    # Update the patient in store
                    store.update_patient(patient)
                    migrated_count += 1

                    logger.info(
                        f"Added country_code {self.default_country_code} to patient {patient.masked_phone}"
                    )

            logger.info(
                f"Memory store migration completed: {migrated_count} patients updated"
            )
            return True

        except Exception as e:
            logger.error(f"Memory store migration failed: {e}")
            return False

    def run_migration(self) -> bool:
        """
        Run the appropriate migration based on storage type.

        Returns:
            bool: True if migration successful, False otherwise
        """
        logger.info("=== Starting International Phone Migration ===")

        success = True

        # Always try to migrate memory store (current implementation)
        if not self.migrate_memory_store():
            success = False

        # Try SQLite migration if database path is provided
        if self.db_path and Path(self.db_path).exists():
            if not self.migrate_sqlite():
                success = False

        if success:
            logger.info("=== Migration completed successfully ===")
        else:
            logger.error("=== Migration completed with errors ===")

        return success

    def validate_migration(self) -> bool:
        """
        Validate that migration was successful.

        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            logger.info("Validating migration results...")

            # Check that all patients in memory store have country_code
            all_patients = []
            for patient_id in store._patients.keys():
                patient = store.get_patient(patient_id)
                if patient:
                    all_patients.append(patient)

            for patient in all_patients:
                if not hasattr(patient, "country_code") or not patient.country_code:
                    logger.error(
                        f"Patient {patient.id} missing country_code after migration"
                    )
                    return False

                if patient.country_code not in ["+1", "+52"]:
                    logger.error(
                        f"Patient {patient.id} has invalid country_code: {patient.country_code}"
                    )
                    return False

            logger.info(
                f"Migration validation passed: {len(all_patients)} patients have valid country_code"
            )
            return True

        except Exception as e:
            logger.error(f"Migration validation failed: {e}")
            return False


def main():
    """Main migration script entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate database for international phone support"
    )
    parser.add_argument("--db-path", help="Path to SQLite database file (optional)")
    parser.add_argument(
        "--validate", action="store_true", help="Validate migration after running"
    )
    args = parser.parse_args()

    migration = PhoneMigration(db_path=args.db_path)

    # Run migration
    success = migration.run_migration()

    # Validate if requested
    if args.validate:
        validation_success = migration.validate_migration()
        success = success and validation_success

    if success:
        print("✅ Migration completed successfully")
        sys.exit(0)
    else:
        print("❌ Migration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
