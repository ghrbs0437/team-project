# Backend DB Schema

The backend uses PostgreSQL in local development and reads its connection string from `DATABASE_URL`.

## Local PostgreSQL

```cmd
cd C:\Users\USER\Github\team-project
docker compose up -d db
```

Connection values:

```text
Host: localhost
Port: 5432
Database: soma17ai35
Username: soma
Password: soma
```

SQLAlchemy URL:

```env
DATABASE_URL=postgresql+psycopg://soma:soma@localhost:5432/soma17ai35
```

## DBeaver

Create a PostgreSQL connection with the values above. After connecting, check:

```text
Databases > soma17ai35 > Schemas > public > Tables
```

Expected tables after running `backend\init-db.bat`:

```text
users
crawled_profiles
```

## users

Stores user profile information used for CRUD, embeddings, and recommendations.

| Column | Type | Description |
| --- | --- | --- |
| id | integer | Primary key |
| name | varchar(100) | User name |
| role | varchar(100), nullable | User role such as Backend or Frontend |
| introduction | text, nullable | Short introduction |
| tech_stack | json | List of technologies |
| interests | json | List of interests |
| raw_text | text, nullable | Original profile text |
| created_at | timestamp | Created time |
| updated_at | timestamp | Updated time |

## crawled_profiles

Stores raw crawled profile data before ontology, embedding, and user conversion.

| Column | Type | Description |
| --- | --- | --- |
| id | integer | Primary key |
| source | varchar(100) | Source such as notion or json-import |
| external_key | varchar(255), nullable | External identifier such as URL, page id, or title#index |
| source_url | varchar(500), nullable | Original crawled page URL |
| title | varchar(255) | Crawled profile title |
| raw_text | text | Raw crawled profile text |
| parsed_json | json, nullable | Optional structured metadata |
| created_at | timestamp | Created time |

## Planned Tables

These are planned for the next milestones:

```text
user_ontologies
user_embeddings
```
