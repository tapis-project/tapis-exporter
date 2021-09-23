FROM python:3.7-alpine

COPY requirements.txt /

RUN apk add --no-cache gcc
RUN pip install -r /requirements.txt

COPY exporter.py /

CMD ["python", "/exporter.py"]
