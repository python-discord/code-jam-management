# code-jam-management
Management microservice for Python Discord Code Jams

## Running tests:
- Create an `.env` file with:
```DATABASE_URL=postgresql+asyncpg://codejam_management:codejam_management@localhost:7777```
- Then, run `docker-compose up`
- And finally, you can run `pytest` locally.
