set REINITIALIZE=0
set NOCACHE=0

if %1%==rn (
    set REINITIALIZE=1
    set NOCACHE=1
)

if %1%==nr (
    set REINITIALIZE=1
    set NOCACHE=1
)

if %1%==n set NOCACHE=1
if %1%==r set REINITIALIZE=1

set res=0
if not exist initialized.sql set res=1
if %REINITIALIZE%==1 set res=1
if %res%==1 (
    echo Membuat berkas inisialisasi basis data...
    echo -- TIDAK UNTUK DISUNTING SECARA MANUAL > initialized.sql
    echo -- Naskah ini digenerasi oleh deploy.sh atau deploy.bat. >> initialized.sql
    echo -- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data. >> initialized.sql
    echo. >> initialized.sql
    echo. >> initialized.sql
    type initialization.sql >> initialized.sql
) else (
    echo Basis data TIDAK akan diinisialisasi.
    echo -- TIDAK UNTUK DISUNTING SECARA MANUAL > initialized.sql
    echo -- Basis data telah terinisialisasi. >> initialized.sql
    echo -- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data dan jalankan naskah build.sh atau build.bat dengan opsi -r untuk menginisialisasi ulang basis data. >> initialized.sql
)

docker-compose -f docker-compose.yml down -v
if %NOCACHE%==true (
        docker-compose build --no-cache
    )else (
        docker-compose build
)

