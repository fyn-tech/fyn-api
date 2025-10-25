FROM python:3.12-slim

ENV DEBUG=True \
ENVIRONMENT=Debug

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --upgrade pip && \
    pip install -e .

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]