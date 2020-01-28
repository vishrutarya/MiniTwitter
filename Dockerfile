FROM python:3.7

RUN useradd minitwitter

WORKDIR /home/minitwitter

COPY requirements.txt requirements.txt
RUN python -m venv env
RUN env/bin/pip install --upgrade pip
RUN env/bin/pip install -r requirements.txt
RUN env/bin/pip install gunicorn pymysql[rsa]

COPY app app
COPY migrations migrations
COPY minitwitter.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP minitwitter.py

RUN chown -R minitwitter:minitwitter ./
USER minitwitter

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]