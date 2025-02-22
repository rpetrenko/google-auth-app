# Example of .env
```
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname
DATABASE_URL=postgresql://username:password@db:5432/dbname

# Google Auth
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
# Update for production
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Application
#ENV=production
ENV=development
# Update for production to https://talkingdigits.com
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=xxx
```

# Development mode
docker-compose up --build

# remove all, including volumes
docker-compose down --volumes


curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
