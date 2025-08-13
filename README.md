# Proyecto de Gestión de Aerolínea

Este es un sistema web para gestionar una aerolínea, desarrollado con Django. Permite a los usuarios buscar vuelos, reservar asientos, gestionar perfiles de pasajeros y recibir notificaciones. Los administradores pueden generar reportes de pasajeros por vuelo.

## Características

*   **Búsqueda de Vuelos**: Permite a los usuarios buscar vuelos por origen, destino y fecha de salida.
*   **Detalle de Vuelo y Reserva de Asientos**: Visualización de detalles de vuelos y reserva de asientos disponibles.
*   **Gestión de Pasajeros**: Creación y edición de perfiles de pasajeros.
*   **Autenticación de Usuarios**: Registro, inicio de sesión y cierre de sesión.
*   **Procesamiento de Pagos**: Simulación de procesamiento de pagos para reservas.
*   **Notificaciones**: Sistema de notificaciones para usuarios.
*   **Reportes de Pasajeros**: Funcionalidad para que el personal de la aerolínea genere reportes de pasajeros por vuelo.
*   **Internacionalización (i18n)**: Soporte para múltiples idiomas (inglés y español).

## Tecnologías Utilizadas

*   **Backend**: Django (Python Web Framework)
*   **Base de Datos**: SQLite (por defecto, configurable para PostgreSQL, MySQL, etc.)
*   **Frontend**: HTML, CSS (Bootstrap), JavaScript
*   **Formularios**: Django Crispy Forms con Bootstrap 5
*   **Gestión de Dependencias**: pip

## Instalación y Configuración

### Con Docker (Recomendado)

1.  **Clonar el Repositorio**:
    ```bash
    git clone https://github.com/ebh2024/EFI_Ing_de_Software.git
    cd EFI_Ing_de_Software
    ```

2.  **Levantar los Contenedores**:
    ```bash
    docker-compose up --build
    ```
    Esto construirá la imagen de Docker, iniciará los servicios de la aplicación y la base de datos, aplicará las migraciones y creará un superusuario (`admin`/`admin`).

3.  **Acceder a la Aplicación**:
    El sitio estará disponible en `http://localhost:8000/`.

### Localmente (Sin Docker)

Sigue estos pasos para configurar y ejecutar el proyecto localmente:

1.  **Clonar el Repositorio**:
    ```bash
    git clone https://github.com/ebh2024/EFI_Ing_de_Software.git
    cd EFI_Ing_de_Software/EFI # Asegúrate de estar en el directorio raíz del proyecto Django
    ```

2.  **Crear un Entorno Virtual (Opcional pero Recomendado)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate # En Linux/macOS
    # venv\Scripts\activate # En Windows
    ```

3.  **Instalar Dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplicar Migraciones de la Base de Datos**:
    ```bash
    python manage.py migrate
    ```

5.  **Crear un Superusuario (para acceder al panel de administración)**:
    ```bash
    python manage.py createsuperuser
    ```
    Sigue las instrucciones para crear un nombre de usuario y contraseña.

6.  **Cargar Datos de Ejemplo (Opcional)**:
    El proyecto incluye un comando para poblar la base de datos con datos de ejemplo.
    ```bash
    python manage.py populate_data
    ```

7.  **Compilar Archivos de Traducción (para i18n)**:
    ```bash
    python manage.py makemessages -l es
    python manage.py compilemessages
    ```

8.  **Ejecutar el Servidor de Desarrollo**:
    ```bash
    python manage.py runserver
    ```
    El sitio estará disponible en `http://127.0.0.1:8000/`.

## Estructura del Proyecto

*   `aerolinea_project/`: Configuración principal del proyecto Django (settings, urls, wsgi, asgi).
*   `gestion/`: Aplicación principal de Django que contiene la lógica de negocio:
    *   `models.py`: Definiciones de los modelos de la base de datos (Vuelo, Pasajero, Asiento, Reserva, etc.).
    *   `views.py`: Lógica para manejar las solicitudes HTTP y renderizar plantillas.
    *   `urls.py`: Definición de las rutas URL específicas de la aplicación `gestion`.
    *   `forms.py`: Formularios Django para la entrada de datos.
    *   `services.py`: Capa de servicios que encapsula la lógica de negocio y orquesta las operaciones.
    *   `repositories.py`: Capa de repositorio para la abstracción de la base de datos.
    *   `templates/gestion/`: Archivos HTML para las vistas de la aplicación.
    *   `static/gestion/`: Archivos estáticos (CSS, JavaScript, imágenes).
    *   `migrations/`: Archivos de migración de la base de datos.
    *   `management/commands/`: Comandos de Django personalizados (ej. `populate_data.py`).
*   `locale/`: Archivos de traducción para internacionalización.
*   `staticfiles/`: Directorio para archivos estáticos recolectados en producción.
*   `db.sqlite3`: Archivo de la base de datos SQLite (en desarrollo).

## Modelos de la Base de Datos

*   **Aircraft**: Representa un tipo de avión con su modelo, capacidad, diseño de asientos e información técnica.
*   **Flight**: Representa un vuelo con origen, destino, fechas de salida/llegada, precio y el avión asignado.
*   **Passenger**: Información del pasajero, vinculada a un usuario de Django, incluyendo nombre, documento, email y teléfono.
*   **Seat**: Representa un asiento específico en un vuelo, con su número y estado (disponible, reservado, ocupado).
*   **Booking**: Representa una reserva de vuelo, vinculando un vuelo, un pasajero y un asiento. Incluye estado de pago y detalles de transacción.
*   **Notification**: Notificaciones para usuarios, con mensaje, fecha de creación y estado de lectura.

## Uso

1.  **Acceder al Sitio**: Abre tu navegador y ve a `http://127.0.0.1:8000/`.
2.  **Buscar Vuelos**: Utiliza los campos de búsqueda en la página principal para encontrar vuelos.
3.  **Reservar un Asiento**: Haz clic en un vuelo para ver los detalles y seleccionar un asiento disponible.
4.  **Crear Pasajero**: Si no tienes una cuenta, puedes registrarte como pasajero.
5.  **Perfil de Usuario**: Accede a tu perfil para ver tus reservas y editar tu información.
6.  **Panel de Administración**: Accede a `http://127.0.0.1:8000/admin/` con las credenciales del superusuario para gestionar datos.

## Internacionalización

El proyecto soporta inglés y español. Puedes cambiar el idioma utilizando el selector de idioma o configurando tu navegador. Las URLs también se adaptan al idioma (`/es/` o `/en/`).

## Panel de Administración de Django

El panel de administración de Django está disponible en `/admin/`. Aquí puedes gestionar todos los modelos de la base de datos (Vuelos, Pasajeros, Reservas, etc.).
