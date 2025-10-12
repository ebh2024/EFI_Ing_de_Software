# Airline Management System

This is a Django-based Airline Management System.

## Features

- User authentication (registration, login, logout)
- Flight search and booking
- Passenger management
- Airplane management
- Seat layout configuration
- Flight history tracking
- Ticket generation

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/EFI_Ing_de_Software.git
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

## Django Rest Framework API

This project now includes a RESTful API using Django Rest Framework.

### API Endpoints

The API endpoints are available under the `/api/` prefix.

-   `/api/airplanes/` - Manage airplanes
-   `/api/flights/` - Manage flights
-   `/api/passengers/` - Manage passengers
-   `/api/reservations/` - Manage reservations
-   `/api/seatlayouts/` - Manage seat layouts
-   `/api/sealtypes/` - Manage seat types
-   `/api/seatlayoutpositions/` - Manage seat layout positions
-   `/api/flighthistories/` - Manage flight histories
-   `/api/tickets/` - Manage tickets

Each endpoint supports standard REST operations (GET, POST, PUT, PATCH, DELETE).
