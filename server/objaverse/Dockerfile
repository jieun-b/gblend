FROM python:3.11-slim

WORKDIR /home

COPY requirements.txt /home/requirements.txt
RUN pip install --no-cache-dir -r /home/requirements.txt

COPY app.py /home/app.py

EXPOSE 8002
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
