from backend import *

print(f"Connecting to IRIS at {CONNECTION_STRING}")
with iris.connect(CONNECTION_STRING, USERNAME, PASSWORD) as conn:
    print("Connected to IRIS")
    sql_cursor = conn.cursor()
    delete_table(sql_cursor, TABLE_NAME)