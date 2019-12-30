#!/usr/bin/env bash
DEFAULT_DOCKER_NAMESPACE="ci_test"
DOCKER_IMAGE_NAME="project_demo"

local_tag="release"
remote_tag="release_"$(date +%Y%m%d)"_01"
local_namespace="ci_test"
remote_namespace="ci_test"
project_name="project_demo"
local_image="dockerhub.datagrand.com/"${local_namespace}"/"${project_name}":"${local_tag}
remote_image="dockerhub.datagrand.com/"${remote_namespace}"/"${project_name}":"${remote_tag}

cd ..

function build_docker_release() {
  docker build -t ${local_image} -f docker/Dockerfile .
}

function ci_docker_script() {
  build_image ${local_image} docker/Dockerfile .
  push_image ${local_image}
}

function manual_build_docker_release() {
  build_image ${local_image} docker/Dockerfile .
}

function manual_push_docker_release() {
  push_image ${local_image} ${remote_image}
}

function push_docker_release() {
  docker tag ${local_image} ${remote_image}
  docker push ${remote_image}
}