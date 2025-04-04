# I was using 3.12 throughout the tutorial so use 3.12 instead
FROM python:3.12-slim

RUN python -m pip install uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT="/venv"

RUN uv venv --python-preference system
ENV PATH="/venv/bin:$PATH"

COPY pyproject.toml /pyproject.toml
COPY uv.lock /uv.lock
RUN uv sync  --frozen --no-dev --no-install-project

COPY src /src

WORKDIR /src

RUN python manage.py collectstatic

ENV DJANGO_DEBUG_FALSE=1
CMD ["gunicorn", "--bind", ":8888", "superlists.wsgi:application"]
