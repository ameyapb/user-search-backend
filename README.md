# user-search-backend > Private search.

## Install:
```
poetry install
```

## Start Server
```bash
poetry run python app.py
```

## Database:

1. Create container
```
docker run --name pg-temp -e POSTGRES_PASSWORD=<custom_password> -p 5432:5432 -d postgres
## Default user is postgres else you can create one by adding -e POSTGRES_USER=myuser
```

2. Log into postgres CLI
```
docker exec -it <container_id> psql -U postgres
```

3. Create Schema
```
poetry run python src/db/run_migration.py
## Use "\dt" in postgres console. You will see tables (if not something went wrong)
```
