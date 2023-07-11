###TODO!!!
# Fungsi tambah user (Token)

### Importing necessary libraries

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
config.read('config.ini')

API_ID = config.get('default','api_id')
API_HASH = config.get('default','api_hash')
BOT_TOKEN = config.get('default','bot_token')
session_name = 'sessions/Bot'

# # Read values for MySQLdb
# HOSTNAME = config.get('default','hostname')
# USERNAME = config.get('default','username')
# PASSWORD = config.get('default','password')
# DATABASE = config.get('default','database')

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

def is_authenticated(user_id: int):
    if user_id == 1139987918:
        return [True, True]
    elif user_id == 6119375027:
        return [True, False]

    return [False, False]

### Middleware functions for user authentication
def authenticate_user(func):
    @wraps(func)
    def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
        # ![Query Autentikasi User & Admin]
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
    # ![Query Input Satuan]
    await update.message.reply_text('Input satuan berhasil.')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

@authenticate_admin
async def input_pangkas(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    file = context.bot.get_file(update.message.document.file_id)
    # ![Query Input Truncate]
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

    if userid == '1139987918': #[Query Cari User Berdasarkan ID]
        await update.message.reply_text('User ID yang dimasukkan telah terdaftar. Proses tambah user dibatalkan.')
        context.chat_data['in_conversation'] = False
        return ConversationHandler.END

    # ![Query Tambah User]
    await update.message.reply_text(f'Berhasil menambahkan user berikut.\nUser ID: {userid}\nNama: {nama}')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

@authenticate_admin
async def proses_tambah_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    token = update.message.text
    decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
    userid = decoded_token['user_id']
    nama = decoded_token['nama']

    if userid == '1139987918': #[Query Cari User Berdasarkan ID]
        await update.message.reply_text('User ID yang dimasukkan telah terdaftar. Proses tambah user dibatalkan.')
        context.chat_data['in_conversation'] = False
        return ConversationHandler.END

    # ![Query Tambah User]
    await update.message.reply_text(f'Berhasil menambahkan user berikut.\nUser ID: {userid}\nNama: {nama}')
    context.chat_data['in_conversation'] = False
    return ConversationHandler.END

### Hapus User
@authenticate_admin
async def hapus_user(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    query = update.callback_query
    await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None)

    if context.chat_data.get('in_conversation'):
        await context.bot.send_message(chat_id=query.message.chat_id, text='Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
        return

    context.chat_data['in_conversation'] = True

    # ![Query Nama & ID User]
    test_list = ['M. Ivan Wiryawan', 'User 1', 'User 2', 'User 3', 'User 4', 'User 5', 'User 6']
    keyboard = [[InlineKeyboardButton(name, callback_data = 'hapus_' + name.replace(' ', '_'))] for name in test_list]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat_id, text='Pilih user yang mau dihapus, atau keluar dari proses dengan menggunakan fungsi /batal.', reply_markup=reply_markup)
    return 1

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
        if context.chat_data['nama_user'] == 'M. Ivan Wiryawan': # ![Query Jumlah Admin]
            reply = 'Tidak bisa menghapuskan user admin terakhir, silahkan tambahkan admin baru terlebih dahulu. Proses penghapusan user dibatalkan.'
        else:
            # ![Query Delete User]
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

@authenticate_user
async def proses_peroleh_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    text = update.message.text
    if len(text) == 8 and text.isalnum():

        if text.upper() == '20BAT001':
            # ![Query Data Site]
            latitude = -7.88267
            longitude = 112.527
            await update.message.reply_text('Site_ID_Tenant: 20BAT001\nTenant: INDOSAT\nAlamat: Jl. Dewi Sartika Atas 110-104, Temas, Kec. Batu, Kota Batu, Jawa Timur 65315\nKoordinat Site: -7.88267,112.527')
            await update.message.reply_location(latitude, longitude)
            context.chat_data['in_conversation'] = False
            return ConversationHandler.END

        await update.message.reply_text('Nama tidak ditemukan. Silahkan masukkan kembali nama item atau keluar dari proses dengan menggunakan fungsi /batal.')
        return 1

    await update.message.reply_text('Format penamaan salah. Silahkan masukkan kembali nama item atau keluar dari proses dengan menggunakan fungsi /batal.')
    return 1

@authenticate_user
async def peroleh_lokasi_func(update: Update, context: ContextTypes.DEFAULT_TYPE, auth_status=None):
    args = context.args
    if context.chat_data.get('in_conversation'):
        await update.message.reply_text('Mohon akhiri percakapan terlebih dahulu dengan menjalankan fungsi /batal.')
    elif args:
        argument = args[0]
        if len(argument) == 8 and argument.isalnum():

            if argument.upper() == '20BAT001':
                # ![Query Data Site]
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
    # ![Query Berdasarkan Jarak & Radius]

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

##### MAIN
if __name__ == '__main__':
    main()
