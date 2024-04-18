# This file contains common functionality that is shared among many processes.

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import types
from sqlalchemy.pool import NullPool
import dotenv
import os

print("utils imported")

env_file = '../dbcredentials.env'
dotenv.load_dotenv(env_file)

host = '0.0.0.0'
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
dbname = os.getenv('POSTGRES_DB')

def connect_db(host, user, password, dbname, schema):
    mydb = psycopg2.connect(
        database=dbname, 
        host=host, 
        user=user, 
        password=password, 
        port='5432')
    engine = create_engine("postgresql://{user}:{pw}@{host}:5432/{db}"
        .format(host=host, db=dbname, user=user, pw=password),
               poolclass=NullPool ,connect_args={'options': '-csearch_path={}'.format(schema)})
    return mydb, engine

def ensure_schema_exists(schema_name, cursor, mydb):
    cursor.execute(f"""CREATE SCHEMA IF NOT EXISTS {schema_name};""")
    mydb.commit()

# Schema and data types of our tables
ttypes = {
        'measures':{
           'measure': types.String(),
           'date': types.DateTime(),
           'value': types.Integer(),
           'store_id': types.Integer()
           },
        'hours':{
           'day': types.Date(),
           'hour': types.Integer(),
           'person_id': types.Integer(),
           'worked_hours': types.Double()
           },
        'associations':{
           'person_id': types.Integer(),
           'from_date': types.Date(),
           'to_date': types.Date(),
           'store_id': types.Integer()
           },
        'contracts':{
           'person_id': types.Integer(),
           'cost_per_hour': types.Double(),
           'from_date': types.Date(),
           'to_date': types.Date(),
           },
        'incidences':{
           'person_id': types.Integer(),
           'type_name': types.String(),
           'from_date': types.Date(),
           'to_date': types.Date()
           }
       }
