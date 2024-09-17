from fastapi import FastAPI, HTTPException
import asyncpg
from typing import List, Tuple, Any
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataMigrationLogger")

# Load sensitive data from environment variables
SOURCE_DB = os.getenv("SOURCE_DB")
TARGET_DB = os.getenv("TARGET_DB")
KEY = os.getenv("KEY")

app = FastAPI()

# Function to fetch all columns from the given table
async def fetch_table_columns(source_conn, table_name: str) -> List[Tuple[str, str]]:
    query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
    """
    columns = await source_conn.fetch(query)
    if not columns:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in source database.")
    return [(record['column_name'], record['data_type']) for record in columns]

# Function to check if the target table exists, drop it if it does, and create the table
async def setup_target_table(target_conn, columns: List[Tuple[str, str]], destination_table_name: str):
    table_exists_query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = '{destination_table_name}'
        );
    """
    exists_result = await target_conn.fetchval(table_exists_query)

    if exists_result:
        logger.info(f"Dropping existing '{destination_table_name}' table in target database.")
        drop_table_query = f'DROP TABLE IF EXISTS "{destination_table_name}";'
        await target_conn.execute(drop_table_query)

    logger.info(f"Creating '{destination_table_name}' table in target database.")
    create_table_columns = ", ".join([
        f'"{col}" {get_postgres_type(data_type)}' for col, data_type in columns
    ])
    create_table_query = f"""
        CREATE TABLE "{destination_table_name}" (
            {create_table_columns}
        );
    """
    await target_conn.execute(create_table_query)
    logger.info(f"'{destination_table_name}' table created successfully in target database.")

def get_postgres_type(data_type: str) -> str:
    if data_type == "uuid":
        return "UUID"
    elif "timestamp" in data_type:
        return "TIMESTAMP WITH TIME ZONE"
    return "TEXT"

async def fetch_and_decrypt_data(source_conn, columns: List[Tuple[str, str]], table_name: str) -> List[List[Any]]:
    encrypted_columns = [col for col, data_type in columns if data_type not in ['uuid', 'timestamp with time zone', 'timestamp without time zone']]
    non_encrypted_columns = [col for col, data_type in columns if data_type in ['uuid', 'timestamp with time zone', 'timestamp without time zone']]

    encrypted_select_query = ", ".join([f'PGP_SYM_DECRYPT(CAST("{col}" AS bytea), $1) AS "{col}"' for col in encrypted_columns])
    non_encrypted_select_query = ", ".join([f'"{col}"' for col in non_encrypted_columns])

    if encrypted_select_query and non_encrypted_select_query:
        select_query = f'"id", {encrypted_select_query}, {non_encrypted_select_query}'
    elif encrypted_select_query:
        select_query = f'"id", {encrypted_select_query}'
    else:
        select_query = f'"id", {non_encrypted_select_query}'

    logger.info(f"Decrypting data from source table '{table_name}'...")
    query = f'SELECT {select_query} FROM "{table_name}"'
    users = await source_conn.fetch(query, KEY)
    logger.info(f"Found {len(users)} records in '{table_name}'.")
    return users

def handle_datetime(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
    return value

async def insert_decrypted_data(target_conn, users: List[List[Any]], columns: List[Tuple[str, str]], destination_table_name: str):
    column_names = ", ".join([f'"{col}"' for col, _ in columns])
    placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])

    insert_query = f"""
        INSERT INTO "{destination_table_name}" ({column_names}) 
        VALUES ({placeholders})
    """

    async with target_conn.transaction():
        for user in users:
            values = [handle_datetime(user[col]) if isinstance(user[col], datetime) else user[col] for col, _ in columns]
            await target_conn.execute(insert_query, *values)

    logger.info(f"Inserted {len(users)} records into the target table '{destination_table_name}'.")

# Function to fetch data from the newly created destination table
async def fetch_data_from_target_table(target_conn, destination_table_name: str) -> List[dict]:
    query = f'SELECT * FROM "{destination_table_name}";'
    rows = await target_conn.fetch(query)
    result = [dict(row) for row in rows]
    return result

@app.post("/migrate/")
async def migrate_data(source_table_name: str, destination_table_name: str):
    source_conn = await asyncpg.connect(SOURCE_DB)
    target_conn = await asyncpg.connect(TARGET_DB)
    try:
        columns = await fetch_table_columns(source_conn, source_table_name)
        logger.info(f"Fetched columns: {columns}")

        await setup_target_table(target_conn, columns, destination_table_name)

        users = await fetch_and_decrypt_data(source_conn, columns, source_table_name)
        logger.info(f"Fetched {len(users)} records from source table '{source_table_name}'.")

        await insert_decrypted_data(target_conn, users, columns, destination_table_name)
        logger.info(f"Data migration completed from '{source_table_name}' to '{destination_table_name}'.")

        # Fetch data from the newly created destination table
        new_data = await fetch_data_from_target_table(target_conn, destination_table_name)
        logger.info(f"Fetched {len(new_data)} records from the destination table '{destination_table_name}'.")

    finally:
        await source_conn.close()
        await target_conn.close()

    return {"message": f"Data migrated from '{source_table_name}' to '{destination_table_name}' successfully.", "data": new_data}

@app.get("/")
async def read_root():
    logger.info("Service running.RESCUE !!!!!!!!!!")
    return {"message": "Data migration service is running!"}
