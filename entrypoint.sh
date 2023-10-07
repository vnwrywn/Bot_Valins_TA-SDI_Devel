#!/bin/bash
set -eo pipefail

source "/usr/local/bin/docker-entrypoint.sh"

mysql_note "Custom entrypoint script for MySQL Server ${MYSQL_VERSION} started."

mysql_check_config "$@"
# Load various environment variables
docker_setup_env "$@"
docker_create_db_directories "$@"

# # If container is started as root user, restart as dedicated mysql user
# if [ "$(id -u)" = "0" ]; then
#     mysql_note "Switching to dedicated user 'mysql'"
#     exec gosu mysql "$BASH_SOURCE" "$@"
# fi

# if [[ "$STR" == 'Basis data sudah terinisialisasi.' ]]; then
#     MAX_RETRIES=60 # Maximum number of retries
#     SLEEP_INTERVAL=5 # Sleep interval in seconds between retries
#     retry_count=0 # Counter to keep track of the number of retries
#
#     echo "Basis data telah terinisialiasi."
#     /usr/local/bin/docker-entrypoint.sh --bind-address=0.0.0.0 --default-authentication-plugin=mysql_native_password &
#
#     until mysql -h localhost -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "SELECT 1;" &> /dev/null; do
#         ((retry_count++))
#         echo "MySQL is unavailable. Retrying (Attempt $retry_count/$MAX_RETRIES)..."
#
#         if [ $retry_count -ge $MAX_RETRIES ]; then
#             echo "Max retries reached. MySQL server is still unavailable. Exiting."
#             exit 1
#         fi
#
#         sleep $SLEEP_INTERVAL
#     done
#
#     echo "MySQL is ready. Continuing with your script..."
#     mysql -h localhost -u "$TELEBOT_USER" -p"$TELEBOT_PASSWORD" -e "YOUR_CUSTOM_MYSQL_COMMAND_HERE"
#
# elif [[ "$STR" == 'Basis data belum terinisialisasi.' ]]; then
#     # Replace variables in the sql initialization script
#     /replace.sh /tmp/init.sql /docker-entrypoint-initdb.d/init.sql
#
#     # Wait until the password for the telebot user is added into the initialization script
#     STR=`cat /docker-entrypoint-initdb.d/init.sql | grep 'CREATE USER'`
#     SUB='__TELEBOT_PASSWORD__'
#
#     while [[ "$STR" == *"$SUB"* ]]; do
#         echo Menunggu password user sql bot telegram...
#         sleep 5
#         STR=`cat /tmp/init.sql | grep 'CREATE USER'`
#     done
#
#     SUB=$(awk '{ sub(/.*BY /, ""); sub(/;.*/, ""); print }' <<< "$STR")
#     echo PASSWORD BOT TELEGRAM: $SUB | tr -d "'"
#
#     echo Basis data sudah terinisialisasi. > init_status.txt
#     # Run mysql docker container's original entrypoint
#     /usr/local/bin/docker-entrypoint.sh --bind-address=0.0.0.0 --default-authentication-plugin=mysql_native_password

STR=$(cat /init_status.txt)
if [[ "$STR" == 'Basis data belum terinisialisasi.' ]]; then
    # there's no database, so it needs to be initialized
    docker_verify_minimum_env

    # Replace variables in the sql initialization script
    /replace.sh /tmp/init.sql /docker-entrypoint-initdb.d/init.sql

    # Wait until the password for the telebot user is added into the initialization script
    STR=`cat /docker-entrypoint-initdb.d/init.sql | grep 'CREATE USER'`
    SUB='__TELEBOT_PASSWORD__'

    while [[ "$STR" == *"$SUB"* ]]; do
        echo Menunggu password user sql bot telegram...
        sleep 5
        STR=`cat /docker-entrypoint-initdb.d/init.sql | grep 'CREATE USER'`
    done

    SUB=$(awk '{ sub(/.*BY /, ""); sub(/;.*/, ""); print }' <<< "$STR")
    mysql_note "PASSWORD BOT TELEGRAM: $SUB"

    # check dir permissions to reduce likelihood of half-initialized database
    ls /docker-entrypoint-initdb.d/ > /dev/null

    docker_init_database_dir "$@"

    mysql_note "Starting temporary server"
    docker_temp_server_start "$@"
    mysql_note "Temporary server started."

    docker_setup_db
    docker_process_init_files /docker-entrypoint-initdb.d/*

    mysql_expire_root_user

    mysql_note "Stopping temporary server"
    docker_temp_server_stop
    mysql_note "Temporary server stopped"

    echo Basis data sudah terinisialisasi. > init_status.txt
    echo > /docker-entrypoint-initdb.d/*
    printf '[client]\n' > /root/.my.cnf
    echo password = $MYSQL_ROOT_PASSWORD >> /root/.my.cnf
    chmod 600 /root/.my.cnf
    echo
    mysql_note "MySQL init process done. Ready for start up."
    echo

elif [[ "$STR" == 'Basis data sudah terinisialisasi.' ]] && test -n "$(shopt -s nullglob; echo /always-initdb.d/*)"; then
    # Replace variables in the sql initialization script
    /replace.sh /tmp/change_telebot_pass.sql /always-initdb.d/init.sql

    # Wait until the password for the telebot user is added into the initialization script
    STR=`cat /always-initdb.d/init.sql | grep 'ALTER USER'`
    SUB='__TELEBOT_PASSWORD__'

    while [[ "$STR" == *"$SUB"* ]]; do
        echo Menunggu password user sql bot telegram...
        sleep 5
        STR=`cat /always-initdb.d/init.sql | grep 'ALTER USER'`
    done

    SUB=$(awk '{ sub(/.*BY /, ""); sub(/;.*/, ""); print }' <<< "$STR")
    mysql_note "PASSWORD BOT TELEGRAM: $SUB"

    # Database exists; run always-run hooks if they exist
    mysql_note "Starting temporary server"
    docker_temp_server_start "$@"
    mysql_note "Temporary server started."

    docker_process_init_files /always-initdb.d/*

    mysql_note "Stopping temporary server"
    docker_temp_server_stop
    mysql_note "Temporary server stopped"

    echo > /always-initdb.d/*
    echo
    mysql_note "MySQL init process done. Ready for start up."
    echo
fi

exec "$@" --bind-address=0.0.0.0 --default-authentication-plugin=mysql_native_password

