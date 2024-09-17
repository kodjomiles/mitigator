### README.md

```md
# PostgreSQL Data Migration with FastAPI

This FastAPI-based project allows you to migrate encrypted data from one PostgreSQL table to another, decrypting the data during the migration process. The source and target table names can be provided dynamically, and sensitive credentials are securely stored in environment variables.

## Features

- Migrate data from any source PostgreSQL table to any destination table.
- Decrypt encrypted fields using `pgcrypto` during the migration.
- Store sensitive credentials like database URLs and encryption keys in a `.env` file.
- Handle various data types, including UUIDs and `TIMESTAMP WITH TIME ZONE`.
- Dynamically specify source and destination tables through API inputs.

## Requirements

- Python 3.8+
- PostgreSQL with the `pgcrypto` extension installed
- fastapi uvicorn
- asyncpg
- python-dotenv
- asyncer

## Installation

1. Clone the repository:

      ```bash
      git clone <repository-url>
      cd <repository-directory>
      ```

2. Create and activate a virtual environment:

      ```bash
      python3 -m venv venv
      source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
      ```
3. Install the required packages:

      ```bash
      pip install -r requirements.txt
      ```

4. Create a `.env` file in the root directory of your project with the following content:

      ```ini
      # .env file
   
      SOURCE_DB=postgres://username:password@source-hostname/source-database
      TARGET_DB=postgres://username:password@target-hostname/target-database
      KEY=your-encryption-key
      ```

   Replace the placeholder values with your actual PostgreSQL credentials and encryption key.

## Running the Project

1. Start the FastAPI server:

      ```bash
      uvicorn main:app --reload
      ```

2. The FastAPI server should now be running on `http://127.0.0.1:8000`. You can access the root endpoint at:

   ```
   GET http://127.0.0.1:8000/
   ```

   This will return a simple message indicating that the service is running.

## API Endpoints

### Migrate Data

**Endpoint**: `/migrate/`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Description**: Triggers the data migration process from the specified source table to the target table, decrypting fields in the process.

**Request Body**:
```json
{
    "source_table_name": "source_table_name",
    "destination_table_name": "destination_table_name"
}
```

**Example Request**:

```bash
curl -X POST "http://127.0.0.1:8000/migrate/" -H "Content-Type: application/json" -d '{"source_table_name": "Users", "destination_table_name": "Users_decrypted"}'
```

This will migrate data from the `Users` table in the source database to the `Users_decrypted` table in the target database.

**Response**:
```json
{
    "message": "Data migrated from 'Users' to 'Users_decrypted' successfully."
}
```

## Configuration

### Environment Variables

You can configure the following environment variables in your `.env` file:

- `SOURCE_DB`: The connection string for the source PostgreSQL database.
- `TARGET_DB`: The connection string for the target PostgreSQL database.
- `KEY`: The encryption key used for decryption in the `pgcrypto` extension.

### Customization

- You can customize the `get_postgres_type()` function in the code if you have specific data types to handle differently during migration.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## Contact

For any issues or questions, feel free to open an issue on the repository or contact the me.
```

### Additional Steps:

1. **Save this README as `README.md`** in your project directory.
2. **Add and commit it to your Git repository**:

   ```bash
   git add README.md
   git commit -m "Add README"
   git push origin <branch-name>
   ```