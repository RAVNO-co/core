FROM python:3.14-slim

ARG POETRY_VERSION="2.4.1"

ARG UID=1000
ARG GID=1000

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1

ENV PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_ROOT_USER_ACTION=ignore

ENV POETRY_VERSION=2.4.1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

WORKDIR /code

# Add non-root user
RUN groupadd -g "${GID}" -r core && \
    useradd -d '/code' -g core -l -r -u "${UID}" core && \
    chown core:core -R '/code'

RUN pip install poetry==${POETRY_VERSION}
COPY --chown=core:core ./poetry.lock ./pyproject.toml /code/
RUN poetry install --without=dev

COPY . /code/

# Set non-root user
USER core

#TODO
CMD [ "poetry", "run", "python", "-m", "uuid"]
