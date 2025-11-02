# ALX Travel App - API Development for Listings and Bookings in Django

This repository contains the backend code for the ALX Travel App, which provides a comprehensive RESTful API for managing travel listings and bookings. The application is built using Django and Django REST Framework, following best practices for API design and documentation.

## Overview

The ALX Travel App API mirrors real-world travel booking platforms like Airbnb and Booking.com. It provides robust endpoints for managing property listings, bookings, and reviews, with full Swagger documentation for easy exploration and testing.

## Key Features

✅ **Complete CRUD Operations** - Create, Read, Update, Delete for Listings, Bookings, and Reviews  
✅ **RESTful API Design** - Following REST conventions with proper HTTP methods and status codes  
✅ **Swagger API Documentation** - Interactive, auto-generated API docs  
✅ **Authentication & Authorization** - Token and session-based authentication with permission checks  
✅ **Advanced Filtering & Search** - Filter listings by location, availability, sort by price, etc.  
✅ **Custom Actions** - Additional endpoints for common workflows (my_listings, my_bookings, cancel, confirm)  
✅ **Comprehensive Error Handling** - Meaningful error messages and proper HTTP status codes  
✅ **🆕 Chapa Payment Gateway Integration** - Secure payment processing for bookings  
✅ **🆕 Payment Transaction Tracking** - Full payment history and status management  
✅ **🆕 Asynchronous Task Processing** - Celery + RabbitMQ for background tasks  
✅ **🆕 Email Notifications** - Automated confirmation emails sent asynchronously without blocking requests  

## Project Structure

```
alx_travel_app/
├── alx_travel_app/              # Main Django project settings
│   ├── settings.py              # Django configuration (MySQL database, installed apps, middleware)
│   ├── urls.py                  # Main URL configuration with Swagger routes
│   ├── wsgi.py                  # WSGI application
│   ├── asgi.py                  # ASGI application
│   └── celery.py                # Celery configuration for async tasks
├── listings/                    # Django app for listings, bookings, and payments
│   ├── models.py                # Listing, Booking, Review, Payment models
│   ├── serializers.py           # DRF serializers for API (includes PaymentSerializer)
│   ├── views.py                 # ViewSets with CRUD operations (includes PaymentViewSet)
│   ├── tasks.py                 # Celery shared tasks for async email sending
│   ├── chapa_utils.py           # Chapa API integration utilities
│   ├── email_tasks.py           # Email notification functions (legacy)
│   ├── urls.py                  # API route configuration with routers
│   ├── admin.py                 # Django admin configuration
│   ├── tests.py                 # Unit tests
│   ├── tests_payment.py         # Payment integration tests
│   └── migrations/
│       ├── 0001_initial.py
│       └── 0002_payment.py      # Payment model migration
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── PAYMENT_INTEGRATION.md       # Detailed payment integration guide
├── TESTING_GUIDE_PAYMENTS.md    # Payment testing guide
├── QUICKSTART_PAYMENTS.md       # Quick start for payment setup
└── README.md                    # This file
```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Andrewkwame1/alx_travel_app_0x01.git
cd alx_travel_app_0x01
```

### 2. Create Virtual Environment

```bash
# For Windows (PowerShell)
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1

# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Database Configuration

Create a `.env` file in the project root with your database credentials:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration (MySQL)
DB_NAME=alx_travel_app
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Chapa Payment Gateway Configuration (NEW)
CHAPA_SECRET_KEY=CHASECK_TEST_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHAPA_API_URL=https://api.chapa.co/v1
CHAPA_CALLBACK_URL=http://localhost:8000/api/payments/verify/

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery Configuration (Optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Getting Chapa API Keys:**
1. Create account at https://developer.chapa.co/
2. Navigate to Settings/API Keys
3. Copy your Secret Key (starts with CHASECK_TEST_ for sandbox)
4. Add to `.env` as `CHAPA_SECRET_KEY`

### 5. Run Migrations

```bash
cd alx_travel_app
python manage.py migrate
```

### 6. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Documentation

### Access Swagger Documentation

- **Swagger UI**: http://localhost:8000/api/swagger/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

```

### 8. (Optional) Setup Celery with RabbitMQ for Asynchronous Email Notifications

This application supports asynchronous task processing using Celery with RabbitMQ as the message broker. This allows email notifications to be sent in the background without blocking the main request-response cycle.

#### Prerequisites

- **RabbitMQ**: Download from https://www.rabbitmq.com/download.html
- **Redis** (optional, used for task results): https://redis.io/

#### Installation Steps

##### Option A: Using RabbitMQ (Recommended for Production)

**Windows:**
```bash
# Download and install RabbitMQ from https://www.rabbitmq.com/install-windows.html
# Or use Chocolatey
choco install rabbitmq-server

# Start RabbitMQ
rabbitmq-server.bat  # or use Windows Services
```

**macOS:**
```bash
# Install with Homebrew
brew install rabbitmq

# Start RabbitMQ
brew services start rabbitmq
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
```

##### Option B: Using Redis (Alternative)

**Windows:**
```bash
# Download from https://github.com/microsoftarchive/redis/releases
# Or use WSL or Docker
docker run -d -p 6379:6379 redis:latest
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

#### Configure Celery in `.env`

```env
# Message Broker Configuration (RabbitMQ)
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Result Backend Configuration (Redis)
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com
```

#### Running Celery Worker

**Windows (PowerShell):**
```bash
# In a new terminal
celery -A alx_travel_app worker -l info
```

**macOS/Linux:**
```bash
# In a new terminal
celery -A alx_travel_app worker -l info
```

#### Running Celery Beat (Task Scheduler - Optional)

```bash
celery -A alx_travel_app beat -l info
```

---

## Asynchronous Task Processing with Celery

The application uses Celery to handle background tasks asynchronously. Currently implemented tasks include:

### 🆕 Email Notification Tasks

#### Available Tasks

1. **`send_booking_confirmation_email_task`** - Sends booking confirmation to guests
   - Triggered when a booking is created
   - Email includes booking details

2. **`send_payment_confirmation_email_task`** - Sends payment confirmation email
   - Triggered when payment is successfully verified
   - Email includes payment and booking details
   - Retries up to 3 times on failure with exponential backoff

3. **`send_payment_failure_email_task`** - Notifies about payment failure
   - Triggered when payment fails
   - Includes error details and retry instructions

### Task Features

✅ **Asynchronous Execution** - Emails sent in background workers  
✅ **Automatic Retries** - Failed tasks retry up to 3 times with exponential backoff  
✅ **Logging** - All task executions logged for monitoring  
✅ **Non-blocking** - User requests complete immediately while email is processing  
✅ **Scalable** - Multiple workers can be started for high throughput  

### Task Configuration

Key settings in `settings.py`:

```python
# Message Broker
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# Result Backend
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Task Settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
```

### How Tasks are Triggered

#### When a Payment is Completed:

```python
# In PaymentViewSet.verify_status()
send_payment_confirmation_email_task.delay(
    booking_id=str(payment.booking.booking_id),
    guest_email=payment.booking.guest.email,
    guest_name=payment.booking.guest.first_name,
    # ... other parameters
)
```

The `.delay()` method sends the task to the message broker immediately and returns control to the caller.

### Testing Celery Tasks

#### 1. Verify Worker is Running

```bash
# Terminal should show:
# - Connected to amqp://guest:guest@localhost:5672//
# - [*] Ready to accept tasks
```

#### 2. Test Email Task (Manually)

Create a test script `test_celery.py`:

```python
from listings.tasks import send_payment_confirmation_email_task

# Trigger task
result = send_payment_confirmation_email_task.delay(
    booking_id='test-booking-123',
    guest_email='test@example.com',
    guest_name='John Doe',
    listing_title='Cozy Apartment',
    listing_location='Downtown NYC',
    check_in_date='2025-02-01',
    check_out_date='2025-02-05',
    amount='500.00',
    currency='USD',
    payment_id='payment-123',
    transaction_id='trans-456'
)

# Check task status
print(f"Task ID: {result.id}")
print(f"Task Status: {result.status}")
```

Run it:
```bash
python manage.py shell < test_celery.py
```

#### 3. Monitor Tasks with Flower (Web UI)

```bash
# Install Flower
pip install flower

# Start Flower
celery -A alx_travel_app events

# Open browser
http://localhost:5555/
```

---

## Monitoring and Debugging

### View Celery Worker Logs

```bash
celery -A alx_travel_app worker -l debug
```

### Check Task Status

```python
# In Django shell
from listings.tasks import send_payment_confirmation_email_task
from celery.result import AsyncResult

# Get task result
result = AsyncResult('task-id-here')
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Ensure RabbitMQ is running: `rabbitmq-server` |
| Tasks not executing | Check worker is running in separate terminal |
| Emails not sending | Verify EMAIL_* settings in .env |
| Task stuck | Check logs, restart worker, increase CELERY_TASK_TIME_LIMIT |

---


All API endpoints are under `/api/`

```
Base URL: http://localhost:8000/api/
```

## Available Endpoints

### Listings Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/listings/` | List all listings | No |
| POST | `/api/listings/` | Create a new listing | Yes |
| GET | `/api/listings/{id}/` | Get listing details | No |
| PUT | `/api/listings/{id}/` | Update a listing | Yes* |
| DELETE | `/api/listings/{id}/` | Delete a listing | Yes* |
| GET | `/api/listings/{id}/reviews/` | Get reviews for a listing | No |
| GET | `/api/listings/my_listings/` | Get your listings | Yes |
| GET | `/api/listings/available/` | Get available listings | No |

### Bookings Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/bookings/` | List relevant bookings | Yes |
| POST | `/api/bookings/` | Create a new booking | Yes |
| GET | `/api/bookings/{id}/` | Get booking details | Yes |
| PUT | `/api/bookings/{id}/` | Update a booking | Yes* |
| DELETE | `/api/bookings/{id}/` | Delete a booking | Yes* |
| GET | `/api/bookings/my_bookings/` | Get your bookings | Yes |
| PATCH | `/api/bookings/{id}/cancel/` | Cancel a booking | Yes* |
| PATCH | `/api/bookings/{id}/confirm/` | Confirm a booking | Yes** |

### Reviews Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/reviews/` | List all reviews | No |
| POST | `/api/reviews/` | Create a new review | Yes |
| GET | `/api/reviews/{id}/` | Get review details | No |
| PUT | `/api/reviews/{id}/` | Update a review | Yes* |
| DELETE | `/api/reviews/{id}/` | Delete a review | Yes* |

### 🆕 Payments Management (Chapa Integration)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/payments/` | List your payments | Yes |
| GET | `/api/payments/{id}/` | Get payment details | Yes* |
| POST | `/api/bookings/{id}/initiate_payment/` | Initiate payment for booking | Yes* |
| POST | `/api/payments/{id}/verify_status/` | Verify payment status | Yes* |
| POST | `/api/payments/verify/` | Webhook callback verification | No |

**Auth Legend:**
- `Yes` = Authentication required
- `No` = Public endpoint
- `Yes*` = Only resource owner
- `Yes**` = Only listing host

## 🆕 Payment Integration Documentation

For comprehensive payment integration guide, see:
- **[PAYMENT_INTEGRATION.md](PAYMENT_INTEGRATION.md)** - Complete integration documentation
- **[TESTING_GUIDE_PAYMENTS.md](TESTING_GUIDE_PAYMENTS.md)** - Step-by-step testing guide
- **[QUICKSTART_PAYMENTS.md](QUICKSTART_PAYMENTS.md)** - Quick start setup

### Payment Flow Example

```
1. User creates booking (Payment created automatically)
2. User calls POST /api/bookings/{id}/initiate_payment/
3. Receives checkout_url from Chapa
4. User completes payment on Chapa
5. User calls POST /api/payments/{id}/verify_status/
6. On success:
   - Payment status → 'completed'
   - Booking status → 'confirmed'
   - Confirmation email sent
```

### 1. List All Listings

**Request:**
```bash
curl -X GET http://localhost:8000/api/listings/
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "listing_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Cozy Apartment in Downtown",
      "description": "Beautiful 2-bedroom apartment...",
      "price_per_night": "150.00",
      "location": "New York",
      "amenities": "WiFi, AC, Kitchen, Laundry",
      "host": {
        "id": 1,
        "username": "john_host",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
      },
      "is_available": true,
      "created_at": "2025-10-20T10:30:00Z",
      "updated_at": "2025-10-20T10:30:00Z",
      "reviews": [],
      "average_rating": 0,
      "review_count": 0
    }
  ]
}
```

### 2. Create a New Listing

**Request:**
```bash
curl -X POST http://localhost:8000/api/listings/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beachfront Villa",
    "description": "Luxury villa with ocean view",
    "price_per_night": "250.00",
    "location": "Miami Beach",
    "amenities": "Pool, WiFi, AC, Kitchen, Parking",
    "is_available": true
  }'
```

**Response (201 Created):**
```json
{
  "listing_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Beachfront Villa",
  "description": "Luxury villa with ocean view",
  "price_per_night": "250.00",
  "location": "Miami Beach",
  "amenities": "Pool, WiFi, AC, Kitchen, Parking",
  "host": {
    "id": 2,
    "username": "jane_host",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com"
  },
  "is_available": true,
  "created_at": "2025-10-24T15:45:00Z",
  "updated_at": "2025-10-24T15:45:00Z",
  "reviews": [],
  "average_rating": 0,
  "review_count": 0
}
```

### 3. Create a Booking

**Request:**
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "550e8400-e29b-41d4-a716-446655440000",
    "check_in_date": "2025-11-01",
    "check_out_date": "2025-11-05",
    "total_price": "600.00"
  }'
```

**Response (201 Created):**
```json
{
  "booking_id": "550e8400-e29b-41d4-a716-446655440100",
  "listing": {
    "listing_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Cozy Apartment in Downtown",
    "description": "Beautiful 2-bedroom apartment...",
    "price_per_night": "150.00",
    "location": "New York",
    "amenities": "WiFi, AC, Kitchen, Laundry",
    "host": {...},
    "is_available": true,
    "created_at": "2025-10-20T10:30:00Z",
    "updated_at": "2025-10-20T10:30:00Z",
    "reviews": [],
    "average_rating": 0,
    "review_count": 0
  },
  "guest": {
    "id": 3,
    "username": "guest_user",
    "first_name": "Guest",
    "last_name": "User",
    "email": "guest@example.com"
  },
  "check_in_date": "2025-11-01",
  "check_out_date": "2025-11-05",
  "total_price": "600.00",
  "status": "pending",
  "created_at": "2025-10-24T16:00:00Z"
}
```

### 4. Create a Review

**Request:**
```bash
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "550e8400-e29b-41d4-a716-446655440000",
    "rating": 5,
    "comment": "Amazing place! Highly recommended."
  }'
```

**Response (201 Created):**
```json
{
  "review_id": "550e8400-e29b-41d4-a716-446655440200",
  "listing": {
    "listing_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Cozy Apartment in Downtown"
  },
  "reviewer": {
    "id": 3,
    "username": "guest_user",
    "first_name": "Guest",
    "last_name": "User",
    "email": "guest@example.com"
  },
  "rating": 5,
  "comment": "Amazing place! Highly recommended.",
  "created_at": "2025-10-24T16:05:00Z"
}
```

### 5. Cancel a Booking

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/bookings/550e8400-e29b-41d4-a716-446655440100/cancel/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN"
```

**Response (200 OK):**
```json
{
  "booking_id": "550e8400-e29b-41d4-a716-446655440100",
  "listing": {...},
  "guest": {...},
  "check_in_date": "2025-11-01",
  "check_out_date": "2025-11-05",
  "total_price": "600.00",
  "status": "cancelled",
  "created_at": "2025-10-24T16:00:00Z"
}
```

## Query Parameters & Filtering

### Filter Listings by Location

```bash
curl -X GET "http://localhost:8000/api/listings/?location=New+York"
```

### Filter Listings by Availability

```bash
curl -X GET "http://localhost:8000/api/listings/?is_available=true"
```

### Search Listings

```bash
curl -X GET "http://localhost:8000/api/listings/?search=beachfront"
```

### Sort Listings by Price (Ascending)

```bash
curl -X GET "http://localhost:8000/api/listings/?ordering=price_per_night"
```

### Sort Listings by Price (Descending)

```bash
curl -X GET "http://localhost:8000/api/listings/?ordering=-price_per_night"
```

### Filter Bookings by Status

```bash
curl -X GET "http://localhost:8000/api/bookings/?status=confirmed" \
  -H "Authorization: Token YOUR_AUTH_TOKEN"
```

## Authentication

### Token Authentication Setup

1. **Create a Token for a User** (Django shell):
```bash
python manage.py shell
```

```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='john_host')
token, created = Token.objects.get_or_create(user=user)
print(token.key)
```

2. **Use Token in API Requests**:
```bash
curl -X GET http://localhost:8000/api/listings/my_listings/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN_HERE"
```

## Testing API Endpoints

### Using Postman

1. **Download Postman** from https://www.postman.com/downloads/
2. **Create a new Collection** for ALX Travel App
3. **Set Base URL** to `http://localhost:8000`
4. **Import Variables**:
   - `token` - Your auth token
   - `listing_id` - UUID of a listing
   - `booking_id` - UUID of a booking

### Sample Postman Workflow

#### Step 1: Register/Login User
- Create a user account or login to get authentication token
- Store the token in Postman variables

#### Step 2: Create a Listing
- **Method**: POST
- **URL**: `{{base_url}}/api/listings/`
- **Headers**: `Authorization: Token {{token}}`
- **Body**:
```json
{
  "title": "Mountain Cabin",
  "description": "Cozy cabin in the mountains",
  "price_per_night": "100.00",
  "location": "Colorado",
  "amenities": "Fireplace, WiFi, Kitchen",
  "is_available": true
}
```

#### Step 3: List Bookings
- **Method**: GET
- **URL**: `{{base_url}}/api/bookings/`
- **Headers**: `Authorization: Token {{token}}`

#### Step 4: Create a Booking
- **Method**: POST
- **URL**: `{{base_url}}/api/bookings/`
- **Headers**: `Authorization: Token {{token}}`
- **Body**:
```json
{
  "listing_id": "550e8400-e29b-41d4-a716-446655440000",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-10",
  "total_price": "900.00"
}
```

#### Step 5: Cancel a Booking
- **Method**: PATCH
- **URL**: `{{base_url}}/api/bookings/{{booking_id}}/cancel/`
- **Headers**: `Authorization: Token {{token}}`

### Using cURL in Terminal

Test all endpoints using cURL (or PowerShell on Windows):

```powershell
# Get all listings
Invoke-WebRequest -Uri "http://localhost:8000/api/listings/" -Method Get

# Create listing (requires auth token)
$headers = @{
    "Authorization" = "Token YOUR_TOKEN"
    "Content-Type" = "application/json"
}
$body = @{
    title = "Beachfront Property"
    description = "Beautiful beach house"
    price_per_night = "200.00"
    location = "California"
    amenities = "Pool, WiFi, AC"
    is_available = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/listings/" -Method Post -Headers $headers -Body $body
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "check_in_date": ["Check-out date must be after check-in date."]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You can only update your own listings."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Technology Stack

- **Django 5.2.6** - Web framework
- **Django REST Framework 3.16.1** - API development
- **drf-yasg 1.21.10** - Swagger/OpenAPI documentation
- **django-cors-headers 4.7.0** - CORS support
- **mysql-connector-python 9.4.0** - MySQL database driver
- **Celery 5.5.3** - Asynchronous task processing
- **Python 3.8+**

## Running Tests

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test -v 2

# Run specific app tests
python manage.py test listings
```

## Development Workflow

1. Create a feature branch
2. Make changes
3. Test endpoints with Swagger or Postman
4. Run migrations if models changed
5. Commit and push
6. Submit PR for review

## Common Commands

```bash
# Start development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Load test data
python manage.py seed

# Reset database
python manage.py flush
```

## Deployment Considerations

- Set `DEBUG=False` in production
- Use environment variables for sensitive data
- Configure allowed hosts
- Use a production-grade database (PostgreSQL recommended)
- Set up HTTPS/SSL
- Configure proper CORS settings
- Use a production WSGI server (Gunicorn, uWSGI)

## Troubleshooting

### Database Connection Error
- Ensure MySQL is running
- Check credentials in `.env` file
- Verify database name exists

### Authentication Token Not Working
- Ensure token is valid: `python manage.py shell`
- Check token format in header: `Authorization: Token your_token`
- Verify user hasn't been deleted

### CORS Issues
- Check `CORS_ALLOW_ALL_ORIGINS` in `settings.py`
- Configure specific origins if needed

### Migration Errors
- Delete old migrations and recreate: `python manage.py makemigrations --empty listings --name reset`
- Check model definitions for conflicts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test thoroughly with Postman/Swagger
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

**Repository**: https://github.com/Andrewkwame1/alx_travel_app_0x01

## Author

Your Name/Your Organization

## Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Guide](https://www.django-rest-framework.org/)
- [drf-yasg Documentation](https://drf-yasg.readthedocs.io/)
- [RESTful API Best Practices](https://restfulapi.net/)
- [Postman Learning Center](https://learning.postman.com/)