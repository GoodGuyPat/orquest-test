# This file generates the "incidences" fact table from our source data.

import pandas as pd
import os
import dotenv
import sys
from orquest_csv_utils import *

# In this case, the table comes already structured as a fact table. We will assign the correct datatypes to the columns
# and return the data to our relational model.

source_schema = 'orquest_raw'
destination_schema = 'orquest_relational'
dest_table_name = 'fact_incidences'
mydb, engine = connect_db(host, user, password, dbname, source_schema)
mycursor = mydb.cursor()
ensure_schema_exists(destination_schema, mycursor, mydb)
print('Connected to database ...')

# Loading the table as is
source_data = pd.read_sql_table('incidences',con=engine)

# Pushing the dataframe to our relational schema with correct datatypes
source_data.to_sql(name=dest_table_name,schema=destination_schema,con=engine, if_exists='replace', index=False, dtype=ttypes['incidences'])

