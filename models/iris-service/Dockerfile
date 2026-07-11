FROM python:3.11-slim

WORKDIR /app

# Copy requirements first and install — this layer only rebuilds when
# requirements.txt changes, not on every code edit. That's the caching win.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code + trained artifact copied last, since these change most often.
COPY app.py .
COPY model.pkl .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
