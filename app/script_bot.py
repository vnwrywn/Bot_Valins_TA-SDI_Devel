#!/bin/python

###TODO!!!
# Fungsi input data
## Fungsi selective insert (SQL)
# Uji fungsi cari lokasi via text

### Importing necessary libraries
import configparser # pip install configparser
import csv
from datetime import datetime, timedelta
from functools import wraps
from geopy.geocoders import Nominatim
import haversine as hs
import io
# import logging
import jwt # pip install pyjwt
from math import ceil, radians, sin, cos, sqrt, atan2
# import MySQLdb # pip install mysqlclient
import os
import openpyxl
import pymysql
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import time

SQRTo2 = sqrt(2)

# # Read values for MySQLdb
# HOSTNAME = config.get('TELEGRAM','hostname')
# USERNAME = config.get('TELEGRAM','username')
# PASSWORD = config.get('TELEGRAM','password')
# DATABASE = config.get('TELEGRAM','database')
# Get Telegram bot token from configuration

def create_mysql_connection():
    print('Configuring...', flush = True)
    config = configparser.ConfigParser()
    config.read('/app/config.ini')

    host = config.get('MYSQL', 'hostname')
    user = config.get('MYSQL', 'username')
    password = config.get('MYSQL', 'password')
    database = config.get('MYSQL', 'database')
    port = int(config.get('MYSQL', 'port'))

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

# Main Function
def main():
    ### Initializing Configuration
    print('Initializing configuration...', flush = True)
    config = configparser.ConfigParser()
    config.read('/app/config.ini')

    BOT_TOKEN = config.get('TELEGRAM','bot_token')

    # logging.basicConfig(level=logging.DEBUG)
    app = Application.builder().token(BOT_TOKEN).build()

    ### Conversation Handler Menu Input
    input_data_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_input, pattern='^opsi_input_data$')],
        states={
            1: [CallbackQueryHandler(input_data, pattern='^input_')],
            2: [MessageHandler(filters.Document.FileExtension('xlsx'), input_satuan_xlsx), MessageHandler(filters.Document.FileExtension('csv'), input_satuan_csv)],
            3: [MessageHandler(filters.Document.FileExtension('xlsx'), input_pangkas_xlsx), MessageHandler(filters.Document.FileExtension('csv'), input_pangkas_csv)]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    ### Conversation Handler Menu Tambah User
    tambah_user_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(tambah_user, pattern='^opsi_tambah_user$')],
        states={
            1: [CallbackQueryHandler(input_tambah_user, pattern='^tambah_')],
            2: [MessageHandler(filters.TEXT & (~ filters.COMMAND), proses_tambah_user)],
            3: [MessageHandler(filters.TEXT & (~ filters.COMMAND), proses_tambah_admin)]
            # 4: [CallbackQueryHandler(konfirmasi_tambah_user, pattern='^konfirmasi_tambah_')]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    ### Conversation Handler Menu Hapus User
    hapus_user_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(hapus_user, pattern='^opsi_hapus_user$')],
        states={
            1: [CallbackQueryHandler(konfirmasi_hapus_user, pattern='^hapus_')],
            2: [CallbackQueryHandler(proses_hapus_user, pattern='^konfirmasi_hapus_')]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    ### Conversation Handler Menu Peroleh Lokasi
    peroleh_lokasi_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(peroleh_lokasi, pattern='^opsi_peroleh_lokasi$')],
        states={
            1: [CallbackQueryHandler(proses_peroleh_lokasi_button, pattern='^item_'), MessageHandler(filters.TEXT & (~ filters.COMMAND), proses_peroleh_lokasi_text)]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    ### Conversation Handler Menu Peroleh Daftar
    peroleh_nama_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(peroleh_nama_1, pattern='^opsi_peroleh_nama$')],
        states={
            1: [MessageHandler(filters.LOCATION, peroleh_nama_2)],
            2: [MessageHandler(filters.TEXT & (~ filters.COMMAND), proses_peroleh_nama)]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    ### Conversation Handler Menu Peroleh File
    peroleh_berkas_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(peroleh_berkas, pattern='^opsi_peroleh_berkas$')],
        states={
            1: [MessageHandler(filters.TEXT & (~ filters.COMMAND), proses_peroleh_berkas)]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    ### Conversation Handler Token
    peroleh_token_handler = ConversationHandler(
        entry_points=[CommandHandler('peroleh_token', peroleh_token)],
        states={
            1: [MessageHandler(filters.TEXT & (~ filters.COMMAND), peroleh_token_process)]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    # Handlers
    app.add_handler(CommandHandler('start', main_menu))
    app.add_handler(input_data_handler)
    app.add_handler(tambah_user_handler)
    app.add_handler(hapus_user_handler)
    app.add_handler(peroleh_lokasi_handler)
    app.add_handler(CommandHandler('peroleh_lokasi', peroleh_lokasi_func))
    app.add_handler(peroleh_nama_handler)
    app.add_handler(peroleh_berkas_handler)
    app.add_handler(peroleh_token_handler)
    app.add_handler(CommandHandler('peroleh_username', peroleh_username))
    app.add_handler(CommandHandler('bantuan', kirim_bantuan))
    app.add_handler(CallbackQueryHandler(kirim_bantuan, pattern='^opsi_bantuan$'))

    while True:
        try:
            print('Polling...', flush = True)
            app.run_polling(poll_interval=4)
        except Exception as e:
            print(e, flush = True)
            time.sleep(10)
            continue

def exclude_commands_filter(update):
    return not update.message.text.startswith('/')

### Middleware functions for user authentication
def authenticate_user(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False], *args, **kwargs):
        # Check if the user is authenticated
        auth_status_res = is_authenticated(update.effective_user.id)
        if auth_status_res[0]:
            # User is authenticated, execute the command handler
            return await func(update, context, auth_status_res, *args, **kwargs)
        else:
            # User is not authenticated.
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Access denied.')
    return wrapper

def authenticate_admin(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False], *args, **kwargs):
        # Check if the user is authenticated and is an admin
        auth_status_res = is_authenticated(update.effective_user.id)
        if auth_status_res[0] and auth_status_res[1]:
            # Admin is authenticated, execute the command handler
            return await func(update, context, auth_status_res, *args, **kwargs)
        else:
            # User is not authenticated or not an admin.
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Access denied.')
    return wrapper

# Function to check user access in the database
def is_authenticated(user_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    # Check if the user is an admin
    query_admin = 'SELECT `is_admin` FROM `allowed_users` WHERE `username` = %s'
    cursor.execute(query_admin, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result == None:
        return [False, False]
    elif result[0]:
        return [True, True]  # Return True if user is an admin with full access
    else:
        return [True, False]  # Return True if user is an admin with full access

def check_conv_status(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False], *args, **kwargs):
        if context.chat_data.get('in_conversation'):
            await update.message.reply_text('Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        else:
            # User is not authenticated or not an admin.
            return await func(update, context, auth_status, *args, **kwargs)
    return wrapper

# Retrieve data from MySQL
def peroleh_nama_site():
    connection = create_mysql_connection()
    cursor = connection.cursor()
    query = 'SELECT `Site_ID_Tenant` FROM `site_data`'
    cursor.execute(query)
    site_ids = [Site_ID_Tenant[0] for Site_ID_Tenant in cursor]
    cursor.close()
    connection.close()
    return site_ids

def cek_nama_site(site_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    query = 'SELECT 1 FROM `site_data` WHERE `Site_ID_Tenant` = %s'
    cursor.execute(query, (site_id))
    exists = cursor.fetchone()
    cursor.close()
    connection.close()
    return exists

# Retrieve Sites Datas from MySQL
def peroleh_data_site(site_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    query = 'SELECT `Site_ID_Tenant`, `Tenant`, `Alamat`, `Latitude`, `Longitude` FROM `site_data` WHERE `Site_ID_Tenant` = %s'
    cursor.execute(query, (site_id))
    site_data = cursor.fetchone()
    cursor.close()
    connection.close()
    return site_data

# Retrieve datas using radius and location
def peroleh_dari_radius(latitude, longitude, radius):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    coordinates = (latitude, longitude)
    sqrt_rds = radius * SQRTo2
    max_lat = hs.inverse_haversine(coordinates, sqrt_rds, hs.Direction.NORTH, unit=hs.Unit.METERS)[0]
    max_lon = hs.inverse_haversine(coordinates, sqrt_rds, hs.Direction.EAST, unit=hs.Unit.METERS)[1]
    min_lat = hs.inverse_haversine(coordinates, sqrt_rds, hs.Direction.SOUTH, unit=hs.Unit.METERS)[0]
    min_lon = hs.inverse_haversine(coordinates, sqrt_rds, hs.Direction.WEST, unit=hs.Unit.METERS)[1]
    query = 'SELECT `Site_ID_Tenant`, `Tenant`, `Alamat`, `Latitude`, `Longitude` FROM `site_data` WHERE `Latitude` BETWEEN %s AND %s AND `Longitude` BETWEEN %s AND %s'
    cursor.execute(query, (min_lat, max_lat, min_lon, max_lon))
    square_res = cursor.fetchall()
    results = []

    for item in square_res:
        dist = hs.haversine((latitude, longitude), (item[3], item[4]), unit=hs.Unit.METERS)
        if dist <= radius:
            results.append(item)
    connection.close()
    return results

# Insert data into MySQL
def truncate_and_insert_sites(site_datas):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    truncate = 'TRUNCATE TABLE `site_data`;'
    cursor.execute(truncate)
    insert = 'INSERT INTO `site_data` (`Site_ID_Tenant`, `Tenant`, `Alamat`, `Latitude`, `Longitude`) VALUES (%s, %s, %s, %s, %s);'
    cursor.executemany(insert, [list(dictionary.values()) for dictionary in site_datas])
    connection.commit()
    connection.close()
    return

def insert_sites(site_datas):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    insert = 'INSERT INTO `site_data` (`Site_ID_Tenant`, `Tenant`, `Alamat`, `Latitude`, `Longitude`) VALUES (%s, %s, %s, %s, %s);'
    cursor.executemany(insert, [list(dictionary.values()) for dictionary in site_datas])
    connection.commit()
    connection.close()
    return

### Main Menu
@authenticate_user
@check_conv_status
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    keyboard = [
        [InlineKeyboardButton('Peroleh Lokasi Item', callback_data='opsi_peroleh_lokasi')],
        [InlineKeyboardButton('Peroleh Daftar Item Terdekat', callback_data='opsi_peroleh_nama')],
        [InlineKeyboardButton('Peroleh File Site', callback_data='opsi_peroleh_berkas')],
        [InlineKeyboardButton('Bantuan', callback_data='opsi_bantuan')]
    ]

    if auth_status[1]:
        keyboard =  [
            [InlineKeyboardButton('Input Data', callback_data='opsi_input_data')],
            [InlineKeyboardButton('Tambah User', callback_data='opsi_tambah_user')],
            [InlineKeyboardButton('Hapus User', callback_data='opsi_hapus_user')],
        ] + keyboard

    await update.message.reply_text('Menu Utama', reply_markup=InlineKeyboardMarkup(keyboard))

### Input Data
@authenticate_admin
@check_conv_status
async def menu_input(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    context.chat_data['in_conversation'] = True
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    keyboard = [
        [InlineKeyboardButton('Pangkas dan Input', callback_data='input_keseluruhan')],
        [InlineKeyboardButton('Input Satuan', callback_data='input_satuan')],
    ]

    await context.bot.send_message(chat_id=query.message.chat_id, text='Pilih metode input.', reply_markup=InlineKeyboardMarkup(keyboard))
    return 1

@authenticate_admin
async def input_data(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    button_pressed = query.data

    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan unggah berkas.')

    if button_pressed == 'input_satuan':
        return 2

    return 3

@authenticate_admin
async def input_satuan_xlsx(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    path = os.environ['APP_TMP_DATA'] + '/input.xlsx'
    await (await context.bot.get_file(update.message.document.file_id)).download_to_drive(custom_path=path)
    output = []
    wb =  openpyxl.load_workbook(path)
    ws = wb.active
    key = [ws.cell(1, col + 1).value for col in range(4)]
    count = 0

    for row in range(2, ws.max_row + 1):
        if cek_nama_site(ws.cell(row, 1).value):
            continue

        else:
            output.append({key[col]: ws.cell(row, col + 1).value for col in range(4)})
            output[-1]['Latitude'], output[-1]['Longitude'] = (float(value) for value in output[-1].pop('Koordinat Site').split(','))
            output[-1]['Alamat'] = cari_alamat((output[-1]['Latitude'], output[-1]['Longitude']))
            count += 1

    insert_sites(output)
    await update.message.reply_text(f'Input satuan {count} baris berhasil.')
    return akhiri_percakapan(context)

@authenticate_admin
async def input_satuan_csv(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    file = await context.bot.get_file(update.message.document.file_id)
    buffer = io.BytesIO()
    await file.download_to_memory(out=buffer)
    file_size = len(buffer.getvalue())
    output = []
    site_list = peroleh_nama_site()
    count = 0

    with io.TextIOWrapper(io.BytesIO(buffer.getvalue())) as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            if cek_nama_site(row['Site_ID_Tenant']):
                continue

            else:
                row['Latitude'], row['Longitude'] = (float(value) for value in row.pop('Koordinat Site').split(','))
                row['Alamat'] = cari_alamat((row['Latitude'], row['Longitude']))
                output.append(row)
                count += 1

    insert_sites(output)
    await update.message.reply_text(f'Input satuan {count} baris berhasil.')
    return akhiri_percakapan(context)

@authenticate_admin
async def input_pangkas_xlsx(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    path = os.environ['APP_TMP_DATA'] + '/input.xlsx'
    await (await context.bot.get_file(update.message.document.file_id)).download_to_drive(custom_path=path)
    output = []
    wb =  openpyxl.load_workbook(path)
    ws = wb.active
    key = [ws.cell(1, col + 1).value for col in range(4)]
    count = 0

    for row in range(2, ws.max_row + 1):
        output.append({key[col]: ws.cell(row, col + 1).value for col in range(4)})
        output[-1]['Latitude'], output[-1]['Longitude'] = (float(value) for value in output[-1].pop('Koordinat Site').split(','))
        output[-1]['Alamat'] = cari_alamat((output[-1]['Latitude'], output[-1]['Longitude']))
        count += 1

    truncate_and_insert_sites(output)
    await update.message.reply_text(f'Input pangkas {count} baris berhasil.')
    return akhiri_percakapan(context)

@authenticate_admin
async def input_pangkas_csv(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    file = await context.bot.get_file(update.message.document.file_id)
    buffer = io.BytesIO()
    await file.download_to_memory(out=buffer)
    file_size = len(buffer.getvalue())
    output = []
    count = 0

    with io.TextIOWrapper(io.BytesIO(buffer.getvalue())) as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            row['Latitude'], row['Longitude'] = (float(value) for value in row.pop('Koordinat Site').split(','))
            row['Alamat'] = cari_alamat((row['Latitude'], row['Longitude']))
            output.append(row)
            count += 1

    truncate_and_insert_sites(output)
    await update.message.reply_text(f'Input pangkas {count} baris berhasil.')
    return akhiri_percakapan(context)

def cari_alamat(koordinat):
    ongoing = True
    geolocator = Nominatim(user_agent='Geocoder')

    while ongoing:
        sleeptime = 1
        try:
            location = geolocator.reverse(koordinat)
            ongoing = False
            return location.address
        except Exception as e:
            print('Geocoder error.', e, 'Retrying', flush = True)
            sleeptime += 1
            time.sleep(sleeptime)
            pass

    return None

### Tambah User
@authenticate_admin
@check_conv_status
async def tambah_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    context.chat_data['in_conversation'] = True

    keyboard = [
        [InlineKeyboardButton('Tambahkan User Reguler', callback_data='tambah_reguler')],
        [InlineKeyboardButton('Tambahkan User Admin', callback_data='tambah_admin')],
    ]

    await context.bot.send_message(chat_id=query.message.chat_id, text='Pilih jenis user.', reply_markup=InlineKeyboardMarkup(keyboard))
    return 1

@authenticate_admin
async def input_tambah_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    button_pressed = query.data
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if button_pressed == 'tambah_reguler':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan masukkan token. Untuk membuat token, calon user reguler tersangkut harus menjalankan perintah /peroleh_token dan memberikan nama lengkapnya dalam tahapan yang dijalankan.')
        return 2

    await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan masukkan ID pengguna. Untuk membuat token, calon user admin tersangkut harus menjalankan perintah /peroleh_token dan memberikan nama lengkapnya dalam tahapan yang dijalankan.')
    return 3

@authenticate_admin
async def proses_tambah_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    token = update.message.text
    decoded_token = jwt.decode(token, 'secret', algorithms=['HS256'])
    userid = decoded_token['user_id']
    nama = decoded_token['nama']

     # Cek apakah user dengan user_id tertentu sudah ada di database
    if user_exists(userid):
        await update.message.reply_text('User ID yang dimasukkan telah terdaftar. Proses tambah user dibatalkan.')
        return akhiri_percakapan(context)

    # Jika user belum terdaftar, tambahkan user baru ke database
    add_user(userid, nama)

    await update.message.reply_text(f'Berhasil menambahkan user berikut.\nUser ID: {userid}\nNama: {nama}')
    return akhiri_percakapan(context)

@authenticate_admin
async def proses_tambah_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    token = update.message.text
    decoded_token = jwt.decode(token, 'secret', algorithms=['HS256'])
    userid = decoded_token['user_id']
    nama = decoded_token['nama']

    # Cek apakah admin dengan user_id tertentu sudah ada di database
    if user_exists(userid):
        await update.message.reply_text('User ID yang dimasukkan telah terdaftar. Proses tambah admin dibatalkan.')
        return akhiri_percakapan(context)

    # Jika admin belum terdaftar, tambahkan admin baru ke database
    add_admin(userid, nama)

    await update.message.reply_text(f'Berhasil menambahkan admin berikut.\nUser ID: {userid}\nNama: {nama}')
    return akhiri_percakapan(context)

# Fungsi untuk cek apakah user dengan user_id tertentu sudah ada di database
def user_exists(user_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    query = 'SELECT 1 FROM `allowed_users` WHERE `username` = %s'
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None

# Fungsi untuk menambahkan user baru ke database
def add_user(user_id, nama):
     connection = create_mysql_connection()
     cursor = connection.cursor()

     query = 'INSERT INTO `allowed_users` (`username`, `nama`, `is_admin`) VALUES (%s, %s, 0)'
     cursor.execute(query, (user_id, nama))

     connection.commit()
     cursor.close()
     connection.close()

# Fungsi untuk menambahkan admin baru ke database
def add_admin(user_id, nama):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    query = 'INSERT INTO `allowed_users` (`username`, `nama`, `is_admin`) VALUES (%s, %s, 1)'
    cursor.execute(query, (user_id, nama))

    connection.commit()
    cursor.close()
    connection.close()


# HAPUS USER
# Fungsi untuk memperoleh seluruh nama user
def peroleh_data_user():
    connection = create_mysql_connection()
    cursor = connection.cursor()
    query = 'SELECT `username`, `nama` FROM `allowed_users`'
    cursor.execute(query)
    data_user = cursor.fetchall()
    cursor.close()
    connection.close()
    return data_user

# Fungsi untuk menghapus user dari database
def delete_user(username):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    # Implementasi penghapusan user dari database
    delete_query = 'DELETE FROM allowed_users WHERE username = %s'
    cursor.execute(delete_query, (user_id,))
    connection.commit()

    cursor.close()
    connection.close()

# Fungsi untuk memeriksa apakah user merupakan admin terakhir atau bukan
def is_last_admin(username):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    # Implementasi pengecekan apakah user merupakan admin terakhir atau bukan
    is_admin_query = 'SELECT `is_admin` FROM `allowed_users` WHERE `username` = %s'
    cursor.execute(is_admin_query)

    if (cursor.fetchone()[0]):
        cursor.close()
        admin_count_query = 'SELECT COUNT(*) FROM `allowed_users` WHERE `is_admin` = 1'
        cursor = connection.cursor()
        cursor.execute(admin_count_query)
        admin_count = cursor.fetchone()[0]
    else:
        admin_count = 2

    cursor.close()
    connection.close()

    return admin_count <= 1

@authenticate_admin
@check_conv_status
async def hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    context.chat_data['in_conversation'] = True

    user_list = peroleh_data_user()
    keyboard = [[InlineKeyboardButton(user[1], callback_data = 'hapus_{0}_{1}'.format(user[1], user[0]))] for user in user_list]

    await context.bot.send_message(chat_id=query.message.chat_id, text='Pilih user yang mau dihapus, atau keluar dari proses dengan menggunakan fungsi /batal.', reply_markup=InlineKeyboardMarkup(keyboard))
    return 1

#  Fungsi untuk memproses hapus user
@authenticate_admin
async def konfirmasi_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query

    # Ambil nama user dari inputan chat yang masuk
    nama_user, username = query.data.split('_')[1:]
    print(query.data.split('_')[1:], flush=True)
    print(username, flush=True)

    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    keyboard = [
        [InlineKeyboardButton('Ya', callback_data='konfirmasi_hapus_ya')],
        [InlineKeyboardButton('Tidak', callback_data='konfirmasi_hapus_tidak')],
    ]
    await context.bot.send_message(chat_id=query.message.chat_id, text=f'Apakah Anda yakin mau menghapus {nama_user} dari daftar user??', reply_markup=InlineKeyboardMarkup(keyboard))

    # Simpan nama user ke dalam chat data untuk digunakan saat proses hapus user
    context.chat_data['nama_user'] = nama_user
    context.chat_data['username'] = username

    return 2

# Fungsi untuk proses hapus user
@authenticate_admin
async def proses_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    button_pressed = query.data
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if button_pressed == 'konfirmasi_hapus_ya':
        # Ambil nama user dari chat data
        username = context.chat_data.get('username')
        if not username:
            reply = 'Terjadi kesalahan saat memproses penghapusan user.'
        elif is_last_admin(username):
            reply = 'Tidak bisa menghapus user admin terakhir. Silahkan tambahkan admin baru terlebih dahulu. Proses penghapusan user dibatalkan.'
        else:
            # Hapus user dari database
            delete_user(username)
            reply = '{0} berhasil dihapus dari daftar user.'.format(context.chat_data.get('username'))

        await context.bot.send_message(chat_id=query.message.chat_id, text=reply)
    elif button_pressed == 'konfirmasi_hapus_tidak':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Proses penghapusan user dibatalkan.')

    return akhiri_percakapan(context)

@authenticate_admin
async def konfirmasi_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    button_pressed = query.data
    nama = context.chat_data['nama_user'] = button_pressed[6:].replace('_', ' ')
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    keyboard = [
        [InlineKeyboardButton('Ya', callback_data='konfirmasi_hapus_ya')],
        [InlineKeyboardButton('Tidak', callback_data='konfirmasi_hapus_tidak')],
    ]
    await context.bot.send_message(chat_id=query.message.chat_id, text=f'Apakah anda yakin mau menghapus {nama} dari daftar user?', reply_markup=InlineKeyboardMarkup(keyboard))
    return 2

@authenticate_admin
async def proses_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    button_pressed = query.data
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if button_pressed == 'konfirmasi_hapus_ya':
        if context.chat_data['nama_user'] == 'M. Ivan Wiryawan':
            reply = 'Tidak bisa menghapuskan user admin terakhir, silahkan tambahkan admin baru terlebih dahulu. Proses penghapusan user dibatalkan.'
        else:
            reply = context.chat_data['nama_user'] + ' berhasil dihapuskan dari daftar user.'
    elif button_pressed == 'konfirmasi_hapus_tidak':
        reply = 'Proses penghapusan user dibatalkan.'

    await context.bot.send_message(chat_id=query.message.chat_id, text=reply)
    return akhiri_percakapan(context)

### Peroleh Lokasi
@authenticate_user
@check_conv_status
async def peroleh_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    context.chat_data['in_conversation'] = True
    site_list = peroleh_nama_site()
    context.chat_data['site_list'] = site_list
    keyboard = []

    for i in range(ceil(len(site_list)/3)):
        temp_item = site_list[i * 3]
        keyboard.append([InlineKeyboardButton(temp_item, callback_data='item_' + temp_item)])

        for j in range(1, 3):
            try:
                temp_item = site_list[i * 3 + j]
                keyboard[-1].append(InlineKeyboardButton(temp_item, callback_data='item_' + temp_item))
            except IndexError:
                break

    message = await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan masukkan nama item atau pilih item dari tombol di bawah ini.', reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data['last_message_id'] = message.message_id
    return 1

# Fungsi untuk memproses peroleh lokasi
@authenticate_user
async def proses_peroleh_lokasi_text(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    await context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id, message_id=context.user_data.get('last_message_id'), reply_markup=None)
    text = update.message.text
    if len(text) == 8 and text.isalnum():

        # Cek apakah site dengan Site_ID_Tenant tertentu ada di database
        try:
            site = peroleh_data_site(next(item for item in context.chat_data['site_list'] if item == text.upper()))
            await kirim_data_item(update, context, [False, False], site)
            return akhiri_percakapan(context)
        except StopIteration:
            await update.message.reply_text('Site tidak ditemukan. Silahkan masukkan atau pilih kembali nama site atau keluar dari proses dengan menggunakan fungsi /batal.')
            return 1

    await update.message.reply_text('Format penamaan salah. Silahkan masukkan atau pilih kembali nama site atau keluar dari proses dengan menggunakan fungsi /batal.')
    return 1

@authenticate_user
async def proses_peroleh_lokasi_button(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    # Cek apakah site dengan Site_ID_Tenant tertentu ada di database
    try:
        site = peroleh_data_site(next(item for item in context.chat_data['site_list'] if item == query.data[5:]))
        await kirim_data_item(update, context, [False, False], site)
        return akhiri_percakapan(context)
    except StopIteration:
        await context.bot.send_message(chat_id=query.message.chat_id, text='Site tidak ditemukan. Silahkan masukkan atau pilih kembali nama site atau keluar dari proses dengan menggunakan fungsi /batal.')
        return 1

# Fungsi untuk memparse koordinat
def parse_coordinates(coordinates):
    coordinates = coordinates.split(',')
    latitude = float(''.join(filter(lambda c: c.isdigit() or c in ['.', '-'], coordinates[0].strip())))
    longitude = float(''.join(filter(lambda c: c.isdigit() or c in ['.', '-'], coordinates[1].strip())))
    return latitude, longitude


@authenticate_user
@check_conv_status
async def peroleh_lokasi_func(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    args = context.args
    if args:
        argument = args[0]
        if len(argument) == 8 and argument.isalnum():

            # Cek apakah site dengan Site_ID_Tenant tertentu ada di database
            site = peroleh_data_site(text.upper())

            if site:
                await kirim_data_item(update, context, [False, False], site[0])

            else:
                await update.message.reply_text('Site tidak ditemukan.')

        else:
            await update.message.reply_text('Format penamaan salah.')
    else:
        await update.message.reply_text('Sintaks: /peroleh_lokasi [nama item]\nContoh: /peroleh_lokasi 20BAT001')

### Peroleh Nama
@authenticate_user
@check_conv_status
async def peroleh_nama_1(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    context.chat_data['in_conversation'] = True
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Kirimkan Lokasi Pencarian.')
    return 1

@authenticate_user
async def peroleh_nama_2(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    location = update.message.location
    context.chat_data['latitude'] = location.latitude
    context.chat_data['longitude'] = location.longitude
    await update.message.reply_text('Kirimkan radius pencarian dalam satuan meter.')
    return 2

# Fungsi async untuk memproses input pengguna
async def proses_peroleh_nama(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    dist = update.message.text

    if dist.lstrip('-').replace(',', '').replace('.', '').isnumeric():
        radius_meter = float(dist.replace(',', '.'))

        if radius_meter <= 0:
            await update.message.reply_text('Nilai radius harus lebih besar dari 0. Silahkan masukkan kembali nilai radius atau keluar dari proses dengan menggunakan fungsi /batal.')
            return 2

        else:
            # Dapatkan lokasi pengguna dari chat_data
            user_latitude = float(context.chat_data['latitude'])
            user_longitude = float(context.chat_data['longitude'])

            # Hitung daftar situs dalam radius
            sites_in_radius = peroleh_dari_radius(user_latitude, user_longitude, radius_meter)

            if sites_in_radius:
                for site in sites_in_radius:
                    await kirim_data_item(update, context, [False, False], site)
                return akhiri_percakapan(context)
            else:
                await update.message.reply_text(f'Tidak ada item dalam radius {radius_meter} meter dari lokasi. Silahkan masukkan kembali nilai radius atau keluar dari proses dengan menggunakan fungsi /batal.')
                return 2

    await update.message.reply_text('Radius harus berupa bilangan cacah atau pecahan desimal > 0 dalam satuan meter. Contoh: 1000. Silahkan masukkan kembali nilai radius atau keluar dari proses dengan menggunakan fungsi /batal.')
    return 2

@authenticate_user
@check_conv_status
async def peroleh_berkas(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    context.chat_data['in_conversation'] = True
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Masukkan nama site.')
    return 1

@authenticate_user
async def proses_peroleh_berkas(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    site_name = update.message.text
    file_path = f'/files/{site_name}.txt'

    if os.path.exists(file_path):
        chat_id = update.effective_chat.id
        await context.bot.send_document(chat_id=chat_id, document=open(file_path, 'rb'))
    else:
        await update.message.reply_text("Berkas tidak ditemukan. Silahkan masukkan kembali nama berkas atau keluar dari proses dengan menggunakan fungsi /batal.")
        return 1

    return akhiri_percakapan(context)

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    if context.chat_data['in_conversation']:
        await update.message.reply_text('Proses telah dibatalkan.')
        return akhiri_percakapan(context)

    await update.message.reply_text('Tidak ada proses yang sedang berjalan.')

def akhiri_percakapan(context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

@authenticate_user
async def kirim_bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    query = update.callback_query
    try:
        await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    except Exception:
        pass
    text='''Fungsi Dasar
/start
Memulai percakapan. Percakapan tidak dapat dimulai apabila sebuah proses sedang berjalan. Lihat /batal.
/batal
Mengakhiri proses. Mengakhiri proses yang sedang berjalan dan membuka kemungkinan untuk memulai kembali percakapan.
/bantuan
Melihat bantuan penggunaan (teks ini).
/peroleh_token
Peroleh token untuk keperluan autentikasi. Penjalanan fungsi ini tidak memerlukan autentikasi.

Arahan Menu
Menu Utama: Berisi berbagai pilihan untuk membuka submenu.
Input Data: Menjalankan proses untuk memasukkan data ke dalam basis data.
Peroleh Lokasi Item: Menjalankan proses untuk memperoleh lokasi item berdasarkan nama item.
Peroleh Nama Item: Menjalankan proses untuk memperoleh nama-nama item berdasarkan lokasi.
Peroleh File Site: Menjalankan proses untuk memperoleh berkas-berkas berdasarkan nama.

Apabila memerlukan bantuan tambahan, anda dapat menghubungi helpdesk pada...'''
    await context.bot.send_message(chat_id=query.message.chat_id, text=text)

async def peroleh_token(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    await update.message.reply_text(f'Mohon kirimkan nama lengkap anda.')
    return 1

async def peroleh_token_process(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    nama = update.message.text.capitalize()
    user_id = str(update.message.from_user.id)
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    payload = {
        'user_id': user_id,
        'nama': nama,
        'exp': expiration_time
    }

    token = jwt.encode(payload, 'secret', algorithm='HS256')
    await update.message.reply_text(f'Token anda adalah: {token}')
    return akhiri_percakapan(context)

async def peroleh_username(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=[False, False]):
    await update.message.reply_text(f'Username anda adalah: {str(update.message.from_user.id)}')

@authenticate_user
async def kirim_data_item(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status, data):
    text = 'Site\_ID\_Tenant: {}\n'.format(data[0])
    text += 'Tenant: {}\n'.format(data[1])
    text += 'Alamat: {}\n'.format(data[2])
    text += 'Koordinat Site: [{0},{1}](http://maps.google.com/maps?q={0},{1})\n'.format(data[3], data[4])
    query = update.callback_query

    if query:
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
        await context.bot.send_location(chat_id=query.message.chat_id, latitude=data[3], longitude=data[4])
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_location(data[3], data[4])

##### MAIN
if __name__ == '__main__':
    main()
