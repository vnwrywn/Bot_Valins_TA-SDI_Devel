FROM python:3.12.0b1-slim-bullseye
COPY . .
RUN apt-get update
RUN apt-get install gcc -y
RUN apt-get install default-libmysqlclient-dev -y
RUN pip3 install --no-cache-dir -r requirements.txt
CMD python script_mysql.py
