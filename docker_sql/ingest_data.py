import pandas as pd
from sqlalchemy import create_engine
from time import time
import argparse
import os
import psycopg2


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    database = params.database
    table = params.table
    url = params.url
    csv_name = params.csv_name  # "yellow_tripdata_2021-01.csv"

    file_path = os.path.join(os.getcwd(), csv_name)

    # Download the CSV file if it doesn't exist
    if not os.path.exists(file_path):
        print(f'Downloading {csv_name} from {url}')
        os.system(f"wget {url} -O {csv_name}")
    else:
        print(f'File {csv_name} exists.')

    df = pd.read_csv(file_path, nrows=100)

    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{database}"
    )

    chunk_size = 50000
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=chunk_size)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table, con=engine, if_exists="replace")

    while True:
        try:
            t_start = time()

            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name=table, con=engine, if_exists="append")

            t_end = time()

            print(
                "inserted another chunk, took %.3f second" % (t_end - t_start)
            )
        except StopIteration:
            break

    df_zones = pd.read_csv("taxi+_zone_lookup.csv")

    df_zones.head()

    df_zones.to_sql(name="zones", con=engine, if_exists="replace")


if __name__ == "__main__":
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
    main(args)
