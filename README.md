# service-app

## Overview
This project is a Flask-based web application for managing healthcare services.

## Features
- User registration and login
- Search for healthcare services like hospitals, doctors, elder care, etc.
- Display detailed information about services, including doctor details at hospitals

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Anangsha072/service-app.git
    cd service-app
    ```

2. Create a virtual environment and install dependencies:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. Set up the database:
    ```sh
    flask db upgrade
    ```

4. Run the application:
    ```sh
    flask run
    ```

## Configuration
The application uses environment variables for configuration. Create a `.env` file in the root directory with the following content:
## Deployment
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
