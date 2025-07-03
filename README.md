# Global Prime Partners (GPP) SFTP Data Ingestion Client

This project implements a secure and automated data ingestion pipeline for retrieving CSV-based financial reports from an SFTP server operated by **GPP Group** ([gpp.group](https://gpp.group) / [Titan IS](https://titan-is.com)). It extracts, transforms, and stores this data into a Microsoft SQL Server database for subsequent analysis and operational use.

## Overview

### Purpose

The application performs the following automated tasks:
- Establishes a secure SFTP connection to GPP’s data repository.
- Detects and downloads new CSV reports.
- Transforms and consolidates raw CSVs into structured dataframes.
- Inserts the processed data into SQL Server tables.
- Avoids redundant ingestion using timestamp-based filters.

This solution is suitable for financial data teams integrating third-party position, transaction, or custody reports into internal systems.

## Source of Data

All data is retrieved from an SFTP server hosted by **GPP Group** or its data platform **Titan IS**:

- Reports are stored under `/Reports` on the SFTP host.
- Filenames follow a structured timestamp format (e.g., `20240501_positions.csv`).
- Each file corresponds to specific financial snapshots (positions, holdings, etc.).

Access requires a valid username/password and server configuration.

## Application Flow

The entry point `main.py` orchestrates the workflow:

1. **Connect to SFTP**:
   - Authenticates and connects via `paramiko` to fetch new CSV reports.

2. **Filter Reports**:
   - Uses the last inserted timestamp (from the DB) to avoid reprocessing old files.

3. **Parse Files**:
   - CSVs are read using `pandas` and filtered to discard invalid rows.
   - Each file is mapped to a derived table name based on naming conventions.

4. **Transform & Insert**:
   - Cleaned data is passed through a transformer and inserted into the configured SQL Server tables.

5. **Cleanup**:
   - The SFTP session and transport are closed cleanly after execution.

## Project Structure

```
gpp-client-main/
├── client/              # SFTP and file engine
│   ├── engine.py        # File filtering, reading, and transformation
│   └── sftp.py          # Secure connection logic
├── config/              # Logging and environment settings
├── database/            # SQL Server DB helpers
├── transformer/         # Custom transformation logic
├── main.py              # Entry point for orchestration
├── .env.sample          # Sample configuration for environment variables
├── Dockerfile           # Container setup
```

## Environment Variables

You must configure a `.env` file based on `.env.sample` with the following variables:

| Variable | Description |
|----------|-------------|
| `SFTP_HOST`, `SFTP_PORT` | SFTP server connection details |
| `SFTP_USER`, `SFTP_PASSWORD` | SFTP credentials |
| `MSSQL_*` | Database connection configuration |
| `OUTPUT_TABLE` | Target table name for inserts |
| `INSERTER_MAX_RETRIES` | Retry limit for DB operations |
| `LOG_LEVEL` | Logging verbosity (e.g., INFO, DEBUG) |

## Docker Support

The application is container-ready for deployment.

### Build Image
```bash
docker build -t gpp-client .
```

### Run Container
```bash
docker run --env-file .env gpp-client
```

## Requirements

Install dependencies via pip:
```bash
pip install -r requirements.txt
```

Key libraries:
- `paramiko`: SFTP communication
- `pandas`: Data loading and shaping
- `SQLAlchemy`, `pyodbc`: MSSQL interfacing
- `fast-to-sql`: Efficient bulk data operations

## Running the App

Ensure `.env` is configured properly, then run:

```bash
python main.py
```

Application logs will confirm:
- Number of new files detected
- Number of rows inserted per table
- Any errors or warnings during transformation

## License

This project is MIT licensed. Usage of the SFTP server and its data is subject to agreements with **GPP Group** and **Titan IS**. Ensure proper authorization before accessing external data.

## Future Enhancements

- Add support for PGP-encrypted reports.
- Implement webhook or schedule triggers.
- Extend transformation rules via configuration or plugins.
- Track ingestion metadata in a separate audit table.
