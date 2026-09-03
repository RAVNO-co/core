FROM python-3.14-slim

WORKDIR /code

COPY ./poetry.lock ./pyproject.toml /code/

RUN pip install poetry

COPY . .

#TODO
CMD [ "poetry", "run", "python", "-m", "uuid"]
