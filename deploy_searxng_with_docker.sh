
PORT=8080
docker pull searxng/searxng
docker run --rm \
    -d -p ${PORT}:8080 \
    -v "${PWD}/searxng:/etc/searxng:rw" \
    -e "BASE_URL=http://localhost:$PORT/" \
    -e "INSTANCE_NAME=searxng-instance" \
    searxng/searxng
