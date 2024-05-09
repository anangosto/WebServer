# Usa la imagen base de WordPress
FROM wordpress:php8.3-apache

# Actualizar paquetes e instalar ssh y dos2unix
RUN apt-get update && \
    apt-get install -y ssh dos2unix default-mysql-client

# Crear usuario anainf con contraseña anainf
RUN useradd -ms /bin/bash -p $(openssl passwd -1 anainf) anainf

# Copiar el script de activación de SSH desde tu máquina local al contenedor
COPY activate_ssh.sh /usr/local/bin/
RUN dos2unix /usr/local/bin/activate_ssh.sh

# Dar permisos de ejecución al script de activación de SSH
RUN chmod +x /usr/local/bin/activate_ssh.sh

# Establecer el script como entrypoint
ENTRYPOINT ["activate_ssh.sh"]