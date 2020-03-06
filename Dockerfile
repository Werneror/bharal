FROM python:3.6

RUN mkdir -p /opt/bharal
COPY . /opt/bharal
RUN pip install -r /opt/bharal/requirements.txt
WORKDIR /opt/bharal
EXPOSE 4430

CMD ["python","bharal.py"]
