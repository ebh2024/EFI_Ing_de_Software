# Airline Management System

This is a comprehensive Django-based Airline Management System designed to handle various aspects of airline operations, from flight and passenger management to seat reservations and ticket generation. It features both a traditional web interface and a robust RESTful API.

## Features

-   **User Authentication**: Secure user registration, login, and logout functionalities.
-   **Flight Management**: Create, view, update, and delete flights, including details like origin, destination, departure/arrival times, and associated airplanes.
-   **Airplane Management**: Manage airplane details, including model, manufacturer, registration number, capacity, and seat layouts.
-   **Passenger Management**: Handle passenger information, including personal details, document types, and contact information.
-   **Seat Layout Configuration**: Define flexible seat layouts for different airplane models, specifying rows, columns, and seat types.
-   **Seat Type Management**: Configure various seat types (e.g., Economy, Business, First Class) with customizable price multipliers.
-   **Reservation System**:
    -   View available seats for specific flights.
    -   Reserve seats for passengers.
    -   Track reservation status (Pending, Confirmed, Cancelled, Paid).
    -   Generate electronic tickets for confirmed reservations.
-   **Flight History Tracking**: Maintain a detailed history of flights taken by each passenger.
-   **Ticket Generation**: Generate and manage unique tickets for each reservation.
-   **Internationalization (i18n)**: Supports multiple languages (English and Spanish) for a broader user base.
-   **RESTful API**: A complete API built with Django Rest Framework for programmatic access to all core functionalities.
-   **API Documentation**: Interactive API documentation powered by DRF-YASG (Swagger/OpenAPI).

## Technologies Used

-   **Backend**: Django 5.2.7
-   **Database**: SQLite3 (default for development)
-   **API**: Django Rest Framework 3.16.1
-   **Authentication**: Django Rest Framework Simple JWT 5.5.1
-   **API Documentation**: DRF-YASG 1.21.11
-   **PDF Generation**: WeasyPrint 66.0
-   **Frontend**: HTML, CSS, JavaScript (Django Templates)
-   **Internationalization**: Django's built-in i18n

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ebh2024/EFI_Ing_de_Software.git
    cd EFI_Ing_de_Software
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Apply database migrations:**
    ```bash
    python3 manage.py migrate
    ```

4.  **Create a superuser (for admin access):**
    ```bash
    python3 manage.py createsuperuser
    ```

5.  **Run the development server:**
    ```bash
    python3 manage.py runserver
    ```

    The application will be available at `http://127.0.0.1:8000/`.

## Docker Setup

1.  **Prerequisites**: Ensure Docker and Docker Compose are installed on your system.

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/ebh2024/EFI_Ing_de_Software.git
    cd EFI_Ing_de_Software
    ```

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

    The application will be available at `http://localhost:8000`.

4.  **Stop the application:**
    ```bash
    docker-compose down
    ```

## Django Rest Framework API

This project includes a comprehensive RESTful API using Django Rest Framework, secured with JWT authentication.

### API Endpoints

The API endpoints are available under the `/api/` prefix.

-   `/api/airplanes/` - Manage airplanes
-   `/api/flights/` - Manage flights
-   `/api/passengers/` - Manage passengers
-   `/api/reservations/` - Manage reservations
-   `/api/seat_layouts/` - Manage seat layouts
-   `/api/seat_types/` - Manage seat types
-   `/api/seat_layout_positions/` - Manage seat layout positions
-   `/api/flight_history/` - Manage flight histories
-   `/api/tickets/` - Manage tickets

Each endpoint supports standard REST operations (GET, POST, PUT, PATCH, DELETE).

### API Documentation (Swagger UI)

Interactive API documentation is available at:
`http://127.0.0.1:8000/swagger/`

You can use this interface to explore endpoints, test requests, and understand the API schema.

## Usage

### Web Interface

Access the application through your browser at `http://127.0.0.1:8000/`. You can register a new user or log in with a superuser account to access the administrative functionalities.

### API Usage

To interact with the API, you will typically need to obtain an authentication token. This project uses Simple JWT.

1.  **Obtain JWT Token**:
    Send a POST request to `/api/token/` with your username and password to get access and refresh tokens.

2.  **Authenticate API Requests**:
    Include the access token in the `Authorization` header of your API requests:
    `Authorization: Bearer YOUR_ACCESS_TOKEN`

Refer to the Swagger UI documentation for detailed information on each endpoint and its expected request/response formats.
