FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5051

CMD ["gunicorn", "--bind", "0.0.0.0:5051", "--workers", "4", "run:app"]