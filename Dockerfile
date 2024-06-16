FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install -r requirements.txt

COPY . /app/

CMD ["sh", "-c", "python3 manage.py makemigrations && python manage.py migrate"]
