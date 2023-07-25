###TODO!!!
# Fungsi tambah user (Token)

### Importing necessary libraries
import pymysql
import configparser # pip install configparser
# import logging
import jwt # pip install pyjwt
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from functools import wraps
# from datetime import datetime
# import MySQLdb # pip install mysqlclient

### Initializing Configuration
print('Initializing configuration...')
config = configparser.ConfigParser()
config.read('config1.ini')

API_ID = config.get('default','api_id')
API_HASH = config.get('default','api_hash')
BOT_TOKEN = config.get('default','bot_token')
session_name = 'sessions/Bot'

# # Read values for MySQLdb
# HOSTNAME = config.get('default','hostname')
# USERNAME = config.get('default','username')
# PASSWORD = config.get('default','password')
# DATABASE = config.get('default','database')
# Get Telegram bot token from configuration

def create_mysql_connection():
    host = config.get('MYSQL', 'hostname')
    user = config.get('MYSQL', 'username')
    password = config.get('MYSQL', 'password')
    database = config.get('MYSQL', 'database')

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

# Main Function
def main():
    # logging.basicConfig(level=logging.DEBUG)
    app = Application.builder().token(BOT_TOKEN).build()

    ### Conversation Handler Menu Input
    input_data_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_input, pattern='^opsi_input_data$')],
        states={
            1: [CallbackQueryHandler(input_data, pattern='^input_')],
            2: [MessageHandler(filters.Document.MimeType('text/plain'), input_satuan)],
            3: [MessageHandler(filters.Document.MimeType('text/plain'), input_pangkas)]
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
        entry_points=[CallbackQueryHandler(delete_user, pattern='^opsi_hapus_user$')],
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
            1: [MessageHandler(filters.TEXT & (~ filters.COMMAND), proses_peroleh_lokasi)]
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
        entry_points=[CallbackQueryHandler(peroleh_berkas, pattern='^opsi_peroleh_file$')],
        states={
            1: [MessageHandler(filters.TEXT & (~ filters.COMMAND), proses_peroleh_berkas)]
        },
        fallbacks=[CommandHandler('batal', batal)]
    )

    ### Conversation Handler Token
    peroleh_berkas_handler = ConversationHandler(
        entry_points=[CommandHandler('get_token', get_token)],
        states={
            1: [MessageHandler(filters.TEXT & (~ filters.COMMAND), get_token_process)]
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
    app.add_handler(CommandHandler('help', bantuan))
    app.add_handler(CallbackQueryHandler(bantuan, pattern='^opsi_bantuan$'))
    print('Polling...')
    app.run_polling(poll_interval=5)

def exclude_commands_filter(update):
    return not update.message.text.startswith('/')

### Middleware functions for user authentication
def authenticate_user(func):
    @wraps(func)
    def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
        # Check if the user is authenticated
        auth_status = is_authenticated(update.effective_user.id)
        if auth_status[0]:
            # User is authenticated, execute the command handler
            return func(update, context, auth_status)
        else:
            # User is not authenticated.
            context.bot.send_message(chat_id=update.effective_chat.id, text='Access denied.')
    return wrapper

def authenticate_admin(func):
    @wraps(func)
    def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
        # Check if the user is authenticated and is an admin
        auth_status = is_authenticated(update.effective_user.id)
        if auth_status[0] and auth_status[1]:
            # Admin is authenticated, execute the command handler
            return func(update, context)
        else:
            # User is not authenticated or not an admin.
            context.bot.send_message(chat_id=update.effective_chat.id, text='Access denied.')
    return wrapper

# Function to check user access in the database
def is_authenticated(user_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    # Check if the user is an admin
    query_admin = "SELECT is_admin FROM allowed_users WHERE username = %s"
    cursor.execute(query_admin, (user_id,))
    result_admin = cursor.fetchone()
    cursor.close()
    connection.close()

    if query_admin == None:
        return [False, False]
    elif query_admin:
        return [True, True]  # Return True if user is an admin with full access
    else:
        return [True, False]  # Return True if user is an admin with full access

# Retrieve data from MySQL
def get_sites(site_id=None):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    query = "SELECT Site_ID_Tenant, Tenant, Alamat, Koordinat_Site FROM site_data"
    if site_id:
        query += f" WHERE Site_ID_Tenant = '{site_id}'"

    cursor.execute(query)

    sites = []
    for (site_id, tenant, alamat, koordinat) in cursor:
        sites.append({
            'site_id': site_id,
            'tenant': tenant,
            'alamat': alamat,
            'koordinat': koordinat
        })

    cursor.close()
    connection.close()

    return sites

### Main Menu
@authenticate_user
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    if context.chat_data.get('in_conversation'):
        await update.message.reply_text('Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        return

    keyboard = [
        [InlineKeyboardButton('Peroleh Lokasi Item', callback_data='opsi_peroleh_lokasi')],
        [InlineKeyboardButton('Peroleh Daftar Item Terdekat', callback_data='opsi_peroleh_nama')],
        [InlineKeyboardButton('Peroleh File Set', callback_data='opsi_peroleh_file')],
        [InlineKeyboardButton('Bantuan', callback_data='opsi_bantuan')]
    ]

    if update.message.from_user.id == 1139987918:
        keyboard =  [
            [InlineKeyboardButton('Input Data', callback_data='opsi_input_data')],
            [InlineKeyboardButton('Tambah User', callback_data='opsi_tambah_user')],
            [InlineKeyboardButton('Hapus User', callback_data='opsi_hapus_user')],
        ] + keyboard

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Menu Utama', reply_markup=reply_markup)

### Input Data
@authenticate_admin
async def menu_input(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    if context.chat_data.get('in_conversation'):
        await context.bot.send_message(chat_id=query.message.chat_id, text='Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        return

    context.chat_data['in_conversation'] = True
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    keyboard = [
        [InlineKeyboardButton('Pangkas dan Input', callback_data='input_keseluruhan')],
        [InlineKeyboardButton('Input Satuan', callback_data='input_satuan')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Pilih metode input.', reply_markup=reply_markup)
    return 1

@authenticate_admin
async def input_data(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    button_pressed = query.data

    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if button_pressed == 'input_satuan':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan unggah berkas.')
        return 2

    await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan unggah berkas.')
    return 3

@authenticate_admin
async def input_satuan(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    file = context.bot.get_file(update.message.document.file_id)
    await update.message.reply_text('Input satuan berhasil.')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

@authenticate_admin
async def input_pangkas(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    file = context.bot.get_file(update.message.document.file_id)
    await update.message.reply_text('Pangkas dan input berhasil.')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

### Tambah User
@authenticate_admin
async def tambah_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if context.chat_data.get('in_conversation'):
        await context.bot.send_message(chat_id=query.message.chat_id, text='Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        return

    context.chat_data['in_conversation'] = True

    keyboard = [
        [InlineKeyboardButton('Tambahkan User Reguler', callback_data='tambah_reguler')],
        [InlineKeyboardButton('Tambahkan User Admin', callback_data='tambah_admin')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Pilih jenis user.', reply_markup=reply_markup)
    return 1

@authenticate_admin
async def input_tambah_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    button_pressed = query.data
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if button_pressed == 'tambah_reguler':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan masukkan token. Untuk membuat token, calon user reguler tersangkut harus menjalankan perintah /get_token dan memberikan nama lengkapnya dalam tahapan yang dijalankan.')
        return 2

    await context.bot.send_message(chat_id=query.message.chat_id, text='Silahkan masukkan ID pengguna. Untuk membuat token, calon user admin tersangkut harus menjalankan perintah /get_token dan memberikan nama lengkapnya dalam tahapan yang dijalankan.')
    return 3

@authenticate_admin
async def proses_tambah_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    token = update.message.text
    decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
    userid = decoded_token['user_id']
    nama = decoded_token['nama']

     # Cek apakah user dengan user_id tertentu sudah ada di database
    if user_exists(userid):
        await update.message.reply_text('User ID yang dimasukkan telah terdaftar. Proses tambah user dibatalkan.')
        context.chat_data['in_conversation'] = False
        return ConversationHandler.END

    # Jika user belum terdaftar, tambahkan user baru ke database
    add_user(userid, nama)

    await update.message.reply_text(f'Berhasil menambahkan user berikut.\nUser ID: {userid}\nNama: {nama}')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

@authenticate_admin
async def proses_tambah_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    token = update.message.text
    decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
    userid = decoded_token['user_id']
    nama = decoded_token['nama']

    # Cek apakah admin dengan user_id tertentu sudah ada di database
    if user_exists(userid):
        await update.message.reply_text('User ID yang dimasukkan telah terdaftar. Proses tambah admin dibatalkan.')
        context.chat_data['in_conversation'] = False
        return ConversationHandler.END

    # Jika admin belum terdaftar, tambahkan admin baru ke database
    add_admin(userid, nama)

    await update.message.reply_text(f'Berhasil menambahkan admin berikut.\nUser ID: {userid}\nNama: {nama}')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

# Fungsi untuk cek apakah user dengan user_id tertentu sudah ada di database
def user_exists(user_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM allowed_users WHERE username = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None

# # Fungsi untuk cek apakah admin dengan user_id tertentu sudah ada di database
# def admin_exists(user_id):
#     connection = create_mysql_connection()
#     cursor = connection.cursor()
#
#     query = "SELECT * FROM allowed_users WHERE username = %s AND is_admin = 1"
#     cursor.execute(query, (user_id,))
#     result = cursor.fetchone()
#
#     cursor.close()
#     connection.close()
#
#     return result is not None
#
# # Fungsi untuk menambahkan user baru ke database
# def add_user(user_id, nama):
#     connection = create_mysql_connection()
#     cursor = connection.cursor()
#
#     query = "INSERT INTO allowed_users (username, nama, is_admin) VALUES (%s, %s, 0)"
#     cursor.execute(query, (user_id, nama))
#
#     connection.commit()
#     cursor.close()
#     connection.close()

# Fungsi untuk menambahkan admin baru ke database
def add_admin(user_id, nama):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    query = "INSERT INTO allowed_users (username, nama, is_admin) VALUES (%s, %s, 1)"
    cursor.execute(query, (user_id, nama))

    connection.commit()
    cursor.close()
    connection.close()


# HAPUS USER
# Fungsi untuk menghapus user dari database
def delete_user(user_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    # Implementasi penghapusan user dari database
    delete_query = "DELETE FROM allowed_users WHERE username = %s"
    cursor.execute(delete_query, (user_id,))
    connection.commit()

    cursor.close()
    connection.close()

# Fungsi untuk memeriksa apakah user merupakan admin terakhir atau bukan
def is_last_admin(user_id):
    connection = create_mysql_connection()
    cursor = connection.cursor()

    # Implementasi pengecekan apakah user merupakan admin terakhir atau bukan
    admin_count_query = "SELECT COUNT(*) FROM allowed_users WHERE is_admin = 1"
    cursor.execute(admin_count_query)
    admin_count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return admin_count <= 1

#  Fungsi untuk memproses hapus user
@authenticate_admin
async def konfirmasi_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    button_pressed = query.data

    # Ambil nama user dari inputan chat yang masuk
    nama_user = button_pressed[6:].replace('_', ' ')

    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    keyboard = [
        [InlineKeyboardButton('Ya', callback_data='konfirmasi_hapus_ya')],
        [InlineKeyboardButton('Tidak', callback_data='konfirmasi_hapus_tidak')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat_id, text=f'Apakah Anda yakin mau menghapus {nama_user} dari daftar user?', reply_markup=reply_markup)

    # Simpan nama user ke dalam chat data untuk digunakan saat proses hapus user
    context.chat_data['nama_user'] = nama_user

    return 2

# Fungsi untuk proses hapus user
@authenticate_admin
async def proses_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    button_pressed = query.data
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if button_pressed == 'konfirmasi_hapus_ya':
        # Ambil nama user dari chat data
        nama_user = context.chat_data.get('nama_user', '')
        if not nama_user:
            reply = 'Terjadi kesalahan saat memproses penghapusan user.'
        elif is_last_admin(nama_user):
            reply = 'Tidak bisa menghapus user admin terakhir. Silahkan tambahkan admin baru terlebih dahulu. Proses penghapusan user dibatalkan.'
        else:
            # Hapus user dari database
            delete_user(nama_user)
            reply = f'{nama_user} berhasil dihapus dari daftar user.'

        await context.bot.send_message(chat_id=query.message.chat_id, text=reply)
    elif button_pressed == 'konfirmasi_hapus_tidak':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Proses penghapusan user dibatalkan.')

    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

@authenticate_admin
async def konfirmasi_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    button_pressed = query.data
    nama = context.chat_data['nama_user'] = button_pressed[6:].replace('_', ' ')
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    keyboard = [
        [InlineKeyboardButton('Ya', callback_data='konfirmasi_hapus_ya')],
        [InlineKeyboardButton('Tidak', callback_data='konfirmasi_hapus_tidak')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat_id, text=f'Apakah anda yakin mau menghapus {nama} dari daftar user?', reply_markup=reply_markup)
    return 2

@authenticate_admin
async def proses_hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
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
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

### Peroleh Lokasi
@authenticate_user
async def peroleh_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    if context.chat_data.get('in_conversation'):
        await context.bot.send_message(chat_id=query.message.chat_id, text='Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        return

    context.chat_data['in_conversation'] = True
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Masukkan nama item.')
    return 1

# Fungsi untuk memproses peroleh lokasi
@authenticate_user
async def proses_peroleh_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    text = update.message.text
    if len(text) == 8 and text.isalnum():

        # Cek apakah site dengan Site_ID_Tenant tertentu ada di database
        site = get_sites(text.upper())

        if site:
            latitude, longitude = parse_coordinates(site['koordinat'])
            await update.message.reply_text(f"Site_ID_Tenant: {site['site_id']}\n"
                                            f"Tenant: {site['tenant']}\n"
                                            f"Alamat: {site['alamat']}\n"
                                            f"Koordinat Site: {latitude},{longitude}")
            await update.message.reply_location(latitude, longitude)
            context.chat_data['in_conversation'] = False
            return ConversationHandler.END

        await update.message.reply_text('Nama tidak ditemukan. Silahkan masukkan kembali nama item atau keluar dari proses dengan menggunakan fungsi /batal.')
        return 1

    await update.message.reply_text('Format penamaan salah. Silahkan masukkan kembali nama item atau keluar dari proses dengan menggunakan fungsi /batal.')
    return 1

# # Fungsi untuk mendapatkan site berdasarkan Site_ID_Tenant
# def get_site_by_id(site_id):
#     connection = create_mysql_connection()
#     cursor = connection.cursor()
#
#     query = "SELECT Site_ID_Tenant, Tenant, Alamat, Koordinat_Site FROM site_data WHERE Site_ID_Tenant = %s"
#     cursor.execute(query, (site_id,))
#     site = cursor.fetchone()
#
#     cursor.close()
#     connection.close()
#
#     if site:
#         return {
#             'site_id': site[0],
#             'tenant': site[1],
#             'alamat': site[2],
#             'koordinat': site[3]
#         }
#     else:
#         return None

# Fungsi untuk memparse koordinat
def parse_coordinates(coordinates):
    coordinates = coordinates.split(',')
    latitude = float(''.join(filter(lambda c: c.isdigit() or c in ['.', '-'], coordinates[0].strip())))
    longitude = float(''.join(filter(lambda c: c.isdigit() or c in ['.', '-'], coordinates[1].strip())))
    return latitude, longitude


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@authenticate_user
async def peroleh_lokasi_func(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    args = context.args
    if context.chat_data.get('in_conversation'):
        await update.message.reply_text('Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
    elif args:
        argument = args[0]
        if len(argument) == 8 and argument.isalnum():

            if argument.upper() == '20BAT001':
                latitude = -7.88267
                longitude = 112.527
                await update.message.reply_text('Site_ID_Tenant: 20BAT001\nTenant: INDOSAT\nAlamat: Jl. Dewi Sartika Atas 110-104, Temas, Kec. Batu, Kota Batu, Jawa Timur 65315\nKoordinat Site: -7.88267,112.527')
                await update.message.reply_location(latitude, longitude)

            else:
                await update.message.reply_text('Nama tidak ditemukan.')

        else:
            await update.message.reply_text('Format penamaan salah.')
    else:
        await update.message.reply_text('Sintaks: /peroleh_lokasi [nama item]\nContoh: /peroleh_lokasi 20BAT001')

### Peroleh Nama
@authenticate_user
async def peroleh_nama_1(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    if context.chat_data.get('in_conversation'):
        await context.bot.send_message(chat_id=query.message.chat_id, text='Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        return

    context.chat_data['in_conversation'] = True
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Kirimkan Lokasi Pencarian.')
    return 1

@authenticate_user
async def peroleh_nama_2(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    location = update.message.location
    context.chat_data['latitude'] = location.latitude
    context.chat_data['longitude'] = location.longitude
    await update.message.reply_text('Kirimkan radius pencarian dalam satuan meter.')
    return 2

@authenticate_user
async def proses_peroleh_nama(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    dist = update.message.text

    if dist.lstrip('-').replace(',', '').replace('.', '').isnumeric():
        if float(dist) <= 0:
            await update.message.reply_text('Nilai radius harus lebih besar dari 0. Silahkan masukkan kembali nilai radius atau keluar dari proses dengan menggunakan fungsi /batal.')
            context.chat_data['in_conversation'] = False
            return 2
        elif float(dist) < 1:
            await update.message.reply_text(f'Tidak ada item dalam radius {dist} m dari lokasi. Silahkan masukkan kembali nilai radius atau keluar dari proses dengan menggunakan fungsi /batal.')
            context.chat_data['in_conversation'] = False
            return 2

        table = f'Daftar item dalam radius {dist} m dari lokasi adalah:\n'
        table += '```\n'
        table += '| Site_ID_Tenant | Tenant | Alamat |    Koordinat    |\n'
        table += '|:--------------:|:------:|:------:|:---------------:|\n'
        table += '|20BAT001        |INDOSAT |        |[-7.88267,112.527](http://maps.google.com/maps?q=-7.88267,112.527) |\n'
        table += '|20BAT011        |INDOSAT |        |[-7.87102,112.523](http://maps.google.com/maps?q=-7.87102,112.523) |\n'
        table += '```'
        await update.message.reply_text(table, parse_mode=ParseMode.MARKDOWN)
        context.chat_data.clear()
        context.chat_data['in_conversation'] = False
        return ConversationHandler.END

    await update.message.reply_text('Radius harus berupa bilangan cacah atau pecahan desimal > 0 dalam satuan kilometer. Contoh: 1,2. Silahkan masukkan kembali nilai radius atau keluar dari proses dengan menggunakan fungsi /batal.')
    return 2

@authenticate_user
async def peroleh_berkas(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    if context.chat_data.get('in_conversation'):
        await context.bot.send_message(chat_id=query.message.chat_id, text='Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        return

    context.chat_data['in_conversation'] = True
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Masukkan nama berkas.')
    return 1

@authenticate_user
async def proses_peroleh_berkas(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    text = update.message.text
    await update.message.reply_text('[PLACEHOLDER BERKAS]')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    if context.chat_data['in_conversation']:
        context.chat_data['in_conversation'] = False
        await update.message.reply_text('Proses dibatalkan.')
        return ConversationHandler.END

    await update.message.reply_text('Tidak ada proses yang sedang berjalan.')

@authenticate_user
async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    await context.bot.send_message(chat_id=query.message.chat_id, text='''Fungsi Dasar
/start
Memulai percakapan. Percakapan tidak dapat dimulai apabila sebuah proses sedang berjalan. Lihat /batal.
/batal
Mengakhiri proses. Mengakhiri proses yang sedang berjalan dan membuka kemungkinan untuk memulai kembali percakapan.
/bantuan
Melihat bantuan penggunaan (teks ini).
/get_token
Peroleh token untuk keperluan autentikasi. Penjalanan fungsi ini tidak memerlukan autentikasi.

Arahan Menu
Menu Utama: Berisi berbagai pilihan untuk membuka submenu.
Input Data: Menjalankan proses untuk memasukkan data ke dalam basis data.
Peroleh Lokasi Item: Menjalankan proses untuk memperoleh lokasi item berdasarkan nama item.
Peroleh Nama Item: Menjalankan proses untuk memperoleh nama-nama item berdasarkan lokasi.
Peroleh File Set: Menjalankan proses untuk memperoleh berkas-berkas berdasarkan nama.''')

async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    await update.message.reply_text(f"Mohon kirimkan nama lengkap anda.")
    return 1

async def get_token_process(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
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
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END
# # Function that creates a message containing a list of all the oders
# def create_message_select_query(ans):
#     text = ''
#     for i in ans:
#         id = i[0]
#         product = i[1]
#         quantity = i[2]
#         creation_date = i[3]
#         text += '<b>'+ str(id) +'</b> | ' + '<b>'+ str(product) +'</b> | ' + '<b>'+ str(quantity)+'</b> | ' + '<b>'+ str(creation_date)+'</b>\n'
#     message = '<b>Received 📖 </b> Information about orders:\n\n'+text
#     return message
#
# ### SELECT COMMAND
# @client.on(events.NewMessage(pattern='(?i)/select'))
# async def select(event):
#     try:
#         # Get the sender of the message
#         sender = await event.get_sender()
#         SENDER = sender.id
#         # Execute the query and get all (*) the oders
#         crsr.execute('SELECT * FROM orders')
#         res = crsr.fetchall() # fetch all the results
#         # If there is at least 1 row selected, print a message with the list of all the oders
#         # The message is created using the function defined above
#         if(res):
#             text = create_message_select_query(res)
#             await client.send_message(SENDER, text, parse_mode='html')
#         # Otherwhise, print a default text
#         else:
#             text = 'No orders found inside the database.'
#             await client.send_message(SENDER, text, parse_mode='html')
#
#     except Exception as e:
#         print(e)
#         await client.send_message(SENDER, 'Something Wrong happened... Check your code!', parse_mode='html')
#         return
#
#
#
# ### UPDATE COMMAND
# @client.on(events.NewMessage(pattern='(?i)/update'))
# async def update(event):
#     try:
#         # Get the sender
#         sender = await event.get_sender()
#         SENDER = sender.id
#
#         # Get the text of the user AFTER the /update command and convert it to a list (we are splitting by the SPACE ' ' simbol)
#         list_of_words = event.message.text.split(' ')
#         id = int(list_of_words[1]) # second (1) item is the id
#         new_product = list_of_words[2] # third (2) item is the product
#         new_quantity = list_of_words[3] # fourth (3) item is the quantity
#         dt_string = datetime.now().strftime('%d/%m/%Y') # We create the new date
#
#         # create the tuple with all the params interted by the user
#         params = (id, new_product, new_quantity, dt_string, id)
#
#         # Create the UPDATE query, we are updating the product with a specific id so we must put the WHERE clause
#         sql_command='UPDATE orders SET id=%s, product=%s, quantity=%s, LAST_EDIT=%s WHERE id =%s'
#         crsr.execute(sql_command, params) # Execute the query
#         conn.commit() # Commit the changes
#
#         # If at least 1 row is affected by the query we send a specific message
#         if crsr.rowcount < 1:
#             text = 'Order with id {} is not present'.format(id)
#             await client.send_message(SENDER, text, parse_mode='html')
#         else:
#             text = 'Order with id {} correctly updated'.format(id)
#             await client.send_message(SENDER, text, parse_mode='html')
#
#     except Exception as e:
#         print(e)
#         await client.send_message(SENDER, 'Something Wrong happened... Check your code!', parse_mode='html')
#         return
#
#
#
# @client.on(events.NewMessage(pattern='(?i)/delete'))
# async def delete(event):
#     try:
#         # Get the sender
#         sender = await event.get_sender()
#         SENDER = sender.id
#
#         #/ delete 1
#
#         # get list of words inserted by the user
#         list_of_words = event.message.text.split(' ')
#         id = list_of_words[1] # The second (1) element is the id
#
#         # Crete the DELETE query passing the id as a parameter
#         sql_command = 'DELETE FROM orders WHERE id = (%s);'
#
#         # ans here will be the number of rows affected by the delete
#         ans = crsr.execute(sql_command, (id,))
#         conn.commit()
#
#         # If at least 1 row is affected by the query we send a specific message
#         if ans < 1:
#             text = 'Order with id {} is not present'.format(id)
#             await client.send_message(SENDER, text, parse_mode='html')
#         else:
#             text = 'Order with id {} was correctly deleted'.format(id)
#             await client.send_message(SENDER, text, parse_mode='html')
#
#     except Exception as e:
#         print(e)
#         await client.send_message(SENDER, 'Something Wrong happened... Check your code!', parse_mode='html')
#         return
#
#
#
# # Create database function
# def create_database(query):
#     try:
#         crsr_mysql.execute(query)
#         print('Database created successfully')
#     except Exception as e:
#         print(f'WARNING: '{e}'')
#
##### MAIN
if __name__ == '__main__':
    main()
#     try:
#         print('Initializing Database...')
#         conn_mysql = MySQLdb.connect( host=HOSTNAME, user=USERNAME, passwd=PASSWORD )
#         crsr_mysql = conn_mysql.cursor()
#
#         query = 'CREATE DATABASE '+str(DATABASE)
#         create_database(query)
#         conn = MySQLdb.connect( host=HOSTNAME, user=USERNAME, passwd=PASSWORD, db=DATABASE )
#         crsr = conn.cursor()
#
#         # Command that creates the 'oders' table
#         sql_command = '''CREATE TABLE IF NOT EXISTS orders (
#             id INTEGER PRIMARY KEY AUTO_INCREMENT,
#             product VARCHAR(200),
#             quantity INT(10),
#             LAST_EDIT VARCHAR(100));'''
#
#         crsr.execute(sql_command)
#         print('All tables are ready')
#
#         print('Bot Started...')
#         client.run_until_disconnected()
#
#     except Exception as error:
#         print('Cause: {}'.format(error))
