# Debug Endpoints for Service Token Inspection

## ⚠️ WARNING
**These endpoints expose sensitive authentication tokens. Remove or disable them in production!**

---

## Frontend Debug Endpoints

### 1. Debug Session Information
**Endpoint:** `GET /debug/session`  
**Authentication:** Requires login  
**Purpose:** Inspect user session and JWT token

**Request:**
```bash
curl http://localhost:5000/debug/session \
  -H "Cookie: session=<your-session-cookie>"
```

**Response:**
```json
{
  "session_data": {
    "has_auth_token": true,
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user123",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "session_keys": ["auth_token", "user", "_permanent"]
  },
  "cookies": {
    "session": "..."
  },
  "note": "This is the JWT token used for backend API calls"
}
```

---

### 2. Debug Service Token Generation
**Endpoint:** `GET /debug/service-token`  
**Authentication:** Requires login  
**Purpose:** See how service tokens are generated and what headers are sent to other microservices

**Request:**
```bash
curl http://localhost:5000/debug/service-token \
  -H "Cookie: session=<your-session-cookie>"
```

**Response:**
```json
{
  "service_token": {
    "raw_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXJ2aWNlIjoiZnJvbnRlbmQiLCJleHAiOjE3MzA4MTg0MzQsImlhdCI6MTczMDgxNDgzNH0.signature",
    "payload": {
      "service": "frontend",
      "exp": 1730818434,
      "iat": 1730814834
    },
    "expiry_hours": 1,
    "note": "This token authenticates the frontend service to other microservices"
  },
  "user_token": {
    "raw_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcjEyMyIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsImV4cCI6MTczMDkwMTIzNCwiaWF0IjoxNzMwODE0ODM0fQ.signature",
    "payload": {
      "user_id": "user123",
      "email": "user@example.com",
      "exp": 1730901234,
      "iat": 1730814834
    },
    "expiry_hours": 24,
    "note": "This token authenticates the user"
  },
  "request_headers": {
    "Content-Type": "application/json",
    "X-Service-Name": "frontend",
    "X-Service-Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "example_request_to_file_parsing": {
    "method": "POST",
    "url": "http://localhost:5002/api/upload/submit",
    "headers": {
      "Content-Type": "application/json",
      "X-Service-Name": "frontend",
      "X-Service-Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    "body": "multipart/form-data with files"
  },
  "how_it_works": {
    "step_1": "ServiceClient._get_service_headers() is called",
    "step_2": "AuthMiddleware.generate_service_token(service_name) creates X-Service-Token",
    "step_3": "User token (if exists) is added as Authorization: Bearer <token>",
    "step_4": "Headers are sent with every request to other microservices",
    "step_5": "Receiving service validates both tokens (if @auth_middleware.require_auth is used)"
  },
  "warning": "This endpoint exposes sensitive tokens - remove in production!"
}
```

**What You'll See:**
- **service_token**: The JWT token that identifies the frontend service
  - Payload contains `service: "frontend"`
  - Expires in 1 hour
  - Used for service-to-service authentication

- **user_token**: The JWT token that identifies the logged-in user
  - Payload contains user_id and email
  - Expires in 24 hours
  - Used for user authentication

- **request_headers**: The actual headers sent to other microservices
  - `X-Service-Token`: Service authentication
  - `Authorization`: User authentication
  - `X-Service-Name`: Identifies calling service

- **how_it_works**: Step-by-step flow of token generation

---

## File Parsing Debug Endpoints

### 3. Debug Request Headers (File Parsing)
**Endpoint:** `GET /debug/request-headers` or `POST /debug/request-headers`  
**Authentication:** None (accepts any request)  
**Purpose:** See what headers and tokens the file-parsing service receives

**Request:**
```bash
# Simple GET request
curl http://localhost:5002/debug/request-headers

# Simulate a real request with tokens
curl http://localhost:5002/debug/request-headers \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-Service-Name: frontend"
```

**Response:**
```json
{
  "received_headers": {
    "Host": "localhost:5002",
    "User-Agent": "curl/7.68.0",
    "Accept": "*/*",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "X-Service-Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "X-Service-Name": "frontend",
    "Content-Type": "application/json"
  },
  "extracted_tokens": {
    "user_token": {
      "header": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "raw_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "decoded_payload": {
        "user_id": "user123",
        "email": "user@example.com",
        "exp": 1730901234,
        "iat": 1730814834
      }
    },
    "service_token": {
      "header": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "decoded_payload": {
        "service": "frontend",
        "exp": 1730818434,
        "iat": 1730814834
      },
      "service_name": "frontend"
    }
  },
  "request_info": {
    "method": "GET",
    "url": "http://localhost:5002/debug/request-headers",
    "endpoint": "debug_request_headers",
    "remote_addr": "127.0.0.1"
  },
  "note": "This shows what file-parsing service receives from frontend",
  "warning": "This endpoint exposes sensitive tokens - remove in production!"
}
```

**What You'll See:**
- **received_headers**: All HTTP headers received by file-parsing service
- **extracted_tokens**: Decoded JWT tokens showing their payloads
- **request_info**: Metadata about the request

---

## Usage Examples

### Example 1: Test Service Token Generation

1. **Start services:**
```bash
./start-services.sh
```

2. **Login to get session:**
```bash
# Visit http://localhost:5000/login in browser
# Login with Google/GitHub
```

3. **Check service token generation:**
```bash
curl http://localhost:5000/debug/service-token \
  -H "Cookie: session=<copy-from-browser-devtools>"
```

4. **Verify what file-parsing receives:**
```bash
curl http://localhost:5002/debug/request-headers \
  -H "Authorization: Bearer <copy-user-token-from-step-3>" \
  -H "X-Service-Token: <copy-service-token-from-step-3>" \
  -H "X-Service-Name: frontend"
```

---

### Example 2: Test Token Expiry

1. **Generate a token:**
```bash
curl http://localhost:5000/debug/service-token -H "Cookie: session=..."
```

2. **Copy the service token and wait 1 hour (or modify expiry in code)**

3. **Test with expired token:**
```bash
curl http://localhost:5002/debug/request-headers \
  -H "X-Service-Token: <expired-token>"
```

4. **You should see:** `"decoded_payload": "Decode error: Signature has expired"`

---

### Example 3: Verify Real File Upload Request

1. **Enable logging in file-parsing service** (add to `app.py`):
```python
@app.before_request
def log_request():
    print(f"[DEBUG] {request.method} {request.path}")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
```

2. **Upload a file through frontend:**
```bash
# Visit http://localhost:5000/dashboard
# Upload resume and job description
```

3. **Check logs to see actual headers sent**

4. **Or use debug endpoint directly:**
```bash
curl http://localhost:5002/debug/request-headers \
  -X POST \
  -F "resume=@test_resume.pdf" \
  -H "Authorization: Bearer <token>" \
  -H "X-Service-Token: <service-token>" \
  -H "X-Service-Name: frontend"
```

---

## Token Payload Breakdown

### Service Token Payload
```json
{
  "service": "frontend",      // Which service is making the request
  "exp": 1730818434,          // Expiration timestamp (1 hour from creation)
  "iat": 1730814834           // Issued at timestamp
}
```

**Purpose:** Authenticates that a legitimate microservice is making the request

### User Token Payload
```json
{
  "user_id": "user123",       // Unique user identifier
  "email": "user@example.com", // User's email
  "exp": 1730901234,          // Expiration timestamp (24 hours from creation)
  "iat": 1730814834           // Issued at timestamp
}
```

**Purpose:** Authenticates which user is making the request through the service

---

## Token Lifecycle

```
1. User Login (OAuth)
   ↓
2. Login Service generates User JWT (24h expiry)
   ↓
3. Frontend stores User JWT in session
   ↓
4. Frontend needs to call File Parsing
   ↓
5. ServiceClient._get_service_headers() called
   ↓
6. AuthMiddleware.generate_service_token('frontend') creates Service JWT (1h expiry)
   ↓
7. Request sent with both tokens:
   - Authorization: Bearer <user-jwt>
   - X-Service-Token: <service-jwt>
   ↓
8. File Parsing receives both tokens
   ↓
9. If endpoint has @auth_middleware.require_auth:
   - Validates User JWT
   - Validates Service JWT (optional)
   ↓
10. Request processed
```

---

## Security Notes

### Why Two Tokens?

1. **User Token (Authorization header)**
   - Identifies WHO is making the request
   - Long-lived (24 hours)
   - Shared across all services for that user
   - Validated by `@auth_middleware.require_auth`

2. **Service Token (X-Service-Token header)**
   - Identifies WHICH SERVICE is making the request
   - Short-lived (1 hour) for security
   - Generated fresh for each inter-service call
   - Prevents external clients from directly calling internal services

### Current Implementation Note

⚠️ **Important:** Currently, user authentication is partially disabled in file-parsing service (uses `user_id = 'anonymous'`). The infrastructure is in place but not enforced on all endpoints.

---

## Testing Checklist

- [ ] Service token is generated with correct payload
- [ ] Service token expires after 1 hour
- [ ] User token is forwarded correctly
- [ ] File-parsing receives both tokens
- [ ] Tokens can be decoded successfully
- [ ] Invalid tokens are rejected (if validation enabled)
- [ ] Headers are formatted correctly

---

## Troubleshooting

### Issue: "Decode error: Signature has expired"
**Solution:** Token expired. Generate a new one.

### Issue: "Decode error: Invalid token"
**Solution:** Check that JWT_SECRET is the same across all services.

### Issue: No X-Service-Token in headers
**Solution:** Ensure ServiceClient is being used, not direct requests.

### Issue: User token is null
**Solution:** User not logged in. Visit `/login` first.

---

**Last Updated:** November 6, 2025  
**Remember:** Remove these debug endpoints before deploying to production!
