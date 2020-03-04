FROM python:3.7-alpine

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY app /app
WORKDIR /

#CMD ["gunicorn", "-w 4", "app:app"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
