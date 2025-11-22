# Getting Started

## Prerequisites

- Docker and Docker Compose installed
- Python 3.x
- pip

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Docker Container

Start the PostgreSQL database container with pgvector extension:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port `5434`
- Adminer (database management UI) on port `8081`

Database credentials:
- Host: `localhost`
- Port: `5434`
- User: `postgres`
- Password: `aicooStudent`
- Database: `app`

### 3. Load Database Dump

If you have an existing database dump, load it with:

```bash
docker cp ./db_backup.dump aicoo-project-multiagent-generate-issue-resolution-options-adminerstudent-1:/tmp/db_backup.dump
docker exec aicoo-project-multiagent-generate-issue-resolution-options-adminerstudent-1 psql -U postgres -c "DROP DATABASE IF EXISTS app;"
docker exec aicoo-project-multiagent-generate-issue-resolution-options-adminerstudent-1 psql -U postgres -c "CREATE DATABASE app;"
docker exec aicoo-project-multiagent-generate-issue-resolution-options-adminerstudent-1 pg_restore -U postgres -d app -v /tmp/db_backup.dump
```

### 4. Run Database Migrations

If starting fresh or after loading a dump, run Alembic migrations:

```bash
alembic upgrade head
```

## Adding New Models and Creating Alembic Migrations

### Step 1: Create Your Model

Add your new model to the appropriate file in the `models/` directory. For example, in `models/projectplan.py`:

```python
class YourNewModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    # ... other fields
```

### Step 2: Import the Model

Make sure your new model is imported in `models/main.py`:

```python
from models.projectplan import Project, Task, Mail, YourNewModel
```

This ensures Alembic can detect your model when generating migrations.

### Step 3: Generate Migration

Create a new Alembic migration:

```bash
alembic revision --autogenerate -m "description of your changes"
```

This will create a new migration file in `alembic/versions/` with a name like `xxxxx_description_of_your_changes.py`.

### Step 4: Review the Migration

Always review the generated migration file to ensure it's correct. The migration will have:
- `upgrade()` function: applies the changes
- `downgrade()` function: reverts the changes

### Step 5: Apply the Migration

Apply the migration to your database:

```bash
alembic upgrade head
```

To revert the last migration:

```bash
alembic downgrade -1
```

## Database Backup and Restore

### Save Dump

```bash
docker exec students-db18student-1 pg_dump -U postgres -d app -F c -f /tmp/db_backup.dump
docker cp students-db18student-1:/tmp/db_backup.dump ./db_backup.dump
```

### Load Dump

```bash
docker cp ./db_backup.dump students-db18student-1:/tmp/db_backup.dump
docker exec students-db18student-1 psql -U postgres -c "DROP DATABASE IF EXISTS app;"
docker exec students-db18student-1 psql -U postgres -c "CREATE DATABASE app;"
docker exec students-db18student-1 pg_restore -U postgres -d app -v /tmp/db_backup.dump
```
