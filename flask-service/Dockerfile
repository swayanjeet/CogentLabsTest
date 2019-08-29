FROM python:3

RUN pip install flask

ADD . /app
WORKDIR /app

EXPOSE 8085
CMD [ "python", "app.py" ]
ENTRYPOINT python "app.py"
