# Read the SQL script template
echo Initializing...
file="/docker-entrypoint-initdb.d/init.sql"
template=$(<"$file")

# Replace placeholders with environment variables
template=${template//__MYSQL_DATABASE__/$MYSQL_DATABASE}
template=${template//__TELEBOT_USER__/$TELEBOT_USER}
template=${template//__TELEBOT_PASSWORD__/$TELEBOT_PASSWORD}
template=${template//__USERNAME__/$USERNAME}
template=${template//__NAMA_USER__/$NAMA_USER}

# Save the processed SQL script
printf '# TIDAK UNTUK DISUNTING SECARA MANUAL\n# Naskah ini digenerasi oleh deploy.sh atau deploy.bat.\n# Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data.\n\n' > "$file"
echo "$template" >> "$file"
