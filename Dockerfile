FROM python:3.12-alpine

WORKDIR /scheduler-script

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
