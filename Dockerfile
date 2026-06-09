FROM python:3.10-slim

# ★【英数記号の崩れ対策】英数字が綺麗に表示される「fonts-liberation」も一緒にロボットに入れます
RUN apt-get update && apt-get install -y \
    poppler-utils \
    poppler-data \
    fonts-noto-cjk \
    fonts-liberation

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "main.py"]
