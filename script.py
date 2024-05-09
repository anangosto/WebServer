import requests
import re
import time
import paramiko
import mysql.connector
from bs4 import BeautifulSoup

# URLs y credenciales
wordpress_url = "http://wordpress"

# Función para obtener la versión de Apache
def obtener_version_apache():
    try:
        response = requests.head(wordpress_url)
        version = response.headers.get('Server', 'Encabezado no encontrado')

        # Usar expresión regular para capturar solo el número de versión
        version_match = re.search(r"Apache/(\d+\.\d+\.\d+)", version)
        if version_match:
            version = version_match.group(1)
            print(f"Versión Apache: {version}")
            return version
        else:
            print("No se pudo extraer la versión de Apache.")
            return None

    except Exception as e:
        print(f"Ocurrió un error al intentar obtener la versión: {e}")
        return None

# Función para obtener la versión de WordPress a través de SSH
def obtener_version_wordpress(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=user, password=password)
        stdin, stdout, stderr = client.exec_command("cat /var/www/html/wp-includes/version.php")
        output = stdout.read().decode('utf-8')
        client.close()

        version_match = re.search(r"\$wp_version\s*=\s*'([\d.]+)'", output)
        if version_match:
            version = version_match.group(1)
            print(f"Versión de WordPress: {version}")
            return version
        else:
            print("No se encontró la versión de WordPress en version.php.")
            return None
    except Exception as e:
        print(f"Error al conectar via SSH: {e}")
        return None

# Función para obtener la versión de MySQL
def obtener_version_mysql(host, user, password, database=None):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"Versión de MySQL: {version[0]}")
        cursor.close()
        connection.close()
        return version[0]
    except mysql.connector.Error as err:
        print(f"Error al conectar con MySQL: {err}")
        return None

def buscar_vulnerabilidades_mitre(servicio, version):

    query = f"{servicio} {version}"
    url = "https://cve.mitre.org/cgi-bin/cvekey.cgi"
    params = {'keyword': query}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        cve_table = soup.find('table', {'id': 'TableWithRules'})

        if cve_table:
            rows = cve_table.find_all('tr')[1:]  # Omitir la primera fila (cabecera)
            for row in rows:
                cve_id = row.find('a').text.strip()
                description = row.find_all('td')[1].text.strip()
                print(f"\nID: {cve_id}\nDescripción: {description}\n")
        else:
            print(f"No se encontraron vulnerabilidades para {servicio} {version} en Mitre.")
    except requests.RequestException as e:
        print(f"Error al obtener datos de Mitre: {e}")


# Ejecución periódica
while True:
    version_apache = obtener_version_apache()
    version_wordpress = obtener_version_wordpress('wordpress', 'anainf', 'anainf')
    version_mysql = obtener_version_mysql('mysql', 'exampleuser', 'examplepass', 'exampledb')

    print("\nResultados CVE Mitre:")
    buscar_vulnerabilidades_mitre("apache", version_apache)
    buscar_vulnerabilidades_mitre("wordpress", version_wordpress)
    buscar_vulnerabilidades_mitre("mysql", version_mysql)

    time.sleep(300)  # Ejecutar cada 5 minutos