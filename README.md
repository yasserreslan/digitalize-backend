# README for Digitalize Hub Backend part

## Overview
This README outlines the backend implementation for the Digitalize HUB project, focusing on user authentication, device management, and system settings.

## Setup
- **Dependencies**: Python, Django, Django REST Framework, PostgreSQL, `django-cors-headers`.
- **Database**: PostgreSQL, with tables for `users`, `devices`, `admin_action_log`, and `system_settings`.

## Functionality
- **User Authentication**: Registration and login with token-based authentication. Includes handling of user types (normal, admin).
- **Device Management**: Functionality to add, toggle (activate/deactivate), and check the status of devices.
- **Admin Actions**: Endpoints for admins to log actions, manage user registrations, and toggle system settings.
- **System Settings**: Modify settings like registration limits and toggle registration status.
- **Data Retrieval**: Endpoints to fetch all 'normal' users with their devices, and to retrieve all system settings.
- **CORS**: Configured for cross-origin resource sharing.

### Endpoints

The backend of the Digitalize HUB project includes the following endpoints:

- **User Registration**: `/register/` allows new users to register.
- **User Login**: `/login/` authenticates users and returns a token.
- **Device Retrieval**: `/devices/` fetches devices associated with a user.
- **Device Status Toggle**: `/devices/status/` toggles the status of a device between active and inactive.
- **Change Registration Limit**: `/settings/registration_limit/` allows admins to change the daily user registration limit.
- **Toggle User Registration**: `/settings/toggle_registration/` enables admins to toggle the user registration on or off.
- **Get System Settings**: `/settings/` retrieves all system settings.
- **Fetch Normal Users and Devices**: `/users/` gets all 'normal' users and their devices.

Each endpoint serves specific functionalities, from user and device management to system settings adjustments.

### Admin User Creation on Startup
The project is configured to automatically create an admin user upon startup if the user doesn't already exist. This is achieved through a function that checks for the existence of a default admin username. If the admin user is not found, it creates one with a predefined username and password. This functionality is particularly useful for ensuring that an admin account is always available for immediate access to the system, especially after the first deployment or when resetting the system. The password is securely hashed before storage.

## Running the Project
- Set up the Python environment and install dependencies.
- Configure PostgreSQL database connection.
- Run migrations: `python manage.py migrate`.
- Start the server: `python manage.py runserver`.

## Deployment

### CI/CD Workflow with Docker

The project includes a GitHub Actions workflow for Continuous Integration and Continuous Deployment (CI/CD). The workflow is configured to:

- Trigger on `workflow_dispatch` and `push` events to the `dev` branch.
- Check out the repository code.
- Set up Docker Buildx.
- Log in to DockerHub using the provided username and a password stored in GitHub secrets.
- Build and push the Docker image to DockerHub, tagging it as `yasserrs/digitalize:backend`.

This workflow automates the process of building a Docker image for the backend and pushing it to DockerHub, ensuring that the latest version of the backend is containerized and readily deployable. Docker secrets are used to securely handle credentials.

This project is configured for deployment using Docker and Nginx, ensuring ease of deployment and scalability. 

### Docker Configuration
- A `compose.yaml` file is included, defining the Docker services, networks, and volumes for the application and database.
- The Django application and PostgreSQL database are set as separate services, allowing for independent scaling and management.

### Nginx Configuration
- An `nginx.conf` file is provided for the Nginx web server, acting as a reverse proxy for the Django application.
- Nginx is configured to efficiently handle static and media files, and to proxy requests to the Django app.

### Deployment Steps
1. **Docker Setup**: Install Docker and Docker Compose.
2. **Environment Configuration**: Set up environment variables as needed (e.g., database credentials).
3. **Building Containers**: Run `docker-compose up --build` to build and start the containers.
4. **Migrations**: Run Django migrations within the Docker container.
5. **Static Files**: Collect static files using Django's `collectstatic` command.

### Managing the Deployment
- The deployment can be monitored and managed using Docker commands.
- Scaling the application can be achieved by adjusting the `docker-compose.yaml` and running the appropriate Docker Compose commands.