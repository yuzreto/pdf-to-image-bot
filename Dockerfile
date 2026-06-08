FROM python:3.10-slim

# ★【文字化け対策】poppler-data と、Googleの日本語フォント（fonts-noto-cjk）をロボットに入れます
RUN apt-get update && apt-get install -y poppler-utils poppler-data fonts-noto-cjk

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "main.py"]
