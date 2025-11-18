import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from urllib.parse import urlparse
from datetime import date

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your React app URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Parse DATABASE_URL for psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set in environment variables.")
    result = urlparse(DATABASE_URL)
    return psycopg2.connect(
        host=result.hostname,
        database=result.path[1:],  # remove leading '/'
        user=result.username,
        password=result.password,
        port=result.port,
        sslmode="require"
    )

    except Exception as e:
        raise Exception(f"Database connection error: {e}")

@app.get("/")
async def root():
    return {"message": "FastAPI backend is running!"}

# ✅ Get all clients
@app.get("/clients")
async def get_clients():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT ClientID, Name, StartDate, EndDate, GoLiveDate FROM "Clients";')
        rows = cur.fetchall()
        conn.close()
        clients = [
            {"ClientID": r[0], "Name": r[1], "StartDate": str(r[2]), "EndDate": str(r[3]), "GoLiveDate": str(r[4])}
            for r in rows
        ]
        return {"clients": clients}
    except Exception as e:
        return {"error": str(e)}

# ✅ Add a new client
@app.post("/clients")
async def add_client(name: str, start_date: date, end_date: date, go_live_date: date):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO "Clients" (Name, StartDate, EndDate, GoLiveDate) VALUES (%s, %s, %s, %s)',
                    (name, start_date, end_date, go_live_date))
        conn.commit()
        conn.close()
        return {"message": "Client added successfully!"}
    except Exception as e:
        return {"error": str(e)}

# ✅ Get tasks for a client
@app.get("/tasks/{client_id}")
async def get_tasks(client_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT TaskID, Name, Status, DueDate FROM "Tasks" WHERE ClientID = %s', (client_id,))
        rows = cur.fetchall()
        conn.close()
        tasks = [
            {"TaskID": r[0], "Name": r[1], "Status": r[2], "DueDate": str(r[3])}
            for r in rows
        ]
        return {"tasks": tasks}
    except Exception as e:
        return {"error": str(e)}

# ✅ Add a new task
@app.post("/tasks")
async def add_task(client_id: int, category_id: int, task_name: str, assigned_user_id: int,
                   status: str, due_date: date, resource_url: str, notes: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO "Tasks" (ClientID, CategoryID, Name, AssignedUserID, Status, DueDate, ResourceURL, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (client_id, category_id, task_name, assigned_user_id, status, due_date, resource_url, notes))
        conn.commit()
        conn.close()
        return {"message": "Task added successfully!"}
    except Exception as e:
        return {"error": str(e)}

# ✅ Get progress for a client
@app.get("/progress/{client_id}")
async def get_progress(client_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "Tasks" WHERE ClientID = %s', (client_id,))
        total_tasks = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM "Tasks" WHERE ClientID = %s AND Status = %s', (client_id, "Completed"))
        completed_tasks = cur.fetchone()[0]
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        cur.execute('SELECT TaskID, Name FROM "Tasks" WHERE ClientID = %s AND Status = %s', (client_id, "Overdue"))
        overdue = cur.fetchall()
        conn.close()

        overdue_tasks = [{"TaskID": r[0], "Name": r[1]} for r in overdue]
        return {"progress": f"{progress:.2f}%", "overdue_tasks": overdue_tasks}
    except Exception as e:
        return {"error": str(e)}
