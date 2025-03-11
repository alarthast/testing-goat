# I was using 3.12 throughout the tutorial so use 3.12 instead
FROM python:3.12-slim

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.prod.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY src /src

WORKDIR /src

RUN python manage.py collectstatic

ENV DJANGO_DEBUG_FALSE=1
CMD ["gunicorn", "--bind", ":8888", "superlists.wsgi:application"]
