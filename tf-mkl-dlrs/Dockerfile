FROM nauta/tensorflow-dlrs-mkl

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD main.py .

ADD training.py .
