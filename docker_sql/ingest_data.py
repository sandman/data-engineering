import pandas as pd
from sqlalchemy import create_engine
from time import time
import argparse
import os
import psycopg2
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_data(url, csv_name):
    file_path = os.path.join(os.getcwd(), csv_name)

    # Download the CSV file if it doesn't exist
    if not os.path.exists(file_path):
        print(f'Downloading {csv_name} from {url}')
        os.system(f"wget {url} -O {csv_name}")
    else:
        print(f'File {csv_name} exists.')

    df = pd.read_csv(file_path, nrows=100)

    chunk_size = 50000
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=chunk_size)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    return df


@task(log_prints=True)
def transform_data(df):
    print(f"pre:Missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(f"post:Missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df

@task(log_prints=True, retries=3)
def ingest_data(table, df):
    database_block = SqlAlchemyConnector.load("sqlalchemy-postgres")
    with database_block.get_connection(begin=False) as engine:
        df.head(n=0).to_sql(name=table, con=engine, if_exists="replace")
        df.to_sql(name=table, con=engine, if_exists="append")

@flow(name="Subflow", log_prints=True)
def log_subflow(table_name: str):
    print(f'Logging subflow for {table_name}')

@flow(name="Ingest Flow")
def main_flow():
    parser = argparse.ArgumentParser(
        description="Ingest CSV file into PostgreSQL database using Pandas"
    )
    # make these arguments mandatory
    parser.add_argument(
        "--user", type=str, help="Username for database", required=True
    )
    parser.add_argument(
        "--password", type=str, help="Password for database", required=True
    )
    parser.add_argument(
        "--host",
        type=str,
        help="Host for database. Default: localhost",
        default="localhost",
        required=True,
    )
    parser.add_argument(
        "--port",
        type=str,
        help="Port for database",
        default=5432,
        required=True,
    )
    parser.add_argument(
        "--database", type=str, help="Database name", required=True
    )
    parser.add_argument(
        "--table", type=str, help="DB Table name", required=True
    )
    parser.add_argument(
        "--url",
        type=str,
        help="URL for CSV file. Only add if the CSV file is not present locally.",  # noqa
        required=False,
    )
    parser.add_argument(
        "--csv_name",
        type=str,
        help="CSV file name to ingest. This should be in the same working \
            directory where the ingest script is run from.",
        required=True,
    )

    args = parser.parse_args()

    log_subflow(args.table)
    raw_data = extract_data(url=args.url, csv_name=args.csv_name)

    data = transform_data(raw_data)

    ingest_data(args.table, data)

if __name__ == "__main__":
    main_flow()
