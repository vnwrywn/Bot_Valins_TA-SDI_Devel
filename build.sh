#!/bin/bash
SKIP=false
NOCACHE=false
optspec="ns"
while getopts "$optspec" optchar; do
    case "${optchar}" in
        n) NOCACHE=true;;
        s) SKIP=true;;
    esac
done

if [[ $SKIP = false ]]; then
    docker volume create mysql_data
    docker swarm init
    docker network create --driver overlay bot_telegram_devel
    openssl rand -base64 24 | sudo docker secret create db_root_password -
    openssl rand -base64 24 | sudo docker secret create db_telebot_password -
fi

docker-compose -f docker-compose.yml down -v || {
    echo Mohon jalankan script ini sebagai root.
    exit 0
}
if [ $NOCACHE = true ];
    then
        docker-compose build --no-cache
    else
        docker-compose build
fi
