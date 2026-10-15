FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o PYTHONPATH para que os imports internos (cogs, services, database, utils)
# sejam resolvidos a partir de src/, independentemente de onde o container for rodado
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["python", "src/bot.py"]
