set REINITIALIZE=false
set NOCACHE=false

if %1%==rn OR %1%==nr (
    set REINITIALIZE=true
    set NOCACHE=true
)

if %1%==n (
    set NOCACHE=true
)

if %1%==r (
    set REINITIALIZE=true
)

if NOT EXIST initialized.sql OR %REINITIALIZE%=true(
    echo "Membuat berkas inisialisasi basis data..." > initialized.sql
    echo "-- TIDAK UNTUK DISUNTING SECARA MANUAL" >> initialized.sql
    echo "-- Naskah ini digenerasi oleh deploy.sh atau deploy.bat." >> initialized.sql
    echo "-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data." >> initialized.sql
    echo "" >> initialized.sql
    echo "" >> initialized.sql
    type initialization.sql >> initialized.sql
) else (
    echo "Basis data TIDAK akan diinisialisasi."
    echo "-- TIDAK UNTUK DISUNTING SECARA MANUAL" > initialized.sql
    echo "-- Basis data telah terinisialisasi." >> initialized.sql
    echo "-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data dan jalankan naskah build.sh atau build.bat dengan opsi -r untuk menginisialisasi ulang basis data." >> initialized.sql
)

docker-compose -f docker-compose.yml down -v
if %NOCACHE%=true (
        docker-compose build --no-cache
    )else (
        docker-compose build
)

