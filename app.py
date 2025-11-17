

import streamlit as st
import psycopg2
from datetime import date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection function
def get_connection():
    return psycopg2.connect(
        host="db.qqfglpoopmnjvkdpylla.supabase.co",
        database="postgres",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),  # Securely load from .env
        port="5432",
        sslmode="require"
    )


st.title("StaxBill Implementation Tracker")

# Show Clients
st.header("Clients")
if st.button("Show All Clients"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "Clients";')
    rows = cur.fetchall()
    st.write(rows)
    conn.close()

# Add Client
st.subheader("Add New Client")
name = st.text_input("Client Name")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
go_live_date = st.date_input("Go Live Date")
if st.button("Add Client"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO "Clients" (Name, StartDate, EndDate, GoLiveDate) VALUES (%s, %s, %s, %s)',
                (name, start_date, end_date, go_live_date))
    conn.commit()
    st.success("Client added successfully!")
    conn.close()

# Show Tasks
st.header("Tasks")
client_id = st.number_input("Enter Client ID to view tasks", min_value=1, step=1)
if st.button("Show Tasks for Client"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT TaskID, Name, Status, DueDate FROM "Tasks" WHERE ClientID = %s', (client_id,))
    tasks = cur.fetchall()
    st.write(tasks)
    conn.close()

# Add Task
st.subheader("Add New Task")
task_name = st.text_input("Task Name")
category_id = st.number_input("Category ID", min_value=1, step=1)
assigned_user_id = st.number_input("Assigned User ID", min_value=1, step=1)
status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Overdue"])
due_date = st.date_input("Due Date")
resource_url = st.text_input("Resource URL", "https://docs.example.com")
notes = st.text_area("Notes")
if st.button("Add Task"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO "Tasks" (ClientID, CategoryID, Name, AssignedUserID, Status, DueDate, ResourceURL, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (client_id, category_id, task_name, assigned_user_id, status, due_date, resource_url, notes))
    conn.commit()
    st.success("Task added successfully!")
    conn.close()

# Progress Calculation
st.header("Progress")
if st.button("Show Progress for Client"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM "Tasks" WHERE ClientID = %s', (client_id,))
    total_tasks = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM "Tasks" WHERE ClientID = %s AND Status = %s', (client_id, "Completed"))
    completed_tasks = cur.fetchone()[0]
    progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    st.write(f"Progress: {progress:.2f}%")

    # Overdue tasks
    cur.execute('SELECT TaskID, Name FROM "Tasks" WHERE ClientID = %s AND Status = %s', (client_id, "Overdue"))
    overdue = cur.fetchall()
    st.write("Overdue Tasks:", overdue)
    conn.close()
