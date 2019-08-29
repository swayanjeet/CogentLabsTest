FROM python:3

RUN pip install flask
RUN pip install redis
RUN pip install requests

ADD . /app
WORKDIR /app

CMD ["python"]
