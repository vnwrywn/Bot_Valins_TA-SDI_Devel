FROM python:3.11.4-slim
COPY /app /app
COPY requirements.txt .
RUN adduser --disabled-password botuser
RUN chmod 755 /app
RUN mkdir /files && chmod 744 /files
USER botuser
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /tmp
ENV APP_TMP_DATA=/tmp
CMD python /app/script_bot.py
