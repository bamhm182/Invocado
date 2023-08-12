#!/usr/bin/env bash

main () {
    setup

    build_extension
}

setup () {
    BASE_DIR=$(dirname $(realpath "$0"))
    BUILD_DIR=${BASE_DIR}/build
    EXT_DIR=${BASE_DIR}/src/extension/

    mkdir -p ${BUILD_DIR}
}

build_extension () {
    rm ${BUILD_DIR}/invocado.jar
    zip -jr ${BUILD_DIR}/invocado.jar ${EXT_DIR}/*
}

main $@
