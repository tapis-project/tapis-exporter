FROM python:3.7

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY exporter.py /

CMD ["python", "/exporter.py"]
