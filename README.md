# Event Registration System

A RESTful backend API built with **Django** and **Django REST Framework** for managing events and user registrations. The system supports event discovery, authenticated registration, personal registration management, and role-based permissions for event organizers.

## Overview

The Event Registration System provides a backend for an event platform where users can browse events and manage their registrations, while authorized organizers manage event listings.

### Key Features

- **Event management** — list events, view event details, and create, update, or delete events.
- **User authentication** — token-based authentication for protected endpoints.
- **Event registration** — authenticated users can register for events.
- **Capacity validation** — prevents new registrations when an event is full.
- **Duplicate prevention** — a user cannot register for the same event more than once.
- **Personal registrations** — users can view their own registrations.
- **Registration cancellation** — users can cancel their own registrations, not other users' registrations.
- **Organizer permissions** — only users in the `Organizers` group can create, update, or delete events.
- **Automated tests** — API tests cover access control and important registration rules.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Django | Web framework |
| Django REST Framework | REST API endpoints and serialization |
| SQLite | Development database |
| Django Token Authentication | API authentication |
| Django Groups and Permissions | Organizer access control |

> **Database note:** This project currently uses SQLite for development. PostgreSQL can be configured for a production deployment if required.

## Architecture

```text
Client (Thunder Client / Postman / frontend)
                  |
                  v
        Django REST Framework API
                  |
          Authentication
          and Permissions
                  |
                  v
       Views + Serializers
                  |
                  v
        Django ORM / Models
           |           |
           v           v
         Event     Registration
                  |
                  v
                SQLite
```

## Getting Started

### Prerequisites

- Python 3.10 or later (use a version supported by your installed Django release)
- Git (optional, for cloning the repository)

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd EventRegistration
```

If you already have the project locally, open the `EventRegistration` folder in your terminal instead.

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the commands using Command Prompt instead:

```bat
venv\Scripts\activate.bat
```

### 3. Install dependencies

If `requirements.txt` is included:

```bash
pip install -r requirements.txt
```

If you have not created it yet, activate your virtual environment and generate it from your working project:

```bash
pip freeze > requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create an administrator (optional)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

The local API is available at:

`http://127.0.0.1:8000/api/`

Keep the development server running while sending API requests.

## API Reference

All routes below use the `/api/` prefix. Protected endpoints require this request header:

```http
Authorization: Token YOUR_AUTH_TOKEN
```

Send JSON request bodies with:

```http
Content-Type: application/json
```

### Authentication

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/auth/login/` | Log in and receive an authentication token | Public |
| `GET` | `/api/auth/profile/` | Retrieve the authenticated user's profile | Authenticated |

**Login example**

Request:

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Use the token returned by the login response in the `Authorization` header for protected endpoints. Never publish a real token in this README or commit it to source control.

### Events

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/events/` | List events | Public |
| `POST` | `/api/events/` | Create an event | Organizer |
| `GET` | `/api/events/<event_id>/` | Retrieve an event | Public |
| `PUT` | `/api/events/<event_id>/` | Replace an event | Organizer |
| `PATCH` | `/api/events/<event_id>/` | Partially update an event | Organizer |
| `DELETE` | `/api/events/<event_id>/` | Delete an event | Organizer |

**Create an event example**

```http
POST /api/events/
Authorization: Token YOUR_ORGANIZER_TOKEN
Content-Type: application/json
```

```json
{
  "title": "Django Backend Workshop",
  "description": "A practical introduction to Django REST APIs.",
  "date": "2027-01-20T10:00:00Z",
  "location": "Coimbatore",
  "capacity": 50
}
```

Only a user who belongs to the Django group named `Organizers` can create, update, or delete events. Event reads are public.

### Registrations

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/registrations/` | Register for an event | Authenticated |
| `GET` | `/api/registrations/my/` | List the current user's registrations | Authenticated |
| `DELETE` | `/api/registrations/<registration_id>/cancel/` | Cancel the current user's registration | Authenticated |

**Register for an event**

```http
POST /api/registrations/
Authorization: Token YOUR_AUTH_TOKEN
Content-Type: application/json
```

```json
{
  "event": 1
}
```

The `event` value is the ID of an existing event. On success, the API returns the created registration with HTTP `201 Created`.

The API rejects a registration when the event does not exist, the user is already registered, or the event has reached its capacity.

**View your registrations**

```http
GET /api/registrations/my/
Authorization: Token YOUR_AUTH_TOKEN
```

This endpoint returns registrations belonging to the authenticated user only.

**Cancel a registration**

```http
DELETE /api/registrations/1/cancel/
Authorization: Token YOUR_AUTH_TOKEN
```

Replace `1` with the registration ID. A user cannot cancel another user's registration.

## Data Model

### Event

Stores the details of an event.

| Field | Description |
|---|---|
| `id` | Primary key |
| `title` | Event title |
| `description` | Event description |
| `date` | Scheduled date and time |
| `location` | Event location |
| `capacity` | Maximum number of registrations |
| `created_at` | Record creation timestamp |

### Registration

Connects a user to an event.

| Field | Description |
|---|---|
| `id` | Primary key |
| `user` | Foreign key to the authenticated user model |
| `event` | Foreign key to the event |
| `registered_at` | Registration timestamp |

A database uniqueness constraint on `(user, event)` prevents duplicate registrations for the same event by the same user.

## Permissions at a Glance

| Action | Anonymous user | Authenticated regular user | Organizer |
|---|---:|---:|---:|
| View events | Yes | Yes | Yes |
| Create an event | No | No | Yes |
| Update or delete an event | No | No | Yes |
| Register for an event | No | Yes | Yes |
| View own registrations | No | Yes | Yes |
| Cancel own registration | No | Yes | Yes |

Organizer access is based on membership in the Django `Organizers` group. Authentication identifies the user; permissions determine which actions the user can perform.

## Running Tests

Run the event app's automated tests:

```bash
python manage.py test events
```

The tests are intended to verify behavior such as:

- Public event listing
- Organizer event creation
- Rejection of event creation by regular users
- Successful registration
- Duplicate registration prevention
- Event-capacity enforcement
- Protection against cancelling another user's registration
- Privacy of each user's registration list

A passing test run should finish with `OK`. Run the tests locally before submitting changes.

## Example Workflow

1. Start the Django development server.
2. Log in through `/api/auth/login/` and copy the returned token.
3. Browse available events using `GET /api/events/`.
4. Register for an event using `POST /api/registrations/`.
5. View your registrations using `GET /api/registrations/my/`.
6. Cancel your registration when needed.
7. Log in as an organizer to create, update, or delete events.

You can test these requests using Thunder Client in VS Code or Postman.

## Security and Production Notes

- Keep `SECRET_KEY`, credentials, and real authentication tokens out of Git.
- Do not commit `venv/`, local database files, or environment files containing secrets.
- Use environment variables for deployment secrets.
- Use HTTPS in production.
- Configure production settings, allowed hosts, and a production-ready database before deployment.
- SQLite is suitable for local development; assess database locking and transaction behavior before relying on capacity enforcement under concurrent production traffic.

## Project Structure

```text
EventRegistration/
├── manage.py
├── config/
│   ├── settings.py
│   └── urls.py
├── events/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── requirements.txt
└── README.md
```

The structure above shows the main files expected in this project. Your local repository may contain additional Django files such as `asgi.py`, `wsgi.py`, `admin.py`, and migration files.

## Future Improvements

- Add pagination, filtering, and search for events.
- Add registration and event ownership rules for organizers.
- Add email confirmations and event reminders.
- Add API schema documentation with Swagger/OpenAPI.
- Configure PostgreSQL and deployment settings for production.
- Add CI to run tests automatically on every push.

## Author

**Your Name**  
Python / Django Backend Developer

- GitHub: [Your GitHub Profile](<YOUR_GITHUB_PROFILE_URL>)
- LinkedIn: [Your LinkedIn Profile](<YOUR_LINKEDIN_PROFILE_URL>)

---

*Built as a backend project to practice Django, REST API design, authentication, authorization, relational data modeling, and automated testing.*
