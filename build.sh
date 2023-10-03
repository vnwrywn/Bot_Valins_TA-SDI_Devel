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

# if [[ ! -f initialized.sql || $REINITIALIZE = true ]];
#     then
#         echo Membuat berkas inisialisasi basis data...
#         printf -- '-- TIDAK UNTUK DISUNTING SECARA MANUAL\n-- Naskah ini digenerasi oleh deploy.sh atau deploy.bat.\n-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data.\n\n' > initialized.sql
#         cat initialization.sql >> initialized.sql
#         echo Berkas inisialisasi basis data berhasil dibuat.
#     else
#         echo Basis data TIDAK akan diinisialisasi.
#         printf -- '-- TIDAK UNTUK DISUNTING SECARA MANUAL\n-- Basis data telah terinisialisasi.\n-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data dan jalankan naskah build.sh atau build.bat dengan opsi -r untuk menginisialisasi ulang basis data.\nALTER USER `__TELEBOT_USER__`@`%` IDENTIFIED WITH mysql_native_password BY '__TELEBOT_PASSWORD__';' > initialized.sql
# fi
#
# chmod 766 initialized.sql

if [[ $SKIP = false ]]; then
    docker volume create mysql_data
    docker swarm init
    docker network create --driver overlay bot_telegram_devel
    openssl rand -base64 32 | sudo docker secret create db_root_password -
    openssl rand -base64 32 | sudo docker secret create db_telebot_password -
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

