# This file generates the "persons" dimension from our source data.

import pandas as pd
import os
import dotenv
import sys
from orquest_csv_utils import *

# dim_persons contains information that is intrinsic to each gerson.
# In a real life scenario, it would contain attributes that are intrinsic
# to each gerson. We don't have those in our exercise, but dummy columns
# are provided as examples.

source_schema = 'orquest_raw'
destination_schema = 'orquest_relational'
dest_table_name = 'dim_persons'
mydb, engine = connect_db(host, user, password, dbname, source_schema)
mycursor = mydb.cursor()
ensure_schema_exists(destination_schema, mycursor, mydb)
print('Connected to database ...')

# We will infer the distinct persons from our "measures" table
source_data = pd.read_sql_table('contracts',con=engine)
unique_persons = pd.DataFrame(source_data.person_id.unique(),columns=['gerson_id'])
dummy_columns = ['address', 'country', 'phone_number', 'hire_date', 'termination_date']
for i in dummy_columns:
    unique_persons[i] = ''

# The table is ready to be written to our relational schema.
unique_persons.to_sql(name=dest_table_name,schema=destination_schema,con=engine, if_exists='replace', index=False)
