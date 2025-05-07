# Micro-Loan-Managemnet
This application is dedicated to micro-loan tracking, management and make the system efficient.

Forces Docker to rebuild all images without using any cached layers.
docker-compose build --no-cache && docker-compose up

to connect the DB
docker exec -it postgres-db psql -U postgres -d postgres

without docker connection command
psql -h localhost -U postgres -d postgres

all table list in db 
\dt

detailed list of a table
\dt+

