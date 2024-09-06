from sqlalchemy import create_engine, MetaData, text, Integer, String
from sqlalchemy.schema import Column, Table
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI
from pydantic import BaseModel
import os

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DATABASE_HOST"]
db_port = os.environ["DATABASE_PORT"]
db_database = os.environ["DB_DATABASE"]


conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"

db_engine = create_engine(conn_string)

metadata = MetaData()

class TableSchema(BaseModel):
    table_name: str
    columns: dict

@app.get("/tables")
async def get_tables():
    with db_engine.connect() as connection:
        results = connection.execute(text("select tablename from pg_catalog.pg_tables where schemaname='public';"))
        dict_res = {}
        res = results.fetchall()
        dict_res['database'] = [str(result[0]) for result in res]
        return dict_res

@app.put("/table")
async def create_table(schema: TableSchema):
    columns = [Column(col_name, eval(col_type)) for col_name, col_type in schema.columns.items()]
    table = Table(schema.table_name, metadata, *columns)
    try:
        metadata.create_all(db_engine, tables=[table], checkfirst=False)
        return f"{schema.table_name} successfully created"
    except SQLAlchemyError as e:
        return dict({"error_msg": str(e)})
