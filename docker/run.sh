#!/usr/bin/env bash
image_path="yangyueguang/tornado:"$(date +%Y%m%d%H)

function build_docker() {
  docker build -t ${image_path} -f Dockerfile . --no-cache
}

function run_docker() {
  docker run -d --env EXTRACT_HOST=100.100.21.163 --env EXTRACT_PORT=15107 -v ~/Desktop/tornado/app/static:/app/static -p 8000:8000  --restart=always --name=output_extract $image_path
}
function clear_docker() {
    docker container prune -f
}
function push_docker() {
  docker push ${image_path}
}
