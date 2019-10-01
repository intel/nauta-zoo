FROM nauta/openvino-ms

WORKDIR /app
ADD training.py .

ADD ovms_nauta.sh /bin/ovms_nauta
RUN chmod +x /bin/ovms_nauta

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
