# pull official base image
FROM python:3.13-slim

# set work directory
WORKDIR /compose

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev netcat-traditional \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copiamos el proyecto
COPY . /compose

# Dar permisos al entrypoint
RUN chmod +x /compose/entrypoint.sh

# Puerto que expone Gunicorn
EXPOSE 8000
CMD ["/compose/entrypoint.sh"]
