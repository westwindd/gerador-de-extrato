FROM python:3.11-alpine

RUN apk add --no-cache \
    build-base jpeg-dev zlib-dev libffi-dev openssl-dev \
    postgresql-dev fontconfig ttf-dejavu

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py logo.png ./

ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
