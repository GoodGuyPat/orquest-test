# This file generates the "stores" dimension from our source data.

import pandas as pd
import os
import dotenv
import sys
from orquest_csv_utils import *

# dim_stores contains information that is intrinsic to each store.
# In a real life scenario, it would contain attributes that are intrinsic
# to each store. We don't have those in our exercise, but dummy columns
# are provided as examples.

source_schema = 'orquest_raw'
destination_schema = 'orquest_relational'
dest_table_name = 'dim_stores'
mydb, engine = connect_db(host, user, password, dbname, source_schema)
mycursor = mydb.cursor()
ensure_schema_exists(destination_schema, mycursor, mydb)
print('Connected to database ...')

# We will infer the distinct stores from our "measures" table
source_data = pd.read_sql_table('measures',con=engine)
unique_stores = pd.DataFrame(source_data.store_id.unique(),columns=['store_id'])
dummy_columns = ['address', 'country', 'store_location_type']
for i in dummy_columns:
    unique_stores[i] = ''

# The table is ready to be written to our relational schema.
unique_stores.to_sql(name=dest_table_name,schema=destination_schema,con=engine, if_exists='replace', index=False)
