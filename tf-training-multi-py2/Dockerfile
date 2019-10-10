FROM mciesielintel/tensorflow:1.12.0-py3

WORKDIR /app


ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD main.py .

ADD training.py .
