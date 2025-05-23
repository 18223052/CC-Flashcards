FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn sqlmodel jinja2 pyotp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "52052"]

