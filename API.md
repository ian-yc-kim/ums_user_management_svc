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

## POST /terminate

### Description

This endpoint allows authenticated users to terminate their accounts, invalidating all active sessions and removing user data.

### Request

**Method:** POST

**Headers:**

- `Authorization`: Bearer JWT token required for authentication.

**Body:**

No request body is required.

### Responses

- **200 OK**: Account successfully terminated.
- **400 Bad Request**: Account is already terminated.
- **401 Unauthorized**: Invalid or missing authentication token.
- **404 Not Found**: User not found.
- **500 Internal Server Error**: Account termination failed.

### Example

```
POST /terminate HTTP/1.1
Host: api.siriusys.com
Authorization: Bearer <token>
```

### Error Codes

- **400**: `Account is already terminated.`
- **401**: `Invalid or missing authentication token.`
- **404**: `User not found.`
- **500**: `Account termination failed.`

### Notes

- Ensure that the provided JWT token is valid and not expired.
- Upon successful termination, all active sessions will be invalidated.