FROM docker.io/python:3.11-slim-bookworm

RUN pip install poetry~=1.7.0

WORKDIR /usr/src/nomsable/
COPY . .

RUN python -m venv .venv
RUN poetry install
RUN poetry run pip install gunicorn~=21.2.0

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "scripts/docker-entrypoint.sh"]
