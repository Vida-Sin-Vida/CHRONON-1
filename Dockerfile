FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Upgrade pip and install
RUN pip install --upgrade pip && pip install -e ".[dev]"

CMD ["chronon1", "reproduce", "--config", "configs/toy.yml"]
