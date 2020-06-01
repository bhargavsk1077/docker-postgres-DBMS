docker run --name my-postgres -v /home/samyak/pg_data:/var/lib/postgresql/data "$@" -e POSTGRES_PASSWORD=overdrive -d -p 5432:5432 postgres
