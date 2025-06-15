### instruction

We create a docker compose file that launches a Postgresql database.
Since the docker compose file lies inside the directory 2_data_modelling, nake sure to implement the path accordingly to make it run correctly. 

In order too start the docker:
```
docker compose down -v && docker compose up -d
```

In order to open the database:
```
docker compose exec -it db psql -U user -d trustpilot
```

Then you can run SQL queries to check the data.
