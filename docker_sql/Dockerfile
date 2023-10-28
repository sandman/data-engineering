FROM python:3.9.18

RUN apt-get install wget
RUN pip install --upgrade pip
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY ingest_data.py ingest_data.py
COPY yellow_tripdata_2021-01.csv yellow_tripdata_2021-01.csv
COPY taxi+_zone_lookup.csv taxi+_zone_lookup.csv

ENTRYPOINT [ "python", "ingest_data.py" ]