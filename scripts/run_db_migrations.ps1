param(
    [string]$Revision = "head"
)

& ".\.venv\Scripts\python.exe" -m alembic upgrade $Revision
