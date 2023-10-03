#!/bin/bash
# Replace variables in the sql initialization script
/replace.sh $1 $2

# # Wait until the password for the telebot user is added into the initialization script
# STR=`cat $2 | grep 'CREATE USER\|ALTER USER'`
# SUB='__TELEBOT_PASSWORD__'
#
# while [[ "$STR" == *"$SUB"* ]]; do
#     echo Menunggu password user sql bot telegram...
#     sleep 5
#     STR=`cat $1 | grep 'CREATE USER'`
# done
#
# NEW_ROOT_PASSWORD=$(openssl rand -base64 32)
#
# SUB=$(awk '{ sub(/.*BY /, ""); sub(/;.*/, ""); print }' <<< "$STR")
# echo ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$NEW_ROOT_PASSWORD'; >> $2
#
echo KATA SANDI ROOT: `cat $MYSQL_ROOT_PASSWORD_FILE`
echo KATA SANDI BOT TELEGRAM: `cat $MYSQL_PASSWORD_FILE`

# Run mysql docker container's original entrypoint
/usr/local/bin/docker-entrypoint.sh --bind-address=0.0.0.0 --default-authentication-plugin=mysql_native_password
# printf -- '-- TIDAK UNTUK DISUNTING SECARA MANUAL\n-- Basis data telah terinisialisasi.\n-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data dan jalankan naskah build.sh atau build.bat dengan opsi -r untuk menginisialisasi ulang basis data.' > $1
# echo Inisialisasi selesai.

