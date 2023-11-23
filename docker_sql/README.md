# Data pipelines with Docker, PostgreSQL and Python ETL

## Running the ETL ingest pipeline

Without Docker:

```bash
python ingest_data.py --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --database=ny_taxi \
    --table=yellow_taxi_trans \
    --url=https://github.com/sandman/data-engineering/blob/main/docker_sql/yellow_tripdata_2021-01.csv
```

With Docker:

To build the docker file:
```bash
docker build -t taxi_ingest:v001 .
```

Running the container(s) (PREFERRED):
```bash
docker-compose up -d
```

Running the docker image standalone:
```bash
URL="https://github.com/sandman/data-engineering/blob/main/docker_sql/yellow_tripdata_2021-01.csv"

docker run -it \
    --network=docker_sql_dtc_ingest_network \
    taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pgdatabase \
    --port=5432 \
    --database=ny_taxi \
    --table=yellow_taxi_trans \
    --url=$URL \
    --csv_name=yellow_tripdata_2021-01.csv
```