# Email Verification API Service

## Overview
A robust, scalable email verification service built with Flask, designed to handle multiple projects with individual email configurations. The service provides a RESTful API for email verification workflows, supporting custom email templates and project-specific SMTP configurations.

## Tech Stack
- **Framework**: Flask 3.0.0
- **Database**: SQLAlchemy with SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **Email Service**: Flask-Mail
- **CORS Support**: Flask-CORS
- **Security**: URL Safe Timed Serializer for token generation

## Architecture
The application follows a modular architecture with:
- **Models**: Database schema and relationships
- **Routes**: API endpoints and business logic
- **Utils**: Helper functions and email handling
- **Config**: Environment-specific configurations

## Database Schema

### Project
```sql
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    api_key VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    mail_username VARCHAR(120),
    mail_password VARCHAR(120),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### User
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### VerificationStatus
```sql
CREATE TABLE verification_status (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verified_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (project_id) REFERENCES project(id)
);
```

## API Documentation

### Authentication
The API uses JWT (JSON Web Tokens) for authentication. All protected routes require a Bearer token in the Authorization header.

```http
Authorization: Bearer <your_jwt_token>
```

### Endpoints

#### 1. Create Project
```http
POST /api/projects
Content-Type: application/json

{
    "name": "Project Name",
    "description": "Project Description",
    "mail_username": "smtp_username@example.com",
    "mail_password": "smtp_password"
}
```
**Response**: 
```json
{
    "message": "Projeto criado com sucesso",
    "project": {
        "id": 1,
        "api_key": "generated_api_key",
        "name": "Project Name",
        "description": "Project Description",
        "mail_username": "smtp_username@example.com"
    }
}
```

#### 2. Project Authentication
```http
POST /api/login
Content-Type: application/json

{
    "api_key": "your_project_api_key"
}
```
**Response**:
```json
{
    "access_token": "jwt_token"
}
```

#### 3. Register Email for Verification
```http
POST /api/register
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "email": "user@example.com",
    "api_key": "project_api_key"
}
```
**Response**:
```json
{
    "message": "Email registrado com sucesso",
    "verification_token": "verification_token"
}
```

#### 4. Verify Email
```http
GET /api/verify/<verification_token>
```
**Response**:
```json
{
    "message": "Email verificado com sucesso"
}
```

#### 5. List Users
```http
GET /api/users
Authorization: Bearer <jwt_token>
```
**Response**:
```json
[
    {
        "id": 1,
        "email": "user@example.com",
        "verified": true,
        "created_at": "2025-03-25T14:59:23"
    }
]
```

## Security Features

1. **API Key Generation**: Secure random generation using Python's `secrets` module
2. **JWT Authentication**: Token-based authentication with 1-hour expiration
3. **Email Verification**: Time-limited tokens for email verification
4. **CORS Protection**: Configured CORS policies for API access
5. **Password Security**: Project SMTP credentials are stored securely
6. **Input Validation**: Email format validation and input sanitization

## Error Handling
The API implements comprehensive error handling:
- Invalid API keys
- Expired tokens
- Invalid email formats
- SMTP configuration errors
- Database constraints violations

## Rate Limiting Recommendations
To protect against abuse, implement rate limiting on:
- Email verification requests
- Login attempts
- Project creation
- Email sending

## Environment Variables
Create a `.env` file with:
```env
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

## Installation and Setup

1. Clone the repository
```bash
git clone <repository_url>
cd validator_email_jm2
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Setup environment variables
```bash
cp .env.example .env
# Edit .env with your configurations
```

5. Initialize database
```bash
flask db upgrade
```

6. Run the application
```bash
python app.py
```

## Testing
```bash
pytest tests/
```

## Performance Considerations
- Database indexing on frequently queried fields
- Caching for frequently accessed data
- Asynchronous email sending
- Connection pooling for database operations

## Monitoring and Logging
Implement monitoring for:
- API response times
- Email sending success rates
- Verification completion rates
- Error rates and types

## Future Enhancements
1. Multi-provider email support
2. Template customization API
3. Webhook notifications
4. Analytics dashboard
5. Bulk verification support
6. Custom domain support

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
