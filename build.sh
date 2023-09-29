#!/bin/bash

REINITIALIZE=false
NOCACHE=false
optspec="nr"
while getopts "$optspec" optchar; do
    case "${optchar}" in
        n) NOCACHE=true;;
        r) REINITIALIZE=true;;
    esac
done

if [[ ! -f initialized.sql || $REINITIALIZE = true ]];
    then
        echo Membuat berkas inisialisasi basis data...
        printf -- '-- TIDAK UNTUK DISUNTING SECARA MANUAL\n-- Naskah ini digenerasi oleh deploy.sh atau deploy.bat.\n-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data.\n\n' > initialized.sql
        cat initialization.sql >> initialized.sql
    else
        echo Basis data TIDAK akan diinisialisasi.
        printf -- '-- TIDAK UNTUK DISUNTING SECARA MANUAL\n-- Basis data telah terinisialisasi.\n-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data dan jalankan naskah build.sh atau build.bat dengan opsi -r untuk menginisialisasi ulang basis data.' > initialized.sql
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

