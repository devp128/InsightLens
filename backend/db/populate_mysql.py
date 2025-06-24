import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

connection = pymysql.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)

try:
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_name VARCHAR(255),
                portfolio_value DECIMAL(20,2),
                relationship_manager VARCHAR(255),
                stock VARCHAR(255)
            )
        """)
        cursor.execute("DELETE FROM portfolios")  # Clean slate
        cursor.executemany(
            "INSERT INTO portfolios (client_name, portfolio_value, relationship_manager, stock) VALUES (%s, %s, %s, %s)",
            [
                ("Alice", 10000000.00, "Rajiv Mehra", "HDFC Bank"),
                ("Bob", 8500000.00, "Priya Shah", "Reliance"),
                ("Charlie", 7000000.00, "Rajiv Mehra", "Infosys"),
                ("Diana", 6500000.00, "Priya Shah", "TCS"),
                ("Eve", 6000000.00, "Suresh Iyer", "HDFC Bank"),
                ("Frank", 5000000.00, "Suresh Iyer", "Reliance"),
                ("Grace", 9000000.00, "Rajiv Mehra", "Infosys"),
                ("Heena", 7500000.00, "Priya Shah", "TCS"),
                ("Ivan", 5500000.00, "Suresh Iyer", "HDFC Bank"),
                ("Jaya", 8000000.00, "Rajiv Mehra", "Reliance")
            ]
        )
        connection.commit()
        print("MySQL portfolios table populated!")
finally:
    connection.close()
