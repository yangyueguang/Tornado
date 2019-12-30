#!/usr/bin/env bash

build_image(){
    if [[ $# != 3 ]]; then
        echo "Usage : build_image image_name dockerfile context_path"
        exit 0
    fi
    image_name=$1
    dockerfile=$2
    context_path=$3
    cp -r ~/.ssh .
    docker build -t ${image_name} -f ${dockerfile} ${context_path}
    build_success=$?
    rm -rf .ssh
    if [[ ${build_success} -eq 0 ]]; then
        echo "Build ### ${image_name} ### success!"
    else
        echo "Build ### ${image_name} ### failed!"
        exit 1
    fi
}

push_image(){
    local_image=$1
    if [[ $2 ]];then
	    remote_image=$2
	    docker tag ${local_image} ${remote_image}
        docker push ${remote_image}
    else
        docker push ${local_image}
    fi
}

check_build_success(){
    if [[ $# != 1 ]]; then
        echo "Usage : check_build_success image"
        exit 0
    fi
    image=$1
    if [[ "$(docker images -q ${image} 2> /dev/null)" == "" ]]; then
        echo "Build ### ${image} ### failed"
        exit 1
    else
        echo "Build ### ${image} ### completed"
    fi
}

push_all_branches(){
    docker_image_name=$1
    tag=$2
    default_namespace=$3
    ignore_namespace_list=$4

    namespace_file="idps_global/conf/namespace/$docker_image_name.txt"

    git clone --depth=1 ssh://git@git.datagrand.com:58422/idps/idps_global.git
    if [[ -e ${namespace_file} ]]; then
        cat ${namespace_file} | while read project_namespace; do
            is_ignore=0
            if [[ ignore_name_space_list ]];then
                for ignore_namespace in ${ignore_namespace_list}; do
                    if [[ ${ignore_namespace} == ${project_namespace} ]]; then
                        is_ignore=1
                        echo "ignore namespace: $project_namespace"
                        break
                    fi
                done
            fi
            if [[ ${is_ignore} != 1 ]]; then
                echo "push to namespace: "${project_namespace}
                default_image="dockerhub.datagrand.com/$default_namespace/$docker_image_name:$tag"
                project_image="dockerhub.datagrand.com/$project_namespace/$docker_image_name:$tag"
                push_image ${default_image} ${project_image}
            fi
        done
    else
        echo "Namespace file $namespace_file not exists"
    fi

    rm -rf idps_global
}

push_extra_namespace(){
    docker_image_name=$1
    tag=$2
    extra_namespace_list=$3
    for extra_namespace in ${extra_namespace_list}; do
        extra_image="dockerhub.datagrand.com/$extra_namespace/$docker_image_name:$tag"
        push_image ${image} ${extra_image}
    done
}