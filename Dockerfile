# All Dockerfiles should start from this base image
# Provide the TAG environment variable, or replace with the image version required
# I was using 3.12 throughout the tutorial so use 3.12 instead
FROM python:3.12-slim

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install --no-cache-dir "django<6"

COPY src /src

WORKDIR /src

CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]
