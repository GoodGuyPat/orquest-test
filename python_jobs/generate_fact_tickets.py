# This file generates the "tickets" fact table from our source data.

import pandas as pd
import os
import dotenv
import sys
from datetime import datetime
from orquest_csv_utils import *

# In this case, the table comes already structured as a fact table. We will assign the correct datatypes to the columns
# and return the data to our relational model.

source_schema = 'orquest_raw'
destination_schema = 'orquest_relational'
dest_table_name = 'fact_tickets'
mydb, engine = connect_db(host, user, password, dbname, source_schema)
mycursor = mydb.cursor()
ensure_schema_exists(destination_schema, mycursor, mydb)
print('Connected to database ...')

# Loading the table as is
source_data = pd.read_sql_table('measures',con=engine)

# Filtering only events of the desired category
dest_data = source_data[source_data["measure"] == 'TICKETS' ]

# date has a non-ISO compliant format that we need to parse for it to be a valid datetime value
dest_data['date'] = dest_data.apply(lambda x: datetime.strptime(x['date'],'%d/%m/%Y %H:%M'), axis=1)

# "value" has a comma as decimal delimiter. We will fix that here.
dest_data['value'] = dest_data.apply(lambda x: float(x['value'].replace(',','.')), axis=1)
# Pushing the dataframe to our relational schema with correct datatypes
dest_data.to_sql(name=dest_table_name,schema=destination_schema,con=engine, if_exists='replace', index=False, dtype=ttypes['measures'])

