# Production Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Production server with at least 2GB RAM
- Domain name (optional, for HTTPS)

## Quick Start

1. **Clone and prepare environment:**
   ```bash
   git clone <repository-url>
   cd CompleteVibeCodingTask
   cp .env.production.example .env
   # Edit .env with your production values
   ```

2. **Deploy the application:**
   ```bash
   docker-compose up -d
   ```

3. **Initialize database (first time only):**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Environment Variables

Key production environment variables:

- `POSTGRES_PASSWORD`: Secure password for PostgreSQL
- `API_KEY`: API key for webhook authentication
- `SECRET_KEY`: Secret key for JWT tokens
- `VITE_API_URL`: Frontend API URL (e.g., https://your-domain.com)
- `VITE_WS_URL`: WebSocket URL (e.g., wss://your-domain.com)

## SSL/HTTPS Setup

For production with HTTPS:

1. Place SSL certificates in `nginx/ssl/` directory:
   ```
   nginx/ssl/cert.pem
   nginx/ssl/key.pem
   ```

2. Uncomment HTTPS configuration in `nginx/nginx.conf`

3. Update domain name in nginx configuration

4. Restart services:
   ```bash
   docker-compose down && docker-compose up -d
   ```

## Monitoring

- **Health checks:** `GET /health`
- **Application logs:** `docker-compose logs -f`
- **Service status:** `docker-compose ps`

## Backup

Backup database regularly:
```bash
docker-compose exec postgres pg_dump -U postgres agent_tracker > backup.sql
```

## Scaling

- **Frontend:** Scale by adding more nginx instances behind load balancer
- **Backend:** Scale by adding more backend instances
- **Database:** Consider managed PostgreSQL for large scale

## Security

- Change default passwords and keys
- Use HTTPS in production
- Implement firewall rules
- Regular security updates
- Monitor access logs