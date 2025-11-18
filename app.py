from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import psycopg2
from datetime import date

app = FastAPI()

# Database connection
def get_connection():
    return psycopg2.connect(
        host="aws-1-us-east-1.pooler.supabase.com",
        database="postgres",
        user="postgres.qqfglpoopmnjvkdpylla",
        password="YZHEXV5HFJMOAKpM",
        port="5432",
        sslmode="require"
    )

# ✅ Endpoint: Show all clients
@app.get("/clients")
async def get_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "Clients";')
    rows = cur.fetchall()
    conn.close()
    return {"clients": rows}

# ✅ Endpoint: Add new client
@app.post("/clients")
async def add_client(name: str, start_date: date, end_date: date, go_live_date: date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO "Clients" (Name, StartDate, EndDate, GoLiveDate) VALUES (%s, %s, %s, %s)',
                (name, start_date, end_date, go_live_date))
    conn.commit()
    conn.close()
    return {"message": "Client added successfully!"}

# ✅ Endpoint: Show tasks for a client
@app.get("/tasks/{client_id}")
async def get_tasks(client_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT TaskID, Name, Status, DueDate FROM "Tasks" WHERE ClientID = %s', (client_id,))
    tasks = cur.fetchall()
    conn.close()
    return {"tasks": tasks}

# ✅ Endpoint: Add new task
@app.post("/tasks")
async def add_task(client_id: int, category_id: int, task_name: str, assigned_user_id: int,
                   status: str, due_date: date, resource_url: str, notes: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO "Tasks" (ClientID, CategoryID, Name, AssignedUserID, Status, DueDate, ResourceURL, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (client_id, category_id, task_name, assigned_user_id, status, due_date, resource_url, notes))
    conn.commit()
    conn.close()
    return {"message": "Task added successfully!"}

# ✅ Endpoint: Show progress for a client
@app.get("/progress/{client_id}")
async def get_progress(client_id: int):
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

    return {"progress": f"{progress:.2f}%", "overdue_tasks": overdue}
