FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn sqlmodel jinja2 pyotp

#RUN python -c "from main import create_db_and_tables; create_db_and_tables()"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "17787"]
