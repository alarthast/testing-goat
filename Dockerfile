# I was using 3.12 throughout the tutorial so use 3.12 instead
FROM python:3.12-slim

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install --no-cache-dir "django<6" gunicorn whitenoise

COPY src /src

WORKDIR /src

CMD ["gunicorn", "--bind", ":8888", "superlists.wsgi:application"]
