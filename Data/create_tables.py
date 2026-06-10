import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="BankDB", user="postgres", password="postgres"
)

cur = conn.cursor()

with open("./create_tables.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

cur.execute(sql_script)

conn.commit()

cur.close()
conn.close()

print("SQL script executed successfully.")
