FROM python:3.9-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt && pip install pyinstaller
RUN pyinstaller -D tabugen


# CMD ["python manage.py runserver 0.0.0.0:8000"]
