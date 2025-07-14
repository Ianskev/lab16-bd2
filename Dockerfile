FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Command to run seed data script and then start the app
CMD python -m scripts.seed_data && python run.py 