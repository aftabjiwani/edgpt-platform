# 🔌 EdGPT Platform API Documentation

This document provides comprehensive API documentation for the EdGPT Platform, including all endpoints, request/response formats, and integration examples.

## 📋 Table of Contents

- [Authentication](#authentication)
- [Public Endpoints](#public-endpoints)
- [Protected Endpoints](#protected-endpoints)
- [Admin Endpoints](#admin-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## 🔐 Authentication

### Session-Based Authentication

The EdGPT Platform uses session-based authentication for web interface access.

#### Login Process
```http
POST /login
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=userpassword
```

#### Response
```json
{
    "success": true,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "is_admin": false
    },
    "redirect": "/dashboard"
}
```

#### Session Management
- Sessions are stored server-side with secure cookies
- Session timeout: 24 hours of inactivity
- Automatic session renewal on activity

## 🌐 Public Endpoints

### Health Check

Check the application status and available domains.

```http
GET /health
```

#### Response
```json
{
    "status": "healthy",
    "timestamp": "2025-01-07T12:00:00Z",
    "domains": [
        "edgpt.ai",
        "gptsites.ai",
        "lawfirmgpt.ai",
        "cpafirm.ai",
        "taxprepgpt.ai",
        "businessbrokergpt.ai"
    ],
    "version": "2.0.0"
}
```

### Landing Pages

Domain-specific landing pages with automatic template routing.

```http
GET /
Host: {domain}
```

#### Supported Domains
- `edgpt.ai` → Education template
- `gptsites.ai` → Business template
- `lawfirmgpt.ai` → Legal template
- `cpafirm.ai` → Accounting template
- `taxprepgpt.ai` → Tax preparation template
- `businessbrokergpt.ai` → Business brokerage template

#### Response
Returns HTML template with domain-specific content and branding.

### Trial Signup

Submit trial signup requests for website conversion.

```http
POST /signup
Content-Type: application/x-www-form-urlencoded

email=customer@example.com&website_url=https://example.com&business_name=Example%20Business&phone=555-1234
```

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | Yes | Customer email address |
| `website_url` | string | Yes | Website URL to convert |
| `business_name` | string | No | Business name |
| `phone` | string | No | Contact phone number |

#### Response
```json
{
    "success": true,
    "message": "Trial request submitted successfully",
    "redirect": "/conversion",
    "trial_id": 123
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Email and website URL are required",
    "code": "VALIDATION_ERROR"
}
```

## 🔒 Protected Endpoints

### User Dashboard

Access user dashboard (requires authentication).

```http
GET /dashboard
Cookie: session=...
```

#### Response
Returns HTML dashboard with user-specific content and tools.

### User Profile

Get or update user profile information.

```http
GET /api/profile
Cookie: session=...
```

#### Response
```json
{
    "success": true,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "business_name": "Example Business",
        "website_url": "https://example.com",
        "phone": "555-1234",
        "created_at": "2025-01-01T00:00:00Z"
    }
}
```

### Update Profile

```http
PUT /api/profile
Content-Type: application/json
Cookie: session=...

{
    "business_name": "Updated Business Name",
    "phone": "555-5678"
}
```

## 👑 Admin Endpoints

### Admin Dashboard

Access admin dashboard (requires admin privileges).

```http
GET /admin/dashboard
Cookie: session=...
```

#### Response
Returns HTML admin interface with analytics and management tools.

### Generate Integration Code

Generate customizable widget integration code for customers.

```http
POST /api/generate-code
Content-Type: application/json
Cookie: session=...

{
    "domain": "gptsites.ai",
    "customization": {
        "color": "#3b82f6",
        "position": "bottom-right",
        "size": "medium"
    }
}
```

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | string | Yes | Target domain for branding |
| `customization.color` | string | No | Widget color (hex) |
| `customization.position` | string | No | Widget position |
| `customization.size` | string | No | Widget size |

#### Response
```json
{
    "success": true,
    "html": "<!-- Generated HTML code -->",
    "css": "/* Generated CSS styles */",
    "config": {
        "domain": "gptsites.ai",
        "name": "GPTSites",
        "color": "#3b82f6",
        "icon": "💼"
    },
    "customization": {
        "color": "#3b82f6",
        "position": "bottom-right",
        "size": "medium"
    }
}
```

### Analytics Data

Get analytics data for admin dashboard.

```http
GET /api/analytics
Cookie: session=...
```

#### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | string | Time period (7d, 30d, 90d) |
| `domain` | string | Filter by specific domain |

#### Response
```json
{
    "success": true,
    "data": {
        "domain_views": [
            {
                "domain": "edgpt.ai",
                "views": 1250
            },
            {
                "domain": "gptsites.ai",
                "views": 980
            }
        ],
        "daily_views": [
            {
                "date": "2025-01-07",
                "views": 145
            },
            {
                "date": "2025-01-06",
                "views": 132
            }
        ],
        "trial_signups": 45,
        "conversion_rate": 3.6
    }
}
```

### User Management

Get list of users (admin only).

```http
GET /api/users
Cookie: session=...
```

#### Response
```json
{
    "success": true,
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "business_name": "Example Business",
            "created_at": "2025-01-01T00:00:00Z",
            "is_admin": false
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20
}
```

### Trial Requests

Get trial signup requests (admin only).

```http
GET /api/trial-requests
Cookie: session=...
```

#### Response
```json
{
    "success": true,
    "requests": [
        {
            "id": 123,
            "email": "customer@example.com",
            "website_url": "https://example.com",
            "business_name": "Example Business",
            "phone": "555-1234",
            "status": "pending",
            "created_at": "2025-01-07T10:30:00Z"
        }
    ],
    "total": 1
}
```

## ❌ Error Handling

### Error Response Format

All API endpoints return errors in a consistent format:

```json
{
    "success": false,
    "error": "Error message description",
    "code": "ERROR_CODE",
    "details": {
        "field": "Additional error details"
    }
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Internal Server Error |

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_REQUIRED` | User must be logged in |
| `INSUFFICIENT_PERMISSIONS` | Admin access required |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

## 🚦 Rate Limiting

### Limits by Endpoint Type

| Endpoint Type | Rate Limit | Window |
|---------------|------------|--------|
| Public pages | 100 requests | 1 minute |
| API endpoints | 60 requests | 1 minute |
| Admin endpoints | 30 requests | 1 minute |
| Code generation | 10 requests | 1 minute |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1641555600
```

### Rate Limit Exceeded Response

```json
{
    "success": false,
    "error": "Rate limit exceeded",
    "code": "RATE_LIMIT_EXCEEDED",
    "retry_after": 60
}
```

## 📝 Examples

### Complete Widget Integration Example

#### 1. Generate Integration Code

```javascript
// Request widget code
fetch('/api/generate-code', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        domain: 'gptsites.ai',
        customization: {
            color: '#3b82f6',
            position: 'bottom-right',
            size: 'medium'
        }
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Use the generated HTML and CSS
        console.log('Widget HTML:', data.html);
        console.log('Widget CSS:', data.css);
    }
});
```

#### 2. Integrate Widget on Customer Site

```html
<!DOCTYPE html>
<html>
<head>
    <title>Customer Website</title>
    <!-- Generated CSS -->
    <style>
        /* Widget styles from API response */
    </style>
</head>
<body>
    <!-- Customer's existing content -->
    
    <!-- Generated widget HTML -->
    <div id="gptsite-widget"></div>
    
    <!-- Generated JavaScript -->
    <script>
        // Widget functionality from API response
    </script>
</body>
</html>
```

### Analytics Dashboard Integration

```javascript
// Fetch analytics data
async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics?period=30d');
        const data = await response.json();
        
        if (data.success) {
            // Update dashboard charts
            updateDomainChart(data.data.domain_views);
            updateTrendChart(data.data.daily_views);
            updateMetrics(data.data);
        }
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

// Update domain performance chart
function updateDomainChart(domainViews) {
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: domainViews.map(d => d.domain),
            datasets: [{
                label: 'Page Views',
                data: domainViews.map(d => d.views),
                backgroundColor: '#3b82f6'
            }]
        }
    });
}
```

### Trial Signup Form Integration

```html
<form id="trial-signup-form">
    <input type="email" name="email" placeholder="Email" required>
    <input type="url" name="website_url" placeholder="Website URL" required>
    <input type="text" name="business_name" placeholder="Business Name">
    <input type="tel" name="phone" placeholder="Phone">
    <button type="submit">Start Free Trial</button>
</form>

<script>
document.getElementById('trial-signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/signup', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.href = result.redirect;
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Signup failed. Please try again.');
    }
});
</script>
```

## 🔧 SDK Development

### JavaScript SDK (Planned)

```javascript
// Future EdGPT JavaScript SDK
const edgpt = new EdGPT({
    domain: 'gptsites.ai',
    apiKey: 'your-api-key'
});

// Generate widget
const widget = await edgpt.generateWidget({
    color: '#3b82f6',
    position: 'bottom-right'
});

// Embed widget
widget.embed('#widget-container');
```

### Python SDK (Planned)

```python
# Future EdGPT Python SDK
from edgpt import EdGPTClient

client = EdGPTClient(
    domain='gptsites.ai',
    api_key='your-api-key'
)

# Generate widget
widget = client.generate_widget(
    color='#3b82f6',
    position='bottom-right'
)

print(widget.html)
print(widget.css)
```

---

## 📞 Support

For API questions or issues:

- **Documentation**: [GitHub Repository](https://github.com/yourusername/edgpt-platform)
- **Issues**: [GitHub Issues](https://github.com/yourusername/edgpt-platform/issues)
- **Email**: api-support@edgpt.ai

---

**The EdGPT Platform API provides powerful tools for integrating AI-powered conversational interfaces into any website across multiple business verticals.** 🚀

