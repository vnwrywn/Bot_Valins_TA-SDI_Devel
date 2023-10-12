set INITIALIZE=0
set NOCACHE=0

if %1%==in (
    set INITIALIZE=1
    set NOCACHE=1
)

if %1%==ni (
    set INITIALIZE=1
    set NOCACHE=1
)

if %1%==n set INITIALIZE=1
if %1%==i set NOCACHE=1


if %INITIALIZE%==1 (
    docker-compose -f docker-compose.yml down -v
    docker volume rm mysql_data
    docker volume create mysql_data
    Echo Basis data belum terinisialisasi. > init_status.txt
)

if %NOCACHE%==1 (
        docker-compose build --no-cache
)else (
        docker-compose build
)

