# Data pipelines with Docker, PostgreSQL and Python ETL

## Running the ETL ingest pipeline

Without Docker:

```bash
python ingest_data.py --user=root
    --password=root
    --host=localhost
    --port=5432
    --database=ny_taxi
    --table=yellow_taxi_trans
    --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
```

With Docker:

```bash
docker build -t taxi_ingest:v001 .
docker run -it --network=pg-network taxi_ingest:v001 --user=root --password=root --host=pg-database --port=5432 --database=ny_taxi --table=yellow_taxi_trans --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
```

## Running the dockerized ingest script on the GCP VM instance

```bash
URL="https://github.com/sandman/data-engineering/blob/main/docker_sql/yellow_tripdata_2021-01.csv"
docker run -it \
    --network=docker_sql_dtc_ingest_network \
    taxi_ingest:v001 \
        --user=root \
        --password=root \
        --host=pg-database \
        --port=5432 \
        --database=ny_taxi \
        --table=yellow_taxi_trans \
        --url={URL}
```