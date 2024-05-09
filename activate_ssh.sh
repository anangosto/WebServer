#!/bin/bash

# Iniciar el servicio SSH
service ssh start

# Ejecutar el entrypoint original
/usr/local/bin/docker-entrypoint.sh apache2-foreground