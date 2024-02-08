# copy data from sqlite tables to postgres tables

import sqlite3

import psycopg2


tables = ["job_pendings", "idles", "status_txt", "job_posts"]



def copy_to_postgres(table_name: str):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()


    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="Tp\ZS?gfLr|]'a",
        port=5432,
    )
    cursor = conn.cursor()

    for i in data:
        cursor.execute(f"INSERT INTO {table_name} VALUES{i}")
    
    conn.commit()
    cursor.close()
    conn.close()


for each in tables:
    copy_to_postgres(each)