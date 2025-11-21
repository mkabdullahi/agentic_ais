# Minimal production-style Dockerfile
FROM python:3.11-slim

# avoid running as root
RUN useradd --create-home appuser
WORKDIR /home/appuser/app
COPY --chown=appuser:appuser requirements.txt ./

# Install dependencies (keep cache minimal)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=appuser:appuser . .

USER appuser
ENV PYTHONUNBUFFERED=1

# Do not include .env in image — mount at runtime or use secret management
# Default command runs the inventory example; override with docker run <image> <cmd>
CMD ["python", "-m", "agents.inventory_optimization_agent"]