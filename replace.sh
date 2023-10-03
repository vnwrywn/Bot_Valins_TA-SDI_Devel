#!/bin/bash
# Read the SQL script template
echo Memperbaharui berkas inisialisasi...
template=$(<"$1")

MYSQL_ROOT_PASSWORD=`cat $MYSQL_ROOT_PASSWORD_FILE`
MYSQL_PASSWORD=`cat $MYSQL_PASSWORD_FILE`
# Replace placeholders with environment variables
template=${template//__MYSQL_DATABASE__/$MYSQL_DATABASE}
template=${template//__MYSQL_USER__/$MYSQL_USER}
template=${template//__MYSQL_PASSWORD__/$MYSQL_PASSWORD}
template=${template//__MYSQL_ROOT_PASSWORD__/$MYSQL_ROOT_PASSWORD}
template=${template//__USERNAME__/$USERNAME}
template=${template//__NAMA_USER__/$NAMA_USER}

# Save the processed SQL script
echo "$template" > "$2"

