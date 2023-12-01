FROM python:3.11

COPY . /docu

WORKDIR /docu

RUN pip install -r requirements.txt && py models/models.py

RUN uvicorn main:app --host 0.0.0.0 --port 8000

EXPOSE 8000