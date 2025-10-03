# API Documentation - Community Packing List

Django REST Framework API documentation for the Community Packing List backend.

## Base URL

- **Development:** `http://localhost:8000/api`
- **Production:** `https://your-backend.com/api`

## Authentication

Currently **no authentication required** (public API). Future versions may add JWT or session-based auth.

## Response Format

All responses are JSON:

```json
{
  "id": 1,
  "name": "Ranger School Packing List",
  "description": "Complete gear list for Ranger School"
}
```

## Error Responses

```json
{
  "error": "Error message here",
  "detail": "Detailed error information"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Server Error

---

## 📋 Packing Lists

### List All Packing Lists

```http
GET /api/packing-lists/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Ranger School Packing List",
    "description": "Complete gear list",
    "type": "course",
    "custom_type": null,
    "school": {
      "id": 1,
      "name": "Ranger School",
      "address": "Fort Moore, GA"
    },
    "base": null
  }
]
```

### Get Packing List Details

```http
GET /api/packing-lists/{id}/detail_view/
```

**Response:**
```json
{
  "packing_list": {
    "id": 1,
    "name": "Ranger School Packing List",
    "description": "Complete gear list",
    "type": "course"
  },
  "items_with_prices": [
    {
      "pli": {
        "id": 1,
        "packing_list": 1,
        "item": {
          "id": 1,
          "name": "Rucksack"
        },
        "quantity": 1,
        "notes": "Military issue preferred",
        "packed": false,
        "section": "Gear",
        "nsn_lin": "8465-01-123-4567",
        "required": true,
        "instructions": "Pack at bottom"
      },
      "item": {
        "id": 1,
        "name": "Rucksack",
        "description": "Large military backpack"
      },
      "prices_with_votes": [
        {
          "price": {
            "id": 1,
            "item": 1,
            "store": {
              "id": 1,
              "name": "Army Navy Store"
            },
            "price": "89.99",
            "quantity": 1
          },
          "upvotes": 15,
          "downvotes": 2,
          "vote_confidence": 0.76,
          "price_per_unit": 89.99
        }
      ]
    }
  ]
}
```

### Create Packing List

```http
POST /api/packing-lists/
```

**Request Body:**
```json
{
  "name": "New Packing List",
  "description": "Optional description",
  "type": "course",
  "custom_type": "",
  "school_id": 1,
  "base_id": null
}
```

**Response:** `201 Created`

### Update Packing List

```http
PUT /api/packing-lists/{id}/
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

### Delete Packing List

```http
DELETE /api/packing-lists/{id}/
```

**Response:** `204 No Content`

### Toggle Item Packed Status

```http
POST /api/packing-lists/{id}/toggle_packed/
```

**Request Body:**
```json
{
  "toggle_packed_item_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "packed": true
}
```

---

## 📦 Packing List Items

### Create Item

```http
POST /api/packing-list-items/
```

**Request Body:**
```json
{
  "packing_list": 1,
  "item_name": "Boots",
  "item_description": "Combat boots",
  "quantity": 1,
  "notes": "Break in before use",
  "section": "Clothing",
  "nsn_lin": "8430-01-123-4567",
  "required": true,
  "instructions": "Pack last"
}
```

**Response:** `201 Created`

### Update Item

```http
PUT /api/packing-list-items/{id}/
```

### Delete Item

```http
DELETE /api/packing-list-items/{id}/
```

---

## 🏪 Stores

### List All Stores

```http
GET /api/stores/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Army Navy Store",
    "address_line1": "123 Main St",
    "address_line2": "",
    "city": "Columbus",
    "state": "GA",
    "zip_code": "31901",
    "country": "USA",
    "url": "https://armynavy.com",
    "latitude": 32.4609,
    "longitude": -84.9877,
    "is_online": true,
    "is_in_person": true
  }
]
```

### Create Store

```http
POST /api/stores/
```

**Request Body:**
```json
{
  "name": "New Store",
  "address_line1": "456 Market St",
  "city": "San Francisco",
  "state": "CA",
  "zip_code": "94102",
  "is_online": true,
  "is_in_person": false
}
```

### Update Store

```http
PUT /api/stores/{id}/
```

### Delete Store

```http
DELETE /api/stores/{id}/
```

---

## 💰 Prices

### Create Price

```http
POST /api/prices/
```

**Request Body:**
```json
{
  "item": 1,
  "store_id": 1,
  "price": "29.99",
  "quantity": 1,
  "date_purchased": "2025-10-03"
}
```

**Response:** `201 Created`

---

## 👍 Voting

### Vote on Price

```http
POST /api/votes/
```

**Request Body (Upvote):**
```json
{
  "price_id": 123,
  "upvote_price_id": 123
}
```

**Request Body (Downvote):**
```json
{
  "price_id": 123,
  "downvote_price_id": 123
}
```

**Response:**
```json
{
  "id": 456,
  "price": 123,
  "is_correct_price": true,
  "ip_address": "192.168.1.1",
  "created_at": "2025-10-03T14:30:00Z"
}
```

---

## 🎓 Schools

### List All Schools

```http
GET /api/schools/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Ranger School",
    "address": "Fort Moore, GA",
    "latitude": 32.3717,
    "longitude": -84.9476
  }
]
```

### Create School

```http
POST /api/schools/
```

**Request Body:**
```json
{
  "name": "New School",
  "address": "Fort Campbell, KY",
  "latitude": 36.6584,
  "longitude": -87.4739
}
```

---

## 🏔️ Military Bases

### List All Bases

```http
GET /api/bases/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Fort Campbell",
    "address": "Kentucky/Tennessee",
    "latitude": 36.6584,
    "longitude": -87.4739
  }
]
```

---

## 🔍 Common Patterns

### Filtering (Future)

```http
GET /api/packing-lists/?type=course
GET /api/stores/?is_online=true
```

### Pagination

```http
GET /api/packing-lists/?page=2
```

**Response:**
```json
{
  "count": 100,
  "next": "http://api.example.com/api/packing-lists/?page=3",
  "previous": "http://api.example.com/api/packing-lists/?page=1",
  "results": [...]
}
```

### Searching (Future)

```http
GET /api/packing-lists/?search=ranger
GET /api/items/?search=boots
```

---

## 📤 File Upload (Future)

### Upload Packing List File

```http
POST /api/packing-lists/upload/
Content-Type: multipart/form-data
```

**Form Data:**
- `file` - CSV, Excel, or PDF file
- `list_name` - Name for the new list
- `list_type` - Type of list (course/selection/etc)

---

## 🔐 CORS Headers

The API includes CORS headers for:
- `http://localhost:5173` (development)
- `https://community-packing-list.pages.dev` (production)

---

## 📊 Data Models

### Packing List Types

```typescript
type PackingListType =
  | 'course'
  | 'selection'
  | 'training'
  | 'deployment'
  | 'other'
```

### Vote Confidence Score

```
vote_confidence = (upvotes - downvotes) / max(total_votes, 1)
```

Range: `-1.0` to `1.0`

---

## 🧪 Testing the API

### Using cURL

```bash
# List packing lists
curl http://localhost:8000/api/packing-lists/

# Create packing list
curl -X POST http://localhost:8000/api/packing-lists/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test List","type":"course"}'

# Get list details
curl http://localhost:8000/api/packing-lists/1/detail_view/
```

### Using HTTP Client

Import into Postman, Insomnia, or HTTPie.

---

## 📝 Notes

- All timestamps are in UTC
- Prices are stored as decimals with 2 decimal places
- Items are unique by name
- One item can appear on multiple lists
- Voting is tracked by IP address (no user auth yet)
- NSN/LIN codes are optional strings

## 🚀 Future Endpoints

- [ ] `GET /api/packing-lists/{id}/export/` - Export as CSV/PDF
- [ ] `POST /api/packing-lists/{id}/duplicate/` - Duplicate list
- [ ] `GET /api/items/search/` - Advanced item search
- [ ] `GET /api/stats/` - Usage statistics
- [ ] `POST /api/auth/login/` - User authentication

---

**Last Updated:** October 2025
**API Version:** 1.0
