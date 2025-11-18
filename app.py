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

def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set in environment variables.")
    try:
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
