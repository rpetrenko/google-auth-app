# Example of .env
```
# Update for production
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
REACT_APP_API_URL=http://localhost:8000
REACT_APP_URL=http://localhost:3000

# Database
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<dbname>
DATABASE_URL=postgresql://<username>:<password>@db:5432/<dbname>

# Google Auth
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
REACT_APP_GOOGLE_CLIENT_ID=<same as GOOGLE_CLIENT_ID>

# EMAIL
SECRET_KEY=<secret key>
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=<user gmail email>
EMAIL_PASSWORD=<app password> 
```

# Development mode
```docker-compose up --build
```

# remove all, including volumes
```
docker-compose down --volumes
```

# populate users in DB
```
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

# Run tests
* build
```
docker compose build
```
* start db, run tests, stop db container
```
docker-compose up -d db_test
docker-compose run --rm backend_test
docker-compose stop db_test
```