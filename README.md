# Sistema de Gestión de Aerolíneas

Este es un sistema integral de gestión de aerolíneas basado en Django, diseñado para manejar varios aspectos de las operaciones aéreas, desde la gestión de vuelos y pasajeros hasta la reserva de asientos y la generación de billetes. Cuenta con una interfaz web tradicional y una robusta API RESTful.

## Características

-   **Autenticación de Usuarios**: Funcionalidades seguras de registro, inicio de sesión y cierre de sesión de usuarios.
-   **Gestión de Vuelos**: Crear, ver, actualizar y eliminar vuelos, incluyendo detalles como origen, destino, horas de salida/llegada y aviones asociados.
-   **Gestión de Aviones**: Administrar detalles de aviones, incluyendo modelo, fabricante, número de registro, capacidad y diseños de asientos.
-   **Gestión de Pasajeros**: Manejar información de pasajeros, incluyendo detalles personales, tipos de documentos e información de contacto.
-   **Configuración de Diseño de Asientos**: Definir diseños de asientos flexibles para diferentes modelos de avión, especificando filas, columnas y tipos de asiento.
-   **Gestión de Tipos de Asiento**: Configurar varios tipos de asiento (por ejemplo, Económica, Ejecutiva, Primera Clase) con multiplicadores de precio personalizables.
-   **Sistema de Reservas**:
    -   Ver asientos disponibles para vuelos específicos.
    -   Reservar asientos para pasajeros.
    -   Seguimiento del estado de la reserva (Pendiente, Confirmada, Cancelada, Pagada).
    -   Generar billetes electrónicos para reservas confirmadas.
-   **Seguimiento del Historial de Vuelos**: Mantener un historial detallado de los vuelos realizados por cada pasajero.
-   **Generación de Billetes**: Generar y gestionar billetes únicos para cada reserva.
-   **Internacionalización (i18n)**: Soporta múltiples idiomas (inglés y español) para una base de usuarios más amplia.
-   **API RESTful**: Una API completa construida con Django Rest Framework para acceso programático a todas las funcionalidades principales.
-   **Documentación de la API**: Documentación interactiva de la API impulsada por DRF-YASG (Swagger/OpenAPI).

## Tecnologías Utilizadas

-   **Backend**: Django 5.2.7
-   **Base de Datos**: SQLite3 (por defecto para desarrollo)
-   **API**: Django Rest Framework 3.16.1
-   **Autenticación**: Django Rest Framework Simple JWT 5.5.1
-   **Documentación de la API**: DRF-YASG 1.21.11
-   **Generación de PDF**: WeasyPrint 66.0
-   **Frontend**: HTML, CSS, JavaScript (Plantillas de Django)
-   **Internacionalización**: i18n incorporado de Django

## Instrucciones de Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/ebh2024/EFI_Ing_de_Software.git
    cd EFI_Ing_de_Software
    ```

2.  **Crear un entorno virtual e instalar dependencias:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Aplicar migraciones de la base de datos:**
    ```bash
    python3 manage.py migrate
    ```

4.  **Crear un superusuario (para acceso de administrador):**
    ```bash
    python3 manage.py createsuperuser
    ```

5.  **Ejecutar el servidor de desarrollo:**
    ```bash
    python3 manage.py runserver
    ```

    La aplicación estará disponible en `http://127.0.0.1:8000/`.

## Configuración de Docker

1.  **Requisitos previos**: Asegúrese de tener Docker y Docker Compose instalados en su sistema.

2.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/ebh2024/EFI_Ing_de_Software.git
    cd EFI_Ing_de_Software
    ```

3.  **Construir y ejecutar con Docker Compose:**
    ```bash
    docker-compose up --build
    ```

    La aplicación estará disponible en `http://localhost:8000`.

4.  **Detener la aplicación:**
    ```bash
    docker-compose down
    ```

## API de Django Rest Framework

Este proyecto incluye una API RESTful completa utilizando Django Rest Framework, asegurada con autenticación JWT.

### Puntos de Acceso de la API

Los puntos de acceso de la API están disponibles bajo el prefijo `/api/`.

-   `/api/airplanes/` - Gestionar aviones
-   `/api/flights/` - Gestionar vuelos
-   `/api/passengers/` - Gestionar pasajeros
-   `/api/reservations/` - Gestionar reservas
-   `/api/seat_layouts/` - Gestionar diseños de asientos
-   `/api/seat_types/` - Gestionar tipos de asiento
-   `/api/seat_layout_positions/` - Gestionar posiciones de diseño de asientos
-   `/api/flight_history/` - Gestionar historiales de vuelo
-   `/api/tickets/` - Gestionar billetes

Cada punto de acceso soporta operaciones REST estándar (GET, POST, PUT, PATCH, DELETE).

### Documentación de la API (Swagger UI)

La documentación interactiva de la API está disponible en:
`http://127.0.0.1:8000/swagger/`

Puede usar esta interfaz para explorar puntos de acceso, probar solicitudes y comprender el esquema de la API.

## Uso

### Interfaz Web

Acceda a la aplicación a través de su navegador en `http://127.0.0.1:8000/`. Puede registrar un nuevo usuario o iniciar sesión con una cuenta de superusuario para acceder a las funcionalidades administrativas.

### Uso de la API

Para interactuar con la API, normalmente necesitará obtener un token de autenticación. Este proyecto utiliza Simple JWT.

1.  **Obtener Token JWT**:
    Envíe una solicitud POST a `/api/token/` con su nombre de usuario y contraseña para obtener tokens de acceso y actualización.

2.  **Autenticar Solicitudes de la API**:
    Incluya el token de acceso en el encabezado `Authorization` de sus solicitudes de API:
    `Authorization: Bearer SU_TOKEN_DE_ACCESO`

Consulte la documentación de Swagger UI para obtener información detallada sobre cada punto de acceso y sus formatos esperados de solicitud/respuesta.
