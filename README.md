# GPP Client
## Overview
GPP Client is a Python-based data pipeline that connects to GPP SFTP server, retrieves CSV reports, processes the data, and stores it in a Microsoft SQL Server database. The system supports automated data ingestion, transformation, and storage.

## Features
- Connects to an SFTP server to fetch financial reports.
- Filters out previously processed files to avoid duplication.
- Transforms and cleans raw CSV data for structured storage.
- Stores processed data into an MSSQL database.
- Implements logging and retry mechanisms for stability.

## Installation
### Prerequisites
- Python 3.10+
- Microsoft SQL Server
- Docker (optional, for containerized execution)

### Setup
Clone the repository:

```bash
git clone https://github.com/arqs-io/gpp-client.git
cd gpp-client.git
```

Install dependencies:

`pip install -r requirements.txt`

Set up environment variables:

- Copy .env.sample to .env
- Edit .env to include your database and API credentials.

Run the application:
`python main.py`

## Docker Usage

To run the application using Docker:


```bash
docker build -t gpp-client .
docker run --env-file .env gpp-client
```

## Contributing
- Fork the repository.
- Create a feature branch: git checkout -b feature-branch
- Commit changes: git commit -m "Add new feature"
- Push to the branch: git push origin feature-branch
- Open a Pull Request.