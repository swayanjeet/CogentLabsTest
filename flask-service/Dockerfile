FROM python:3

RUN pip install flask
RUN pip install redis

ADD . /app
WORKDIR /app

EXPOSE 8085
CMD [ "python", "app.py" ]
