#!/usr/bin/env nix-shell
#!nix-shell -i bash -p unzip zip

main () {
    setup

    build_extension
    run_guacamole
}

setup () {
    BASE_DIR=$(dirname $(realpath "$0"))
    BUILD_DIR=${BASE_DIR}/build
    EXT_DIR=${BASE_DIR}/src/extension/

    mkdir -p ${BUILD_DIR}
}

build_extension () {
    rm -r ${BUILD_DIR}/extensions
    mkdir -p ${BUILD_DIR}/extensions
    #zip -jr ${BUILD_DIR}/extensions/invocado.jar ${EXT_DIR}/*
}

run_guacamole () {
    sudo chown ${USERNAME}:${USERNAME} ~/.local/share/containers/storage -R
    mkdir -p ${BUILD_DIR}/db
    podman kill invocado_guacd
    podman kill invocado_guac
    podman kill invocado_db
    podman pod rm invocado
    podman pod create -n invocado -p 8080:8080
    podman run --rm guacamole/guacamole /opt/guacamole/bin/initdb.sh --mysql > ${BUILD_DIR}/db/initdb.sql
    podman run --rm -d --name "invocado_guacd" --pod invocado guacamole/guacd
    podman run --rm -d --name "invocado_db" -e "MYSQL_RANDOM_ROOT_PASSWORD=yes" -e "MYSQL_DATABASE=db" -e "MYSQL_USER=user" -e "MYSQL_PASSWORD=password" -v "${BUILD_DIR}/db/initdb.sql:/initdb.sql:ro" --pod invocado mysql:8.1
    while true; do [[ $(podman exec -it invocado_db mysqladmin ping -h localhost -uuser -ppassword) == *"is alive"* ]] && break || sleep 1; done
    podman exec invocado_db bash -c '/usr/bin/mysql -uuser -ppassword -Ddb < /initdb.sql'
    podman run --rm -e "GUACAMOLE_HOME=/opt/guachome" -e "LOGBACK_LEVEL=debug" -e "GUACD_HOSTNAME=invocado_guacd" -e "MYSQL_SSL_MODE=disabled" -e "MYSQL_HOSTNAME=invocado_db" -e "MYSQL_DATABASE=db" -e "MYSQL_USER=user" -e "MYSQL_PASSWORD=password" -v "${BUILD_DIR}:/opt/guachome:ro" --name "invocado_guac" --pod invocado guacamole/guacamole:latest
    podman kill invocado_guacd
    podman kill invocado_db
    podman pod rm invocado
}

main $@
