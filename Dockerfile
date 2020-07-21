FROM python:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/
ENV APP_HOME=/backend_aaiss
RUN mkdir /backend_aaiss
WORKDIR /backend_aaiss
COPY requirements.txt /backend_aaiss/
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /backend_aaiss/