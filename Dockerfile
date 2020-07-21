FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /backend_aaiss
WORKDIR /backend_aaiss
COPY requirements.txt /backend_aaiss/
RUN pip3 install -r requirements.txt
COPY . /backend_aaiss/