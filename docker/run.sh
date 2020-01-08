#!/usr/bin/env bash
image_path="dockerhub.datagrand.com/idps/output_extract:"$(date +%Y%m%d%H)

function hool_to_web() {
  ssh -f -p 58422 xuechao@idps-jumper.datagrand.cn -L 10022:10.0.1.20:22 -L 15107:10.0.1.20:15107 -N
  ssh -f -t -p 58422 xuechao@idps-jumper.datagrand.cn -L 10022:10.0.1.20:22 -L 100.100.21.163:15107:10.0.1.20:15107 -N
}

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
