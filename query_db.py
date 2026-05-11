#!/usr/bin/env python3
import urllib.parse
from urllib import parse
import pyodbc

server = 'sql-knowledgehub-dev.database.windows.net'
database = 'db-monitoring'
username = 'sqladmin'
password = 'Fontys1234!'

try:
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = ?', 'BASE TABLE')
    print("TABLAS:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    print("\nIntentando instalar ODBC Driver 17...")
    import subprocess
    subprocess.run(['choco', 'install', 'sql-odbc', '-y'], check=False)
