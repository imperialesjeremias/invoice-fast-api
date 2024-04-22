# Usa la imagen base
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia todo el contenido de tu directorio local al contenedor en /app
COPY . .

# Actualiza los paquetes e instala libgl1-mesa-glx para solucionar el problema con libGL.so.1
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000 para que la aplicación sea accesible desde fuera del contenedor
EXPOSE 8000

# Comando para iniciar la aplicación con auto-reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
