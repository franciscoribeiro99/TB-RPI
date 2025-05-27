FROM dtcooper/raspberrypi-os:python3.9

# Install dependencies (system)
RUN apt update && apt install -y \
    python3-pip \
    curl \
    libopencv-dev \
    python3-opencv \
    v4l-utils \
    libcap-dev \
    && apt clean
    

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"


# Install Python dependencies using uv
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN python -m venv .venv && \
    uv pip install -r requirements.txt

# Activate virtualenv by default
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the rest of your code
COPY . .

# Default command
CMD ["python3", "main.py"]
