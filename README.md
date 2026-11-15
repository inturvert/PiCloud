# PiCloud

A self-hosted cloud storage prototype built using **FastAPI, PostgreSQL, and React**.

PiCloud Phase 1 provides a basic web interface to view and download files stored on a local server. Files can be manually copied into the storage directory and discovered using the storage scanner.

## 1. System Requirements and Prerequisites

The following software must be installed before setting up PiCloud.

### Required Software

| Software | Purpose |
|---|---|
| Debian / Ubuntu Linux | Operating system |
| Git | Source code management and repository cloning |
| Python 3 | Backend development |
| Python venv | Python virtual environment |
| pip | Python package management |
| PostgreSQL | Relational database |
| Node.js | Frontend runtime |
| npm | Frontend package management |

### Backend Dependencies

Installed automatically using `requirements.txt`:

- FastAPI
- Uvicorn
- SQLAlchemy
- psycopg2-binary
- python-multipart
- python-dotenv
- Alembic
- argon2-cffi

### Frontend Dependencies

Installed automatically using `package.json`:

- React
- React DOM
- Vite
- Tailwind CSS
- Lucide React

### Install System Prerequisites (Debian / Ubuntu)

```bash
sudo apt update

sudo apt install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nodejs \
    npm
```

### Verify Installation

```bash
git --version
python3 --version
pip3 --version
psql --version
node --version
npm --version
```

**Note:** Python and Node.js package dependencies are installed separately during the backend and frontend setup processes.

## 2. Clone the Repository

```bash
git clone https://github.com/inturvert/PiCloud.git
cd PiCloud
```


## 3. Backend Setup

### Create a Python virtual environment

```bash
cd backend

python3 -m venv venv
source venv/bin/activate
```

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create your environment configuration file:

```bash
cp .env.example .env
nano .env
```

Update the database credentials and storage path:

```env
APP_NAME=PiCloud
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+psycopg2://picloud_user:YOUR_PASSWORD@127.0.0.1:5432/picloud_db

STORAGE_PATH=/absolute/path/to/PiCloud/storage
MAX_UPLOAD_SIZE=104857600
```

Replace `YOUR_PASSWORD` and `/absolute/path/to/PiCloud` with your actual values.


## 4. PostgreSQL Setup

Make sure PostgreSQL is installed and running.

Create the application database and user:

```bash
sudo -u postgres psql
```

Execute the following SQL commands:

```sql
CREATE USER picloud_user WITH PASSWORD 'YOUR_PASSWORD';

CREATE DATABASE picloud_db OWNER picloud_user;

\q
```

Use the same password in your `.env` file.

### Run database migrations

From the `backend` directory, with the virtual environment activated:

```bash
alembic upgrade head
```

This creates the required database tables using the project's Alembic migrations.

## 5. Initialize Storage Directories

From the project root:

```bash
mkdir -p storage/objects storage/temp
```

These directories are used for storing files and temporary uploads.

## 6. Start the Backend Server

Open a terminal:

```bash
cd PiCloud/backend
source venv/bin/activate

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at:

- API: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

## 7. Start the Frontend

Open another terminal:

```bash
cd PiCloud/frontend
npm install
npm run dev
```

Open the frontend in your browser:

**http://localhost:5173**

The frontend communicates with the backend through the Vite development proxy.

## 8. Adding Files to PiCloud

Currently, files are manually added to the storage directory.

Copy your files into:

```text
PiCloud/storage/objects/
```

Open the PiCloud web interface and use the **Refresh Storage** button.

The storage scanner discovers files that have been manually added and registers their metadata in PostgreSQL.

The discovered files will then appear in the dashboard, where they can be downloaded.

## 9. Accessing PiCloud from Another Device

To access the dashboard from another device on the same Wi-Fi network:

1. Find the IP address of the machine running PiCloud:

   ```bash
   hostname -I
   ```

2. Start the frontend with LAN access enabled:

   ```bash
   npm run dev -- --host 0.0.0.0
   ```

3. Open the following address on the other device:

   ```text
   http://YOUR_SERVER_IP:5173
   ```

Replace `YOUR_SERVER_IP` with the server machine's local IP address.

## 10. Current Project Limitations

PiCloud is currently an early-stage development prototype.

- No user authentication or account management.
- No HTTPS configuration.
- No public internet deployment.
- Files must currently be added manually to the storage directory.
- File discovery requires manually triggering the storage scanner.
- No automatic reconciliation of modified or deleted files.

**Security notice:** This development version is intended for testing on a trusted local network. Do not expose it directly to the public internet or configure router port forwarding.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database migrations | Alembic |
| Frontend | React, Vite |
| Styling | Tailwind CSS |
| API communication | REST API |

---

**PiCloud – Phase 1: Basic Self-Hosted File Storage Prototype**
