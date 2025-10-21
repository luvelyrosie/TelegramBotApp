FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8000

CMD ["daphne", "-p", "8000", "core.asgi:application"]