#!/bin/bash
optspec="in"
while getopts "$optspec" optchar; do
    case "${optchar}" in
        i) INITIALIZE=1;;
        n) NOCACHE=1;;
    esac
done

docker-compose -f docker-compose.yml down -v || {
    exit 0
}

INIT_STATUS=$(cat init_status.txt)
if [[ -n "$INITIALIZE" ]] || [[ "$INIT_STATUS" == 'Basis data belum terinisialisasi.' ]]; then
    docker volume rm mysql_data
    docker volume create mysql_data
    echo Basis data belum terinisialisasi. > init_status.txt
fi

if [ -n "$NOCACHE" ];
    then
        docker-compose build --no-cache
    else
        docker-compose build
fi
