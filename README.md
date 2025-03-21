# UK Tax Statement Parser

A microservice for processing UK tax documents (P60, P45, self-assessment statements) using OCR and structured data extraction.

## Features

- Document upload and processing (PDF, PNG, JPEG)
- OCR text extraction using Tesseract and AWS Textract
- Structured data extraction with NLP
- Secure REST API with OAuth 2.0 authentication
- Role-based access control
- Multi-container architecture with Docker Compose
- Scalable and maintainable infrastructure

## Quick Start

1. Clone the repository
2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and run with Docker Compose:
```bash
docker compose up -d
```

4. Access the API at `http://localhost:8000`
   - API documentation available at `http://localhost:8000/docs`

## Container Architecture

The application is split into three main services:

1. **App Container**
   - FastAPI application with OCR processing
   - Automatic database migrations
   - Health checks and monitoring

2. **Database Container**
   - PostgreSQL 14
   - Persistent volume storage
   - Automated backups

3. **Cache Container**
   - Redis 6 for caching and rate limiting
   - In-memory data storage
   - High performance

## Environment Variables

Required environment variables:
```
DATABASE_URL=postgresql://taxparser:taxparser@db:5432/tax_parser
REDIS_URL=redis://cache:6379/0
SECRET_KEY=your-secret-key
AWS_ACCESS_KEY_ID=your-aws-key  # If using AWS Textract
AWS_SECRET_ACCESS_KEY=your-aws-secret  # If using AWS Textract
AWS_DEFAULT_REGION=eu-west-2  # Default AWS region
```

## API Endpoints

- POST `/upload` - Upload tax document
- GET `/status/{doc_id}` - Check processing status
- GET `/data/{doc_id}` - Retrieve extracted data
- DELETE `/delete/{doc_id}` - Delete document and data

## Security

- OAuth 2.0 authentication
- Role-based access control
- TLS 1.3 encryption in transit
- AES-256 encryption at rest
- Rate limiting
- Isolated container network

## Development

1. For local development without Docker:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. For development with Docker:
```bash
# Build and run all services
docker compose up --build

# View logs
docker compose logs -f

# Run migrations
docker compose exec app alembic upgrade head

# Access PostgreSQL
docker compose exec db psql -U taxparser -d tax_parser
```

## Testing

Run tests with:
```bash
# Local testing
pytest

# Container testing
docker compose exec app pytest
```

## Maintenance

1. Update services:
```bash
docker compose pull  # Get latest base images
docker compose build --no-cache  # Rebuild services
docker compose up -d  # Deploy updates
```

2. Database management:
```bash
# Create database backup
docker compose exec db pg_dump -U taxparser tax_parser > backup.sql

# Restore database
docker compose exec -T db psql -U taxparser tax_parser < backup.sql
```

3. Monitor services:
```bash
docker compose ps  # Check service status
docker compose top  # View running processes
```

## License

MIT License
