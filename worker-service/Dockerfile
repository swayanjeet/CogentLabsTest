FROM python:3

RUN pip install redis
RUN pip install Pillow

ADD . /app
WORKDIR /app

CMD [ "python", "app.py" ]
