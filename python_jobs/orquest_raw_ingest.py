# The purpose of this script is to ingest the csv data as-is, straight into a database.
import pandas as pd
import os
import dotenv
import sys
# Read our table schemas
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
    env_file = '/code/dbcredentials.env'
    env_file = '../dbcredentials.env'
    dotenv.load_dotenv(env_file)

    host = '0.0.0.0'
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    dbname = os.getenv('POSTGRES_DB')
    schema = 'orquest_raw'

    table_types = ttypes[clean_name]

    df = pd.read_csv(filename, delimiter=';')
    print('File read ...')
    mydb, engine = connect_db(host, user, password, dbname, schema)
    mycursor = mydb.cursor()
    print('Connected to database ...')
    ensure_schema_exists(schema, mycursor, mydb)
    print('Schema ready ...')
    if exec_mode == 'strict':
        df.to_sql(name=filename,schema=schema,con=engine, if_exists='replace', index=False, dtype=table_types)
    else:
        df.to_sql(name=filename,schema=schema,con=engine, if_exists='replace', index=False)
    print('Data uploaded to database')

if __name__ == '__main__':
    main()
