# USER-SEARCH-BACKEND API

## Start Server
```bash
poetry run python app.py
```

## Sample API Commands

### General Account Endpoints

**List all accounts**
```bash
curl "http://localhost:3000/api/v1/"
```

**List accounts by type**
```bash
curl "http://localhost:3000/api/v1/?account_type=service_provider"
```

**List accounts by tags**
```bash
curl "http://localhost:3000/api/v1/?tags=plumber&tags=emergency"
```

**Get account by ID**
```bash
curl "http://localhost:3000/api/v1/ACCOUNT_ID"
```

**Delete account by ID**
```bash
curl -X DELETE "http://localhost:3000/api/v1/ACCOUNT_ID"
```

### Service Provider Endpoints

**Create ServiceProvider**
```bash
curl -X POST "http://localhost:3000/api/v1/providers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@plumbing.com",
    "address": {"street": "123 Main St", "city": "Boston"},
    "tags": ["plumber", "emergency", "residential"],
    "hourly_rate": 75.0,
    "availability": "Mon-Fri 8AM-6PM"
  }'
```

**Get ServiceProvider**
```bash
curl "http://localhost:3000/api/v1/providers/PROVIDER_ID"
```

**Update ServiceProvider**
```bash
curl -X PUT "http://localhost:3000/api/v1/providers/PROVIDER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson Updated",
    "hourly_rate": 85.0,
    "availability": "24/7"
  }'
```

**Delete ServiceProvider**
```bash
curl -X DELETE "http://localhost:3000/api/v1/providers/PROVIDER_ID"
```

### Service Consumer Endpoints

**Create ServiceConsumer**
```bash
curl -X POST "http://localhost:3000/api/v1/consumers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "David Wilson",
    "email": "david@homeowner.com",
    "address": {"street": "789 Pine Rd", "city": "Seattle"},
    "tags": ["homeowner", "budget-conscious"],
    "preferred_budget": 200.0
  }'
```

**Get ServiceConsumer**
```bash
curl "http://localhost:3000/api/v1/consumers/CONSUMER_ID"
```

**Update ServiceConsumer**
```bash
curl -X PUT "http://localhost:3000/api/v1/consumers/CONSUMER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "David Wilson Updated",
    "preferred_budget": 300.0,
    "tags": ["homeowner", "urgent"]
  }'
```

**Add Service to History**
```bash
curl -X POST "http://localhost:3000/api/v1/consumers/CONSUMER_ID/service-history" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "plumbing repair",
    "provider": "Alice Johnson",
    "cost": 150.0,
    "date": "2024-08-10"
  }'
```

**Delete ServiceConsumer**
```bash
curl -X DELETE "http://localhost:3000/api/v1/consumers/CONSUMER_ID"
```
