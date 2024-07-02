FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt && pip install pyinstaller
RUN pyinstaller -F ./tabugen/__main__.py -c -n tabugen


FROM builder
COPY --from=builder /app/dist/tabugen ./
CMD ["./tabugen --help"]
