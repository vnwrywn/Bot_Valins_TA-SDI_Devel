set REINITIALIZE=0
set NOCACHE=0

if %1%==sn (
    set REINITIALIZE=1
    set SKIP=1
)

if %1%==ns (
    set REINITIALIZE=1
    set SKIP=1
)

if %1%==n set NOCACHE=1
if %1%==s set SKIP=1

if %SKIP%==1 (
    docker volume create mysql_data
    docker swarm init
    docker network create --driver overlay bot_telegram_devel
    python3 create_password.py | sudo docker secret create db_root_password -
    python3 create_password.py | sudo docker secret create db_telebot_password -
)

docker-compose -f docker-compose.yml down -v
if %NOCACHE%==true (
        docker-compose build --no-cache
    )else (
        docker-compose build
)

