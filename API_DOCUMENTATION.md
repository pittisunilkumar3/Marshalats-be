# Student Management System API Documentation

## Overview
This is a comprehensive Student Management System API built with FastAPI, supporting role-based access for Super Admin, Staff (Coach Admin), Coaches, and Students. The API features nested data structures, comprehensive branch management, and JWT-based authentication.

## Base URL
```
Production: https://edumanage-44.preview.dev.com/api
Development: http://localhost:8001/api
```

## Authentication
The API uses JWT (JSON Web Token) for authentication. All protected endpoints require a valid bearer token.

### Getting a Bearer Token
1. **Login**: POST `/api/auth/login` with email and password
2. **Extract Token**: Copy the `access_token` from the response
3. **Use Token**: Include in Authorization header for all protected requests

### Authentication Header Format
```
Authorization: Bearer <your_jwt_token>
```

### Example Authentication Flow
```bash
# Step 1: Login to get token
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Step 2: Use token in protected requests
curl -X GET http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json"
```

### Postman Setup
1. Login request → Tests tab → Add: `pm.globals.set("token", pm.response.json().access_token);`
2. Use `{{token}}` in Authorization header: `Bearer {{token}}`

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

## User Roles & Permissions
- **super_admin**: Full system access, manages branches, courses, users, and system settings
- **coach_admin**: Branch-level management, student enrollment, course scheduling, branch operations
- **coach**: Limited access to assigned courses and students, attendance tracking
- **student**: Personal profile, course enrollment, attendance viewing, payment history

## Available User Role Values
When creating or updating users, use these exact role values:
- `"super_admin"` - System administrator with full access
- `"coach_admin"` - Branch manager with branch-level permissions  
- `"coach"` - Instructor with course-specific access
- `"student"` - End user with personal account access

## Data Structure Overview
The API uses nested JSON structures for complex entities:
- **Users**: Include nested `course` and `branch` objects
- **Branches**: Comprehensive nested structure with address, operational details, assignments, and bank details
- **Consistent Storage**: Data is stored and returned in the same nested format

## Testing & Development Tools

### Available Test Scripts
- `test_auth_bearer.py` - Comprehensive authentication testing
- `simple_auth_test.py` - Step-by-step authentication guide
- `Student_Management_API_Bearer_Auth.postman_collection.json` - Postman collection

### Quick Test Commands
```bash
# Test authentication
python test_auth_bearer.py

# Show step-by-step auth flow
python simple_auth_test.py

# Test specific endpoints
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@test.com", "password": "SuperAdmin123!"}'
```

### Demo Users
- **Super Admin**: `superadmin@test.com` / `SuperAdmin123!`
- **Student**: Available after registration

---

# API Endpoints

## 1. Authentication & User Management

### POST /api/auth/register
**Description**: Register a new student (public endpoint). Creates user with nested course and branch information. Upon successful registration, an SMS containing login credentials will be sent to the registered phone number.

**Access**: Public (no authentication required)

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

**Field Specifications**:
- `date_of_birth`: YYYY-MM-DD format (e.g., "2005-08-15")
- `gender`: Any string value (e.g., "male", "female", "other")
- `course`: If provided, all nested fields are required
- `branch`: If provided, all nested fields are required
- `password`: Auto-generated if not provided

**Response**:
```json
{
  "message": "User registered successfully",
  "user_id": "0b44cebf-f0e1-4716-b521-0e3ba290e5c4"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "phone": "+1234567890",
    "first_name": "New",
    "last_name": "User",
    "role": "student",
    "password": "UserPass123!",
    "date_of_birth": "1995-01-01",
    "gender": "male",
    "course": {
      "category_id": "cat-123",
      "course_id": "course-456", 
      "duration": "3-months"
    },
    "branch": {
      "location_id": "loc-789",
      "branch_id": "branch-101"
    }
  }'
```

**Notes**: 
- SMS with login credentials sent to provided phone number
- If `password` not provided, random password generated
- User data stored with nested structure intact
- `full_name` auto-generated from `first_name` + `last_name`



### POST /api/auth/login
**Description**: User login - authenticate user and receive JWT bearer token

**Access**: Public (no authentication required)

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

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@test.com",
    "password": "SuperAdmin123!"
  }'
```

**Response Fields**:
- `access_token`: JWT token for authentication (use in Authorization header)
- `token_type`: Always "bearer"
- `user`: Complete user profile with nested objects
- Nested `course` and `branch` objects (null if not set during registration)

**Usage**: Save the `access_token` and use as `Authorization: Bearer <token>` for all protected endpoints.

### GET /api/auth/me
**Description**: Get current authenticated user information

**Access**: All authenticated users

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
  "biometric_id": "fingerprint_123",
  "is_active": true,
  "date_of_birth": "2005-08-15",
  "gender": "male",
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json"
```

**Notes**: 
- Returns complete user profile for current authenticated user
- `date_of_birth`, `gender`, `biometric_id` may be `null` if not set
- Timestamps in ISO 8601 format

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
**Description**: Create new branch with comprehensive nested structure

**Access**: Super Admin only

**Headers**:
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "branch": {
    "name": "Rock martial arts",
    "code": "RMA01",
    "email": "yourname@email.com",
    "phone": "+13455672356",
    "address": {
      "line1": "928#123",
      "area": "Madhapur",
      "city": "Hyderabad",
      "state": "Telangana",
      "pincode": "500089",
      "country": "India"
    }
  },
  "manager_id": "manager-uuid-1234",
  "operational_details": {
    "courses_offered": ["Rock martial arts"],
    "timings": [
      { "day": "Monday", "open": "07:00", "close": "19:00" },
      { "day": "Tuesday", "open": "07:00", "close": "19:00" }
    ],
    "holidays": ["2025-10-02", "2025-12-25"]
  },
  "assignments": {
    "accessories_available": true,
    "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
    "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
  },
  "bank_details": {
    "bank_name": "State Bank of India",
    "account_number": "XXXXXXXXXXXX",
    "upi_id": "name@ybl"
  }
}
```

**Required Fields**: All nested objects and their fields are required

**Field Specifications**:
- `assignments.courses`: Array of course IDs (UUIDs) for database relationships
- `assignments.branch_admins`: Array of user IDs (UUIDs) for coaches who can manage this branch
- `operational_details.courses_offered`: Array of course names for display purposes
- `operational_details.holidays`: Array of date strings in YYYY-MM-DD format
- `operational_details.timings`: Array with day, open/close times in HH:MM format

**Response**:
```json
{
  "message": "Branch created successfully",
  "branch_id": "branch-uuid"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8001/api/branches \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": {
      "name": "Test Branch",
      "code": "TB01",
      "email": "test@branch.com",
      "phone": "+1234567890",
      "address": {
        "line1": "123 Test St",
        "area": "Test Area",
        "city": "Test City",
        "state": "Test State",
        "pincode": "123456",
        "country": "India"
      }
    },
    "manager_id": "manager-uuid",
    "operational_details": {
      "courses_offered": ["Martial Arts"],
      "timings": [
        {"day": "Monday", "open": "09:00", "close": "18:00"}
      ],
      "holidays": ["2025-12-25"]
    },
    "assignments": {
      "accessories_available": true,
      "courses": ["course-uuid-1"],
      "branch_admins": ["admin-uuid-1"]
    },
    "bank_details": {
      "bank_name": "Test Bank",
      "account_number": "1234567890",
      "upi_id": "test@upi"
    }
  }'
```

### GET /api/branches
**Description**: Get all branches with comprehensive nested structure
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
      "branch": {
        "name": "Rock martial arts",
        "code": "RMA01",
        "email": "yourname@email.com",
        "phone": "+13455672356",
        "address": {
          "line1": "928#123",
          "area": "Madhapur",
          "city": "Hyderabad",
          "state": "Telangana",
          "pincode": "500089",
          "country": "India"
        }
      },
      "manager_id": "manager-uuid-1234",
      "operational_details": {
        "courses_offered": ["Rock martial arts"],
        "timings": [
          { "day": "Monday", "open": "07:00", "close": "19:00" },
          { "day": "Tuesday", "open": "07:00", "close": "19:00" }
        ],
        "holidays": ["2025-10-02", "2025-12-25"]
      },
      "assignments": {
        "accessories_available": true,
        "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
        "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
      },
      "bank_details": {
        "bank_name": "State Bank of India",
        "account_number": "XXXXXXXXXXXX",
        "upi_id": "name@ybl"
      },
      "is_active": true,
      "created_at": "2025-01-07T12:00:00Z",
      "updated_at": "2025-01-07T12:00:00Z"
    }
  ]
}
```

### GET /api/branches/{branch_id}
**Description**: Get branch by ID with comprehensive nested structure
**Access**: All authenticated users
**Response**:
```json
{
  "id": "branch-uuid",
  "branch": {
    "name": "Rock martial arts",
    "code": "RMA01",
    "email": "yourname@email.com",
    "phone": "+13455672356",
    "address": {
      "line1": "928#123",
      "area": "Madhapur",
      "city": "Hyderabad",
      "state": "Telangana",
      "pincode": "500089",
      "country": "India"
    }
  },
  "manager_id": "manager-uuid-1234",
  "operational_details": {
    "courses_offered": ["Rock martial arts"],
    "timings": [
      { "day": "Monday", "open": "07:00", "close": "19:00" },
      { "day": "Tuesday", "open": "07:00", "close": "19:00" }
    ],
    "holidays": ["2025-10-02", "2025-12-25"]
  },
  "assignments": {
    "accessories_available": true,
    "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
    "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
  },
  "bank_details": {
    "bank_name": "State Bank of India",
    "account_number": "XXXXXXXXXXXX",
    "upi_id": "name@ybl"
  },
  "is_active": true,
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```

### PUT /api/branches/{branch_id}
**Description**: Update branch with comprehensive nested structure.
**Access**: Super Admin, Coach Admin (own branch only)
**Details**: Coach Admins can only update branches where they are listed in the `assignments.branch_admins` array and cannot update certain fields (manager_id, is_active, assignments, bank_details).
**Request Body** (all fields are optional):
```json
{
  "branch": {
    "name": "Updated Branch Name",
    "code": "UBN01",
    "email": "updated@email.com",
    "phone": "+1234567890",
    "address": {
      "line1": "456 New St",
      "area": "New Area",
      "city": "New City",
      "state": "New State", 
      "pincode": "123456",
      "country": "India"
    }
  },
  "operational_details": {
    "courses_offered": ["Updated Course"],
    "timings": [
      { "day": "Monday", "open": "08:00", "close": "18:00" }
    ],
    "holidays": ["2025-12-25"]
  }
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

# Complete API Usage Examples

## Full Authentication Flow

### 1. User Registration (Public)
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newstudent@example.com",
    "phone": "+1234567890",
    "first_name": "New",
    "last_name": "Student",
    "role": "student",
    "password": "StudentPass123!",
    "date_of_birth": "2000-01-01",
    "gender": "male",
    "course": {
      "category_id": "cat-martial-arts",
      "course_id": "course-karate-101",
      "duration": "6-months"
    },
    "branch": {
      "location_id": "loc-downtown",
      "branch_id": "branch-main"
    }
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newstudent@example.com",
    "password": "StudentPass123!"
  }'
```
**Extract the `access_token` from response for subsequent requests.**

### 3. Get Current User Info
```bash
curl -X GET http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## Branch Management Examples

### 1. Create Comprehensive Branch (Super Admin Only)
```bash
curl -X POST http://localhost:8001/api/branches \
  -H "Authorization: Bearer YOUR_SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": {
      "name": "Elite Martial Arts Academy",
      "code": "EMAA01",
      "email": "elite@martialarts.com",
      "phone": "+1555123456",
      "address": {
        "line1": "789 Warrior Way",
        "area": "Dojo District",
        "city": "Martial City",
        "state": "Combat State",
        "pincode": "54321",
        "country": "India"
      }
    },
    "manager_id": "mgr-john-doe-uuid",
    "operational_details": {
      "courses_offered": ["Karate", "Taekwondo", "Jiu-Jitsu", "Kickboxing"],
      "timings": [
        {"day": "Monday", "open": "06:00", "close": "22:00"},
        {"day": "Tuesday", "open": "06:00", "close": "22:00"},
        {"day": "Wednesday", "open": "06:00", "close": "22:00"},
        {"day": "Thursday", "open": "06:00", "close": "22:00"},
        {"day": "Friday", "open": "06:00", "close": "22:00"},
        {"day": "Saturday", "open": "08:00", "close": "20:00"},
        {"day": "Sunday", "open": "08:00", "close": "18:00"}
      ],
      "holidays": ["2025-01-01", "2025-08-15", "2025-10-02", "2025-12-25"]
    },
    "assignments": {
      "accessories_available": true,
      "courses": [
        "course-karate-uuid",
        "course-taekwondo-uuid", 
        "course-jiujitsu-uuid",
        "course-kickboxing-uuid"
      ],
      "branch_admins": [
        "admin-sarah-uuid",
        "admin-mike-uuid"
      ]
    },
    "bank_details": {
      "bank_name": "First National Bank",
      "account_number": "9876543210",
      "upi_id": "elite@okaxis"
    }
  }'
```

### 2. Get All Branches
```bash
curl -X GET http://localhost:8001/api/branches \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Get Specific Branch
```bash
curl -X GET http://localhost:8001/api/branches/BRANCH_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## User Management Examples

### 1. Get All Users (Admin Only)
```bash
curl -X GET http://localhost:8001/api/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

### 2. Create New User (Admin Only)
```bash
curl -X POST http://localhost:8001/api/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newcoach@example.com",
    "phone": "+1234567890",
    "first_name": "New",
    "last_name": "Coach",
    "role": "coach",
    "date_of_birth": "1985-05-15",
    "gender": "female"
  }'
```

## Common Response Patterns

### Success Response Format
```json
{
  "message": "Operation completed successfully",
  "data": { /* relevant data */ }
}
```

### Error Response Format
```json
{
  "detail": "Error description or validation errors array"
}
```

### Nested Data Structure Example
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "course": {
      "category_id": "cat-uuid",
      "course_id": "course-uuid", 
      "duration": "6-months"
    },
    "branch": {
      "location_id": "loc-uuid",
      "branch_id": "branch-uuid"
    }
  }
}
```

## Testing Tools & Resources

### Python Test Scripts
```bash
# Comprehensive authentication testing
python test_auth_bearer.py

# Step-by-step authentication guide
python simple_auth_test.py

# Test complete branch API functionality
python test_complete_branch_api.py
```

### Postman Collection
Import `Student_Management_API_Bearer_Auth.postman_collection.json` into Postman for GUI testing with automatic token management.

### Demo Credentials
- **Super Admin**: `superadmin@test.com` / `SuperAdmin123!`
- **Test Users**: Created via registration endpoint

### API Features Summary
- ✅ **JWT Bearer Token Authentication**
- ✅ **Role-Based Access Control** (Super Admin, Coach Admin, Coach, Student)
- ✅ **Nested Data Structures** (User courses/branches, Branch comprehensive details)
- ✅ **Comprehensive Branch Management** (Address, Operations, Assignments, Banking)
- ✅ **Secure Endpoints** (All protected routes require authentication)
- ✅ **Consistent Data Storage** (Nested structures preserved in database)
- ✅ **RESTful Design** (Standard HTTP methods and status codes)

---

