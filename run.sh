case $1 in
  start_services)
    docker-compose up -d postgres redis elasticsearch nginx
    sleep 3
    JWT_PUBLIC_KEY=$(cat keys/rs256.pub) docker-compose up -d --build search-api
    JWT_PRIVATE_KEY=$(cat keys/rs256.pem) JWT_PUBLIC_KEY=$(cat keys/rs256.pub) docker-compose up -d --build auth-api
    docker-compose up -d --build admin-panel
    docker-compose up -d --build movies-on-demand-api
  ;;
  load_es_index)
    bash -c "curl  -XPUT http://localhost:9200/movies -H 'Content-Type: application/json' -d @es-schemas/es.movies.schema.json \
      && curl  -XPUT http://localhost:9200/persons -H 'Content-Type: application/json' -d @es-schemas/es.persons.schema.json \
      && curl  -XPUT http://localhost:9200/genres -H 'Content-Type: application/json' -d @es-schemas/es.genres.schema.json"
  ;;
  start_etl)
    docker-compose up -d --build postgres-to-es
  ;;

esac