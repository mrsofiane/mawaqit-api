# Security Features: Authentication & Rate Limiting

## Overview

Mawaqit API includes two main security features:

1. **Bearer Token Authentication** (opt-in) - Protect your API with a secret token
2. **Rate Limiting** (always active) - Prevent abuse by limiting requests per IP address

## Bearer Token Authentication

### What It Does

Bearer token authentication ensures that only authorized clients can access your API endpoints (except public endpoints like root info and documentation).

### Configuration

#### Enable Authentication

1. **Generate a secure bearer token:**

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

2. **Add to your `.env` file:**

```env
ENABLE_AUTH=true
BEARER_TOKEN=your_generated_secure_token_here
```

3. **Restart the API** - Authentication is now required

#### Disable Authentication (Default)

```env
ENABLE_AUTH=false
# or simply omit this variable
```

### Making Authenticated Requests

#### Using Swagger UI

When authentication is enabled:

1. Open `http://your-api.com/docs`
2. Click the "Authorize" button (top-right)
3. Enter your bearer token
4. Click "Authorize"
5. Now you can test protected endpoints directly in the browser

### Public Endpoints

These endpoints are **always accessible** without authentication:

- `GET /api/v1/` - Root/info endpoint
- `/docs` - Swagger UI documentation
- `/openapi.json` - OpenAPI schema
- `/redoc` - ReDoc documentation

### Error Responses

**Missing Authorization Header:**
```json
{
  "detail": "Missing Authorization header"
}
```
HTTP Status: `401 Unauthorized`

**Invalid Bearer Token:**
```json
{
  "detail": "Invalid bearer token"
}
```
HTTP Status: `401 Unauthorized`

## Rate Limiting

### What It Does

Rate limiting prevents abuse by restricting the number of requests each IP address can make within a time window.

- **Default Limit:** 60 requests per minute per unique IP address
- **Always Active:** Cannot be disabled, only configured

### Configuration

Edit your `.env` file:

```env
# Format: "number/time_unit"
RATE_LIMIT=60/minute      # 60 requests per minute (default)
RATE_LIMIT=1000/hour      # 1000 requests per hour
RATE_LIMIT=10000/day      # 10000 requests per day
RATE_LIMIT=5/second       # 5 requests per second
```

### Rate Limit Exceeded Response

```json
{
  "detail": "Rate limit exceeded: 60 per 1 minute"
}
```
HTTP Status: `429 Too Many Requests`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_AUTH` | No | `false` | Enable/disable bearer token authentication |
| `BEARER_TOKEN` | Yes (if `ENABLE_AUTH=true`) | - | Your secret bearer token |
| `RATE_LIMIT` | No | `60/minute` | Rate limit per IP address |

## Next Steps

- [View API Usage Examples](/docs/usage_example.md)
- [Enable Redis Caching](/docs/redis_activation.md)
- [Docker Deployment](/docs/docker.md)
