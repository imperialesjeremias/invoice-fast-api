FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./main.py /app/main.py


# Copia el archivo requirements.txt al contenedor
COPY requirements.txt /requirements.txt

# Instala las dependencias de la aplicación
RUN pip install -r /requirements.txt

# Expone el puerto 80 para que la aplicación sea accesible desde fuera del contenedor
EXPOSE 80

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]