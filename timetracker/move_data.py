# copy data from sqlite tables to postgres tables

import sqlite3

import psycopg2
from os import getenv
from dotenv import load_dotenv


tables = ["job_pendings", "idles", "status_txt", "job_posts"]


def copy_to_postgres(table_name: str):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()

    for i in data:
        cursor.execute(f"INSERT INTO {table_name} VALUES{i}")

    conn.commit()
    cursor.close()
    conn.close()


for each in tables:
    copy_to_postgres(each)
