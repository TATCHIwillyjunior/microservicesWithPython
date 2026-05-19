# Module 2 Reflection

## What I built

A `game-service` FastAPI microservice following the same four-layer architecture as `user-service`:
- **models** — SQLAlchemy ORM model for the `games` table
- **schemas** — Pydantic DTOs (`GameCreate`, `GameOut`, `GameList`)
- **repository** — raw DB queries using SQLAlchemy ORM
- **service** — business logic, raises `ValueError` on missing resources
- **routes** — HTTP layer with four endpoints, converts `ValueError` to 404

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/v1/games/` | Add a game to the catalogue |
| GET | `/v1/games/` | List all games (paginated) |
| GET | `/v1/games/search?q=<term>` | Case-insensitive search by title |
| GET | `/v1/games/{id}` | Get a game by ID |

## Key decisions

**Search before ID route**: `/search` must be declared before `/{game_id}` in the router. If `/{game_id}` comes first, FastAPI matches the literal string `"search"` as an ID and returns 422.

**Layer separation**: routes never touch the repository directly — they always go through the service. The repository never raises HTTP errors — it returns `None` for missing records. The service raises `ValueError`, and routes turn that into `HTTPException`.

**Testing with in-memory SQLite**: tests override `get_db` with a `StaticPool` in-memory SQLite database so they never touch the real `games.db` and run in isolation.

## What was harder than expected

Understanding why the `/search` route ordering matters — FastAPI's router matches routes in declaration order, so a parametric route like `/{game_id}` will eagerly consume any path segment that comes before it.

## What I'd improve next

Add input validation (e.g. `release_year` must be a reasonable year), pagination defaults as query param validators, and more granular error messages.