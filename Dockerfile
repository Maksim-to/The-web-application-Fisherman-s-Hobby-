FROM python:3.11-slim

WORKDIR /app

# Устанавливаем пакеты по одному с повторными попытками
RUN pip install --no-cache-dir --timeout 100 --retries 5 Flask==3.1.0 && \
    pip install --no-cache-dir --timeout 100 --retries 5 Flask-SQLAlchemy==3.1.1 && \
    pip install --no-cache-dir --timeout 100 --retries 5 Flask-Login==0.6.3 && \
    pip install --no-cache-dir --timeout 100 --retries 5 Flask-WTF==1.2.1 && \
    pip install --no-cache-dir --timeout 100 --retries 5 Werkzeug==3.1.3 && \
    pip install --no-cache-dir --timeout 100 --retries 5 requests==2.31.0 && \
    pip install --no-cache-dir --timeout 100 --retries 5 python-dotenv==1.0.0

RUN pip install --no-cache-dir --timeout 100 --retries 5 shapely==2.0.4

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=development
ENV SECRET_KEY=change-me-in-production-12345

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]