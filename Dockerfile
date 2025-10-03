FROM playcourt/python:3.12

# Set build arguments
ARG ARGS_APP_DIR="."
ARG ARGS_FLASK_NAME="app:app"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/usr/src/app/${ARGS_APP_DIR} \
    FLASK_APP=${ARGS_FLASK_NAME} \
    GUNICORN_WORKER=3 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create a virtual environment without pip and install pip manually
RUN python -m venv /opt/venv --without-pip && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    /opt/venv/bin/python get-pip.py && \
    rm get-pip.py

# Activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements file
COPY ${ARGS_APP_DIR}/requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt gunicorn gevent

# Copy application code
COPY ${ARGS_APP_DIR}/ ${ARGS_APP_DIR}/

# Expose application port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "gunicorn ${FLASK_APP} --worker-class gevent --workers ${GUNICORN_WORKER} --preload --bind 0.0.0.0:8080 --pythonpath='${PYTHONPATH}' --chdir ${PYTHONPATH} --log-level DEBUG"]
