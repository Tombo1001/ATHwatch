# ATHwatch
A container to track new All Time High values in crypto curency. Read tracked coins from a postgres instance and record their new ATH values in InfluxDB and Postgres. Watch your crypto moon from the safety of your lambo.
## Configuring the container:
You can configure your Influx Server with the followoing `docker-compose` environment variables:
- `INFLUXDB_IP=<X.X.X.X>`
- `INFLUXDB_PORT=<8086?`
- `INFLUXDB_NAME=<my-db-name>`

And postgres server details with the following `docker-compose` environment variables:
- `PGDB_IP=<X.X.X.X>`
- `PGDB_PORT=<5432>`
- `PGDB_USER=<postgres>`
- `PGDB_PASS=<postgres>`
- `PGDB_NAME=<my-db-name>`

### Postgres schema
Currently you need to know/use my exact PG schema for any of this to work. Here is the SQL code to build a mirror of the table which this code is based on:
```
CREATE TABLE public.ath
(

)
    INHERITS (public.ath)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.ath
    OWNER to postgres;
```
(set owner to your specific Postgres user. Insert this table into the database name configure above in your `docker-compose` file)
## Starting the container:
```
docker-compose build && docker-compose up -d
```