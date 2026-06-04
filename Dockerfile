FROM python:3.11-slim

WORKDIR /app

# Reflex requiere Node.js para compilar la interfaz de Next.js
RUN apt-get update && apt-get install -y curl unzip && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente estructurado
COPY . .

EXPOSE 3000 8000

# El host 0.0.0.0 es crucial para que Docker exponga los puertos hacia tu Windows
CMD ["reflex", "run", "--backend-host", "0.0.0.0"]