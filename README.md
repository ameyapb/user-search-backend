user-search-backend > Private search.

3 personas:
1. service providers
2. service consumers
3. Admin


Account (Parent Class)
- name: string
- email: string (should be unique)
- address: object/string
- tags: array of strings (for search functionality)
- id: unique identifier
- created_at: timestamp
- updated_at: timestamp

Service Provider Account (Child)

- Inherits all Account fields
- hourly_rate: number (optional)
- availability: object/string

Service Consumer Account (Child)

- Inherits all Account fields
- preferred_budget: number (optional)
- service_history: array (for tracking past services)
