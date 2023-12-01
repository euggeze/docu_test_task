FROM python:3.11

COPY . /docu

WORKDIR /docu

RUN pip install -r requirements.txt 
RUN python models/models.py

EXPOSE 8000
