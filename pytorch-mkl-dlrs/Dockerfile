FROM nauta/pytorch-dlrs-mkl

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD training.py .
