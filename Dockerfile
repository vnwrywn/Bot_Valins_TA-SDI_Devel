FROM python:3.11.4-slim
COPY /app /app
COPY requirements.txt .
RUN adduser --disabled-password botuser
RUN chmod 755 /app && chmod 766 /app/sessions
USER botuser
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
ENV APP_TMP_DATA=/tmp
CMD python script_bot.py
