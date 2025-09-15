#!/usr/bin/env python3
"""
Script for updating the USA-NPN ancillary database.

Combines API data fetching, CSV processing, database building, and refinement.
"""

import csv
import json
import logging
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import requests


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# API configuration
API_BASE_URL = "https://services.usanpn.org/npn_portal/"

API_ENDPOINTS = {
    "datasets": ["ancillary_dataset_data.csv", "observations/getDatasetDetails"],
    "networks": ["ancillary_network_data.csv", "networks/getPartnerNetworks"],
    "phenophases": [
        "ancillary_phenophase_definition_data.csv",
        "phenophases/getPhenophaseDefinitionDetails",
    ],
    "phenoclasses": [
        "ancillary_phenophase_data.csv",
        "phenophases/getPhenophaseDetails",
    ],
    "species": ["ancillary_species_data.csv", "species/getSpecies"],
}

# Database configuration
DB_PATH = PROJECT_ROOT / "src" / "usa_npn_mcp_server" / "data" / "ancillary_data.db"
TEMP_DIR = PROJECT_ROOT / ".github" / "db_sources"

CSV_FILES = {
    "species": "ancillary_species_data.csv",
    "phenophases": "ancillary_phenophase_definition_data.csv",
    "phenoclasses": "ancillary_phenophase_data.csv",
    "datasets": "ancillary_dataset_data.csv",
    "literature": "elicit_analysis.csv",  # Persistent file in .github/db_sources
    "networks": "ancillary_network_data.csv",
}


def fetch_api_data(endpoint: str) -> str:
    """Fetch data from API endpoint."""
    request_url = f"{API_BASE_URL}/{endpoint}.json"
    logger.info(f"Fetching data from: {request_url}")

    try:
        response = requests.get(request_url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from {request_url}: {e}")
        raise


def fetch_and_write_csv(filename: str, endpoint: str) -> None:
    """Fetch API data and write to CSV file in temp directory."""
    logger.info(f"Processing {filename} from endpoint {endpoint}")

    try:
        # Fetch data
        response_data = fetch_api_data(endpoint)
        data = json.loads(response_data)

        # Define CSV file path in temp directory
        csv_file = TEMP_DIR / filename
        csv_file.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON data to CSV
        if data:
            with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                # Write headers
                headers = data[0].keys()
                writer.writerow(headers)

                # Write rows
                for item in data:
                    writer.writerow(item.values())

            logger.info(f"Successfully wrote {len(data)} records to {csv_file}")
        else:
            logger.warning(f"No data received for {filename}")

    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}")
        raise


def download_all_api_data() -> None:
    """Download all API data to CSV files."""
    logger.info("Starting API data download...")

    for endpoint_info in API_ENDPOINTS.values():
        filename, endpoint = endpoint_info
        fetch_and_write_csv(filename, endpoint)

    logger.info("API data download completed")


def build_database() -> None:
    """Build SQLite database from CSV files."""
    logger.info(f"Building database at {DB_PATH}")

    try:
        # Create database connection
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)

        # Import each CSV into the database
        for table_name, file_path in CSV_FILES.items():
            csv_path = TEMP_DIR / file_path

            if not csv_path.exists():
                logger.warning(f"CSV file not found: {csv_path}")
                continue

            logger.info(f"Importing {file_path} to table {table_name}")
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            logger.info(f"Imported {len(df)} records to {table_name} table")

        conn.close()
        logger.info("Database build completed successfully")

    except Exception as e:
        logger.error(f"Database build failed: {e}")
        raise


def cleanup_temp_files() -> None:
    """Clean up temporary CSV files, keeping only elicit_analysis.csv."""
    logger.info("Cleaning up temporary files...")

    try:
        if not TEMP_DIR.exists():
            logger.info("Temp directory doesn't exist, nothing to clean up")
            return

        # List all files in temp directory
        temp_files = list(TEMP_DIR.glob("*.csv"))

        for temp_file in temp_files:
            # Keep elicit_analysis.csv, delete others
            if temp_file.name != "elicit_analysis.csv":
                temp_file.unlink()
                logger.info(f"Deleted temporary file: {temp_file.name}")
            else:
                logger.info(f"Keeping persistent file: {temp_file.name}")

        logger.info("Cleanup completed")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        # Don't raise here - cleanup failure shouldn't stop the pipeline


def modify_database() -> None:
    """Apply database modifications (column filtering/removal)."""
    logger.info("Applying database modifications...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get available tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        logger.info(f"Available tables: {tables}")

        # Modify datasets table - keep only specific columns
        if "datasets" in tables:
            logger.info("Modifying datasets table...")

            # Get current columns
            cursor.execute("PRAGMA table_info(datasets);")
            current_columns = [col[1] for col in cursor.fetchall()]

            # Define columns to keep
            keep_columns = [
                "dataset_id",
                "dataset_name",
                "dataset_description",
                "dataset_comments",
                "dataset_documentation_url",
            ]

            # Check which columns exist
            existing_keep_columns = [
                col for col in keep_columns if col in current_columns
            ]
            logger.info(f"Keeping columns in datasets table: {existing_keep_columns}")

            if existing_keep_columns:
                columns_str = ", ".join(existing_keep_columns)

                cursor.execute("BEGIN TRANSACTION;")
                cursor.execute(
                    f"CREATE TABLE datasets_temp AS SELECT {columns_str} FROM datasets;"
                )
                cursor.execute("DROP TABLE datasets;")
                cursor.execute("ALTER TABLE datasets_temp RENAME TO datasets;")
                cursor.execute("COMMIT;")

                logger.info("Successfully modified datasets table")
            else:
                logger.warning("No matching columns found in datasets table")

        # Modify phenoclasses table - remove phenophase_revision_comments column
        if "phenoclasses" in tables:
            logger.info("Modifying phenoclasses table...")

            # Get current columns
            cursor.execute("PRAGMA table_info(phenoclasses);")
            current_columns = [col[1] for col in cursor.fetchall()]

            if "phenophase_revision_comments" in current_columns:
                # Get all columns except the one to remove
                keep_columns = [
                    col
                    for col in current_columns
                    if col != "phenophase_revision_comments"
                ]
                columns_str = ", ".join(keep_columns)

                cursor.execute("BEGIN TRANSACTION;")
                cursor.execute(
                    f"CREATE TABLE phenoclasses_temp AS SELECT {columns_str} FROM phenoclasses;"
                )
                cursor.execute("DROP TABLE phenoclasses;")
                cursor.execute("ALTER TABLE phenoclasses_temp RENAME TO phenoclasses;")
                cursor.execute("COMMIT;")

                logger.info(
                    "Successfully removed phenophase_revision_comments column from phenoclasses table"
                )
            else:
                logger.info(
                    "phenophase_revision_comments column not found in phenoclasses table"
                )

        conn.close()
        logger.info("Database modifications completed successfully")

    except Exception as e:
        logger.error(f"Database modification failed: {e}")
        raise


def update_endpoints_file() -> None:
    """Update table lengths and headers in endpoints.py file."""
    logger.info("Updating endpoints.py with current table information...")

    try:
        # Get current table information
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get tables and their info
        table_info = {}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]

        for table in tables:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            # Get column headers
            cursor.execute(f"PRAGMA table_info({table});")
            headers = [col[1] for col in cursor.fetchall()]

            table_info[table] = {"length": row_count, "headers": headers}

        conn.close()

        # Read endpoints.py file
        endpoints_path = (
            PROJECT_ROOT / "src" / "usa_npn_mcp_server" / "utils" / "endpoints.py"
        )
        with open(endpoints_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update QueryReferenceMaterial description
        if "species" in table_info:
            # Update species table info
            species_info = table_info["species"]
            old_species_line = "Table: species, Length: \\d+, Headers:"
            new_species_line = (
                f"Table: species, Length: {species_info['length']}, Headers:"
            )
            content = __import__("re").sub(old_species_line, new_species_line, content)

        if "phenophases" in table_info:
            # Update phenophases table info
            pheno_info = table_info["phenophases"]
            old_pheno_line = "Table: phenophases, Length: \\d+, Headers:"
            new_pheno_line = (
                f"Table: phenophases, Length: {pheno_info['length']}, Headers:"
            )
            content = __import__("re").sub(old_pheno_line, new_pheno_line, content)

        if "phenoclasses" in table_info:
            # Update phenoclasses table info
            classes_info = table_info["phenoclasses"]
            old_classes_line = "Table: phenoclasses, Length: \\d+, Headers:"
            new_classes_line = (
                f"Table: phenoclasses, Length: {classes_info['length']}, Headers:"
            )
            content = __import__("re").sub(old_classes_line, new_classes_line, content)

        if "datasets" in table_info:
            # Update datasets table info
            datasets_info = table_info["datasets"]
            old_datasets_line = "Table: datasets, Length: \\d+, Headers:"
            new_datasets_line = (
                f"Table: datasets, Length: {datasets_info['length']}, Headers:"
            )
            content = __import__("re").sub(
                old_datasets_line, new_datasets_line, content
            )

        if "networks" in table_info:
            # Update networks table info
            networks_info = table_info["networks"]
            old_networks_line = "Table: networks, Length: \\d+, Headers:"
            new_networks_line = (
                f"Table: networks, Length: {networks_info['length']}, Headers:"
            )
            content = __import__("re").sub(
                old_networks_line, new_networks_line, content
            )

        # Write updated content back
        with open(endpoints_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("Successfully updated endpoints.py with current table information")

    except Exception as e:
        logger.error(f"Failed to update endpoints.py: {e}")
        # Don't raise here - this shouldn't stop the pipeline


def main() -> None:
    """Run the complete database update pipeline."""
    logger.info("Starting database update pipeline...")

    try:
        # Step 1: Download API data
        download_all_api_data()

        # Step 2: Build database from CSV files
        build_database()

        # Step 3: Apply database modifications
        modify_database()

        # Step 4: Update endpoints.py with current table info
        update_endpoints_file()

        # Step 5: Clean up temporary files (keeping elicit_analysis.csv)
        cleanup_temp_files()

        logger.info("Database update pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Database update pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
