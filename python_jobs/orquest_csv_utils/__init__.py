# This file contains common functionality that is shared among many processes.

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import types
from sqlalchemy.pool import NullPool

print("utils imported")

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
        'associations':{'person_id': types.Integer(),
               'from_date': types.Date(),
               'to_date': types.Date(),
               'store_id': types.Integer()
               }
           }
