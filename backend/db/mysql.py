from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = getenv('MYSQL_PORT', '3306')
MYSQL_USER = getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = getenv('MYSQL_PASSWORD', '')
MYSQL_DB = getenv('MYSQL_DB', 'wealth')

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Example usage:
# with SessionLocal() as session:
#     result = session.execute("SELECT * FROM transactions LIMIT 1")
#     print(result.fetchall())
