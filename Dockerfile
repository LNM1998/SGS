# Imagen base oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el contenido del proyecto al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto por donde escucha Waitress
EXPOSE 8080

# Comando para ejecutar la app usando Waitress
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "app2:app"]
