FROM python:3.14 

WORKDIR /code

COPY ./requirements.txt /code/

RUN pip install --no-cache-dir -r /code/requirements.txt 

COPY . /code/

EXPOSE 8080

RUN useradd app
USER app

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8080"]