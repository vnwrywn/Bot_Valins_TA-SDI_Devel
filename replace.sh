#!/bin/bash
# Read the SQL script template
echo Memperbaharui berkas inisialisasi...
template=$(<"$1")

# Replace placeholders with environment variables
template=${template//__MYSQL_DATABASE__/$MYSQL_DATABASE}
template=${template//__TELEBOT_USER__/$TELEBOT_USER}
template=${template//__USERNAME__/$USERNAME}
template=${template//__NAMA_USER__/$NAMA_USER}
template=${template//__MYSQL_ROOT_PASSWORD__/$MYSQL_ROOT_PASSWORD}

# Save the processed SQL script
echo "$template" > "$2"

