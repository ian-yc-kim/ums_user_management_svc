# ums_user_management_svc

## User Signup Feature

### Endpoint Overview

The `POST /signup` endpoint allows users to create a new account by providing their email, full name, country, state/province, and password. This endpoint ensures that all required fields are validated and stored securely in the system.

### Request Parameters

- **email** (`EmailStr`): User's email address. Must be a valid email format.
- **full_name** (`str`): User's full name. Minimum length of 1 character.
- **country** (`str`): User's country. Minimum length of 1 character.
- **state_province** (`str`): User's state or province. Minimum length of 1 character.
- **password** (`str`): User's password. Must be at least 8 characters long and meet complexity requirements.

### Response Structure

- **Success Response** (`200 OK`):
  ```json
  {
      "message": "User created successfully. Please verify your email."
  }
  ```

- **Error Responses**:
  - `400 Bad Request`: Invalid input data.
  - `409 Conflict`: Email already registered.
  - `500 Internal Server Error`: Server-side error.

### Email Verification

After signing up, users receive a verification email to confirm their email address. The verification link is generated using a secure token and directs the user to the verification endpoint. Upon clicking the link, the user's account status is updated to active.

### Setup Instructions

Ensure the following dependencies are installed:

- `email-validator`
- `bcrypt`
- `itsdangerous`

Install dependencies using Poetry:

```bash
poetry install
```

### Usage Examples

**Sign Up using `curl`:**

```bash
curl -X POST "http://localhost:8000/signup" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "user@example.com",
           "full_name": "John Doe",
           "country": "USA",
           "state_province": "California",
           "password": "Password123"
         }'
```

**Sign Up using HTTPie:**

```bash
http POST http://localhost:8000/signup \
    email=user@example.com \
    full_name="John Doe" \
    country=USA \
    state_province=California \
    password=Password123
```
