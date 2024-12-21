# API Documentation

## POST /logout

### Description

This endpoint allows users to log out of the system by invalidating their session tokens.

### Request

**Method:** POST

**Headers:**

- `Authorization`: Bearer token required for authentication.

**Body:**

No request body is required.

### Responses

- **200 OK**: Logout successful.
- **401 Unauthorized**: Invalid or missing authentication token.

### Example

```
POST /logout HTTP/1.1
Host: api.siriusys.com
Authorization: Bearer <token>
```

### Notes

Ensure that the token provided is valid and not expired.