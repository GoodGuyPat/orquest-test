# This file contains common functionality that is shared among many processes.

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import types
from sqlalchemy.pool import NullPool
import dotenv
from datetime import datetime
import pandas as pd
import os

print("utils imported")

env_file = '../dbcredentials.env'
dotenv.load_dotenv(env_file)

host = '0.0.0.0'
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
dbname = os.getenv('POSTGRES_DB')

df_names =  [{'associations':associations_raw},
           {'contracts':contracts_raw},
           {'hours':hours_raw},
           {'incidences':incidences_raw},
           {'measures':measures_raw}
          ]

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

def cast_comma_decimal_as_float(df, column):
    df[column] = df.apply(lambda x: float(x[column].replace(',','.')), axis=1)

def cast_d_m_y_h_m_as_datetime(df, column):
    # df[column] = df.apply(lambda x: datetime.strptime(x[column],'%d/%m/%Y %H:%M'), axis=1)
     df[column] = pd.to_datetime(df[column],format='mixed', dayfirst=True)
def cast_y_m_d_as_datetime(df, column):
    # df[column] = df.apply(lambda x: datetime.strptime(x[column],'%Y-%m-%d'), axis=1)
     df[column] = pd.to_datetime(df[column])
# Schema and data types of our tables
ttypes = {
        'measures':{
           'measure': types.String(),
           'date': types.DateTime(),
           'value': types.Double(),
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
dftypes = {
        'measures':{
           'measure': 'str',
           'date': 'object',
           'value': 'object',
           'store_id': 'int32',
           },
        'hours':{
           'day': 'object',
           'hour': 'int16',
           'person_id': 'int32',
           'worked_hours': 'object',
           },
        'associations':{
           'person_id': 'int32',
           'from_date': 'object',
           'to_date': 'object',
           'store_id': 'int32',
           },
        'contracts':{
           'person_id': 'int32',
           'cost_per_hour': 'object',
           'from_date':'object',
           'to_date': 'object',
           },
        'incidences':{
           'person_id': 'int32',
           'type_name': 'str',
           'from_date': 'object',
           'to_date': 'object',
           }
       }

tcasts = {
    'measures':{
       'date': 'dmy_hm_datetime',
       'value': 'decimal_with_comma'
       },
    'hours':{
       'worked_hours': 'decimal_with_comma',
       'day': 'ymd_datetime'
       },
    'contracts':{
       'cost_per_hour': 'decimal_with_comma'
       },
    'associations':{
       'from_date':'ymd_datetime',
       'to_date':'ymd_datetime'
           }
        }
