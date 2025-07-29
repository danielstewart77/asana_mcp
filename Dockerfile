# Use full Ubuntu image for package compatibility
FROM ubuntu:latest

# Set working directory
WORKDIR /usr/src/app

# Install Python and system dependencies
RUN apt update && apt install -y \
    python3 python3-pip python3-venv python3-dev gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Create global python alias
RUN ln -s /usr/bin/python3 /usr/bin/python

# Ensure Python is available
RUN python3 --version

# Create and activate a virtual environment
RUN python3 -m venv venv

# Upgrade pip inside the virtual environment
RUN venv/bin/pip install --upgrade pip

# Copy only the requirements file first (to cache dependencies)
COPY requirements.txt .

# Manually install agent_tooling first (to avoid issues)
RUN venv/bin/pip install --no-cache-dir --force-reinstall agent_tooling

# Install all other dependencies
RUN venv/bin/pip install --no-cache-dir --force-reinstall -r requirements.txt

# Specifically install mcpo to ensure it's available
RUN venv/bin/pip install --no-cache-dir mcpo

# Verify installations
RUN echo "=== Checking mcpo installation ===" && \
    venv/bin/pip list | grep mcpo && \
    ls -la venv/bin/ | grep mcpo && \
    echo "=== mcpo verification complete ==="

# Copy the rest of the application after dependencies are installed
COPY . .

# Expose the application port
EXPOSE 7777

# Run the application with the virtual environment's Python
CMD ["venv/bin/python3", "mcp_server.py"]
