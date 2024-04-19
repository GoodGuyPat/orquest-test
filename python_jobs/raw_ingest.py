# The purpose of this script is to ingest the csv data as-is, straight into a database.
import pandas as pd
import os
import sys
from datetime import datetime
from orquest_csv_utils import *

# Read filename to be ingested! We split on the dot to ignore the file extension, if provided.
# If no file is specified, we exit the program.
try:
    filename = sys.argv[1]
    clean_name = filename.split('.')[0]
except:
    sys.exit("Missing filename. Please provide it as a command-line argument!")

# If the file is specified but not found, we also exit.
if filename not in os.listdir():
    sys.exit(f"The file specified ({sys.argv[1]}) was not found.")

# An exec mode can be optionally specified.
try:
    exec_mode = sys.argv[2]
except:
    exec_mode = 'flexible'

if exec_mode != 'strict':
    exec_mode = 'flexible'

def main():

    print(f'Ingesting {filename}, mode = {exec_mode}')

    # Gather relevant datatypes for the processed file
    table_types = ttypes[clean_name]

    # Load data into a DataFrame, connect to database, 
    # ensure that destination schema is present and create it if it is not
    df = pd.read_csv(filename, delimiter=';')
    print('File read ...')
    schema = 'orquest_raw'
    mydb, engine = connect_db(host, user, password, dbname, schema)
    mycursor = mydb.cursor()
    print('Connected to database ...')
    ensure_schema_exists(schema, mycursor, mydb)
    print('Schema ready ...')

    '''
    Write data to our database. exec_mode will determine whether or not
    the datatypes should be enforced on the values. If not, Pandas will
    infer them, and each 'object' dtype will be treated as text
    by our database engine.

    Affected columns must be registered in our configuration file, specifying
    how they must be treated. In our example, we only have decimal numbers using
    commas as delimiter, and datetimes on a non-standard format.
    '''
    if exec_mode == 'strict':
        if clean_name in tcasts.keys():
           for col in df.columns:
               if col in tcasts[clean_name].keys():
                   match tcasts[clean_name][col]:
                       case 'decimal_with_comma':
                           cast_comma_decimal_as_float(df,col)
                       case 'dmy_hm_datetime':
                           cast_d_m_y_h_m_as_datetime(df,col)
        df.to_sql(name=clean_name,schema=schema,con=engine, if_exists='replace', index=False, dtype=table_types)

    else:
        df.to_sql(name=clean_name,schema=schema,con=engine, if_exists='replace', index=False)

    print('Data uploaded to database')

if __name__ == '__main__':
    main()
