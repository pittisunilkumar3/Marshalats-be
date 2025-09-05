# Student Management System API Documentation

## Overview
This is a comprehensive Student Management System API built with FastAPI, supporting role-based access for Super Admin, Staff (Coach Admin), Coaches, and Students.

## Base URL
```
Production: https://edumanage-44.preview.dev.com/api
Development: http://localhost:8001/api
```

## Authentication
The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Error Responses
All endpoints may return the following error formats:

**400 Bad Request**:
```json
{
  "detail": "Error message describing what went wrong"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Insufficient permissions"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

## User Roles
- **super_admin**: Full system access, manages branches, courses, users
- **coach_admin**: Branch-level management, student enrollment, course scheduling
- **coach**: Limited access to assigned courses and students
- **student**: Personal profile, course enrollment, attendance, payments

## Available User Role Values
When creating or updating users, use these exact role values:
- `"super_admin"`
- `"coach_admin"`
- `"coach"`
- `"student"`

---

# API Endpoints

## 1. Authentication & User Management

### POST /api/auth/register
**Description**: Register a new student (public endpoint). Upon successful registration, an SMS containing login credentials will be sent to the registered phone number.
**Access**: Public
**Request Body**:
```json
{
  "email": "pittisunilkumar3@gmail.com",
  "phone": "+9876543210",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "password": "Neelarani@10",
  "date_of_birth": "2005-08-15",
  "gender": "male",
  "biometric_id": "optional-fingerprint-id",
  "course": {
    "category_id": "category-uuid",
    "course_id": "course-uuid",
    "duration": "6-months"
  },
  "branch": {
    "location_id": "location-uuid",
    "branch_id": "branch-uuid"
  }
}
```
**Required Fields**: `email`, `phone`, `first_name`, `last_name`, `role`
**Optional Fields**: `password`, `date_of_birth`, `gender`, `biometric_id`, `course`, `branch`
**Response**:
```json
{
  "message": "User registered successfully",
  "user_id": "0b44cebf-f0e1-4716-b521-0e3ba290e5c4"
}
```
**Notes**: 
- If `password` is not provided, a random password will be generated
- `date_of_birth` should be in YYYY-MM-DD format (e.g., "2005-08-15")
- `gender` accepts any string value
- `course` object is optional but if provided, all nested fields are required
- `branch` object is optional but if provided, all nested fields are required
- SMS with login credentials will be sent to the provided phone number



### POST /api/auth/login
**Description**: User login
**Access**: Public
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Required Fields**: `email`, `password`
**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwYjQ0Y2ViZi1mMGUxLTQ3MTYtYjUyMS0wZTNiYTI5MGU1YzQiLCJleHAiOjE3NTcxMzY3MDZ9.TzV1jpaRxAh0jRUPwZ5o8fAPuaBMNQsNgUAHhVKWZkI",
  "token_type": "bearer",
  "user": {
    "id": "1e22ab99-b6ab-4cf1-9bc5-95cd3d62da21",
    "email": "user@example.com",
    "role": "student",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "date_of_birth": "2005-08-15",
    "gender": "male",
    "course": {
      "category_id": "category-uuid",
      "course_id": "course-uuid",
      "duration": "6-months"
    },
    "branch": {
      "location_id": "location-uuid", 
      "branch_id": "branch-uuid"
    }
  }
}
```
**Note**: `date_of_birth`, `gender`, `course`, and `branch` will be `null` if not provided during registration.

### GET /api/auth/me
**Description**: Get current user information
**Access**: Authenticated users
**Headers**: 
```
Authorization: Bearer <your_jwt_token>
```
**Response**:
```json
{
  "id": "0b44cebf-f0e1-4716-b521-0e3ba290e5c4",
  "email": "user@example.com",
  "phone": "+1234567890",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "student",
  "branch_id": "branch-uuid",
  "biometric_id": "fingerprint_123",
  "is_active": true,
  "date_of_birth": "2005-08-15",
  "gender": "male",
  "course_category_id": "category-uuid",
  "course_id": "course-uuid",
  "course_duration": "6-months",
  "location_id": "location-uuid",
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```
**Note**: `date_of_birth`, `gender`, `branch_id`, `biometric_id`, and course-related fields may be `null` if not set.

### PUT /api/auth/profile
**Description**: Update user profile
**Access**: Authenticated users
**Headers**: 
```
Authorization: Bearer <your_jwt_token>
```
**Request Body** (all fields are optional):
```json
{
  "email": "newemail@example.com",
  "phone": "+0987654321",
  "first_name": "Jane",
  "last_name": "Smith",
  "biometric_id": "fingerprint_456",
  "date_of_birth": "1990-01-01",
  "gender": "female"
}
```
**Optional Fields**: All fields in the request body are optional
**Response**:
```json
{
  "message": "Profile updated successfully"
}
```

### POST /api/auth/forgot-password
**Description**: Initiate password reset. If an account with the provided email exists, a password reset token will be sent via SMS.
**Access**: Public
**Request Body**:
```json
{
  "email": "user@example.com"
}
```
**Required Fields**: `email`
**Response**:
```json
{
  "message": "If an account with that email exists, a password reset link has been sent."
}
```
**Note**: In testing mode (`TESTING=True` in .env), the response will also include the reset token for testing purposes.

### POST /api/auth/reset-password
**Description**: Reset password with a valid token
**Access**: Public
**Request Body**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "YourNewPassword123!"
}
```
**Required Fields**: `token`, `new_password`
**Response**:
```json
{
  "message": "Password has been reset successfully."
}
```

---

## 2. User Management

### POST /api/users
**Description**: Create new user. Coach Admins can only create users for their own branch and cannot create other admin users (Super Admin or Coach Admin roles).
**Access**: Super Admin, Coach Admin
**Request Body**:
```json
{
  "email": "newuser@example.com",
  "phone": "+1234567890",
  "full_name": "New User",
  "role": "coach_admin",
  "branch_id": "branch-uuid",
  "date_of_birth": "1990-01-01",
  "gender": "female"
}
```
**Response**:
```json
{
  "message": "User created successfully",
  "user_id": "user-uuid"
}
```

### GET /api/users
**Description**: Get users with filtering
**Access**: Super Admin, Coach Admin
**Query Parameters**:
- `role`: Filter by user role
- `branch_id`: Filter by branch
- `skip`: Skip records (pagination)
- `limit`: Limit records (default: 50)

**Response**:
```json
{
  "users": [
    {
      "id": "user-uuid",
      "email": "user@example.com",
      "full_name": "User Name",
      "role": "student",
      "is_active": true,
      "date_of_birth": "1990-01-01",
      "gender": "female"
    }
  ],
  "total": 1
}
```

### PUT /api/users/{user_id}
**Description**: Update user. Coach Admins can only update students in their own branch.
**Access**: Super Admin, Coach Admin
**Request Body**:
```json
{
  "email": "newemail@example.com",
  "phone": "+0987654321",
  "full_name": "Jane Doe",
  "biometric_id": "fingerprint_456",
  "date_of_birth": "1990-01-01",
  "gender": "female",
  "is_active": true
}

```
**Response**:
```json
{
  "message": "User updated successfully"
}
```

### DELETE /api/users/{user_id}
**Description**: Deactivate user
**Access**: Super Admin
**Response**:
```json
{
  "message": "User deactivated successfully"
}
```

### POST /api/users/{user_id}/force-password-reset
**Description**: Force a password reset for a user. A new temporary password will be generated and sent to the user via SMS and WhatsApp.
**Access**: Super Admin, Coach Admin
**Details**:
- Super Admins can reset the password for any user.
- Coach Admins can only reset passwords for Students and Coaches within their own branch.
**Response**:
```json
{
  "message": "Password for user [User's Full Name] has been reset and sent to them."
}
```

---

## 3. Branch Management

### POST /api/branches
**Description**: Create new branch
**Access**: Super Admin
**Request Body**:
```json
{
  "name": "Downtown Branch",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "pincode": "62701",
  "phone": "+1234567890",
  "email": "downtown@example.com",
  "manager_id": "manager-uuid",
  "business_hours": {
    "monday": {"open": "09:00", "close": "18:00"},
    "tuesday": {"open": "09:00", "close": "18:00"}
  }
}
```
**Response**:
```json
{
  "message": "Branch created successfully",
  "branch_id": "branch-uuid"
}
```

### GET /api/branches
**Description**: Get all branches
**Access**: All authenticated users
**Query Parameters**:
- `skip`: Skip records (pagination)
- `limit`: Limit records (default: 50)
**Response**:
```json
{
  "branches": [
    {
      "id": "branch-uuid",
      "name": "Downtown Branch",
      "address": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "pincode": "62701",
      "phone": "+1234567890",
      "email": "downtown@example.com",
      "manager_id": "manager-uuid",
      "is_active": true,
      "business_hours": {},
      "created_at": "2025-01-07T12:00:00Z",
      "updated_at": "2025-01-07T12:00:00Z"
    }
  ]
}
```

### GET /api/branches/{branch_id}
**Description**: Get branch by ID
**Access**: All authenticated users
**Response**:
```json
{
  "id": "branch-uuid",
  "name": "Downtown Branch",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "pincode": "62701",
  "phone": "+1234567890",
  "email": "downtown@example.com",
  "manager_id": "manager-uuid",
  "is_active": true,
  "business_hours": {},
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```

### PUT /api/branches/{branch_id}
**Description**: Update branch.
**Access**: Super Admin, Coach Admin (own branch only)
**Details**: Coach Admins can only update certain fields (e.g., name, address, phone) and cannot update the manager or active status.
**Request Body**:
```json
{
  "name": "Updated Branch Name",
  "address": "456 New St",
  "phone": "+0987654321"
}
```
**Response**:
```json
{
  "message": "Branch updated successfully"
}
```

### POST /api/branches/{branch_id}/holidays
**Description**: Create a new holiday for a branch.
**Access**: Super Admin, Coach Admin (own branch only)
**Request Body**:
```json
{
  "date": "2025-12-25",
  "description": "Christmas Day"
}
```
**Response**:
```json
{
  "id": "holiday-uuid",
  "branch_id": "branch-uuid",
  "date": "2025-12-25",
  "description": "Christmas Day",
  "created_at": "2025-01-07T12:00:00Z"
}
```

### GET /api/branches/{branch_id}/holidays
**Description**: Get all holidays for a specific branch.
**Access**: All authenticated users
**Response**:
```json
{
  "holidays": [
    {
      "id": "holiday-uuid",
      "branch_id": "branch-uuid",
      "date": "2025-12-25",
      "description": "Christmas Day",
      "created_at": "2025-01-07T12:00:00Z"
    }
  ]
}
```

### DELETE /api/branches/{branch_id}/holidays/{holiday_id}
**Description**: Delete a holiday for a branch.
**Access**: Super Admin, Coach Admin (own branch only)
**Response**: (No content) `204 No Content`

---

