### Alembic Commands with Examples

offline mode : https://alembic.sqlalchemy.org/en/latest/offline.html


1. **`alembic init <directory>`**
    - **Description**: Initializes a new Alembic environment.
    - **Example**:
      ```bash
      alembic init alembic
      ```
      This command creates an `alembic` directory with the necessary configuration files.

2. **`alembic revision -m "<message>"`**
    - **Description**: Creates a new migration script with a descriptive message.
    - **Example**:
      ```bash
      alembic revision -m "add users table"
      ```
      This command generates a new, empty migration script with the message "add users table".

3. **`alembic revision --autogenerate -m "<message>"`**
    - **Description**: Generates a new migration script based on model changes.
    - **Example**:
      ```bash
      alembic revision --autogenerate -m "create initial tables"
      ```
      This command inspects the models and generates a migration script to create the initial tables.

4. **`alembic upgrade <revision>`**
    - **Description**: Applies the specified revision to the database.
    - **Example**:
      ```bash
      alembic upgrade head
      ```
      This command applies all pending migrations up to the latest revision.

5. **`alembic downgrade <revision>`**
    - **Description**: Reverts the database to the specified revision.
    - **Example**:
      ```bash
      alembic downgrade -1
      ```
      This command reverts the last applied migration.

6. **`alembic current`**
    - **Description**: Displays the current revision applied to the database.
    - **Example**:
      ```bash
      alembic current
      ```
      This command shows the current migration version in the database.

7. **`alembic history`**
    - **Description**: Shows the history of all migrations.
    - **Example**:
      ```bash
      alembic history
      ```
      This command lists all the migration scripts, both applied and unapplied.

8. **`alembic show <revision>`**
    - **Description**: Displays the details of a specific revision.
    - **Example**:
      ```bash
      alembic show abc123
      ```
      This command shows the details of the migration script with revision ID `abc123`.

9. **`alembic heads`**
    - **Description**: Lists all the current heads in the migration script directory.
    - **Example**:
      ```bash
      alembic heads
      ```
      This command lists all the current head revisions.

10. **`alembic branches`**
    - **Description**: Shows all branches in the migration history.
    - **Example**:
      ```bash
      alembic branches
      ```
      This command lists all branches in the migration history.

11. **`alembic merge <revisions>`**
    - **Description**: Merges two or more branches together.
    - **Example**:
      ```bash
      alembic merge -m "merge branches" abc123 def456
      ```
      This command merges the branches with revision IDs `abc123` and `def456`.

12. **`alembic stamp <revision>`**
    - **Description**: Stamps the database with the specified revision without running migrations.
    - **Example**:
      ```bash
      alembic stamp head
      ```
      This command marks the database as up-to-date with the latest revision without applying any migrations.