# Starship Architect

A web application for designing and managing starships for the Star Wars Saga Edition RPG.

## Local Development

This project uses Docker Compose to provide a full-stack local development environment.

### Prerequisites

- Docker and Docker Compose.

### Running the App

1. **Start the stack:**

   From the repository root:

   ```bash
   docker compose up -d
   ```

   This will start:
   - **Frontend App**: `http://localhost:8080` (Nginx serving `public/` + API Proxy)
   - **Backend Service**: `http://localhost:8787` (Cloudflare Worker with D1)

2. **Initialize the local database:**

   Wait for the backend service to be fully up (check `docker compose logs backend`), then apply the schema:

   ```bash
   docker compose exec backend wrangler d1 execute swse-db --local --file=schema.sql
   ```

   This creates the necessary tables (`users`, `ships`, `permissions`, etc.) in the local SQLite database managed by Wrangler inside the container.

### Architecture

- **Frontend**: Static HTML/JS served via Nginx from `public/`.
- **Backend**: Cloudflare Worker (Python/FastAPI) located in `backend/`.
- **Database**: Cloudflare D1 (SQLite), running locally via Wrangler.
- **Infrastructure**: Terraform definitions in `infrastructure/`.

### Authentication

The system supports both Google SSO and standard Email/Password authentication.
- **Register**: `POST /auth/register`
- **Login**: `POST /auth/login`
- **Google Auth**: `GET /auth/google`

Default development secrets are set in `docker-compose.yml`.
