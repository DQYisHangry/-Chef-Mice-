# Chef Mice — AI-Powered Constraint-Aware Meal Planning Agent

> A stateful, constraint-aware meal planning system that generates intelligent multi-day meal plans, minimizes food waste, and produces targeted shopping lists — powered by Claude AI.

---

## What This Is
This is Chef Mice, a pantry&kitchen helper 🐁👑
This is a **constraint-aware, stateful planning system** that:

- Tracks your current pantry inventory (including expiration dates)
- Learns your dietary and cuisine preferences
- Plans meals across multiple days under real constraints
- Prioritizes ingredients that are about to expire
- Generates a shopping list with reasons for every item
- Updates your inventory state after confirming a plan

---

## Architecture

```
User Request
     │
     ▼
[ FastAPI Layer ]  ←→  [ SQLite / PostgreSQL ]
     │
     ▼
[ Agent Orchestrator ]        ← deterministic pipeline, not a free agent loop
     │
     ├── get_inventory()          pure DB read
     ├── get_user_preferences()   pure DB read
     ├── search_recipes(filters)  → RecipeProvider → external API + local cache
     ├── rank_recipes()           → single bounded LLM call (Claude)
     ├── filter_by_constraints()  pure logic
     ├── assemble_meal_plan()     pure logic
     └── generate_shopping_list() pure logic
```

### Key Design Principle

The LLM is a **reasoning engine, not an orchestrator**. It receives ~20 normalized recipe candidates and returns a ranked list with brief reasoning. It never calls APIs directly, never writes to the database, and is called exactly once per planning request.

---

## Core Modules

| Module | Responsibility |
|--------|---------------|
| `app/models/` | SQLAlchemy ORM — `UserProfile`, `InventoryItem`, `Recipe`, `MealPlan`, `ShoppingList` |
| `app/schemas/` | Pydantic request/response schemas |
| `app/api/` | FastAPI routers — users, inventory, plans, shopping |
| `app/services/` | Business logic — user CRUD, inventory management |
| `app/agent/` | Planning orchestrator, constraint filtering, LLM ranking *(Milestone 3)* |
| `app/recipes/` | `RecipeProvider` abstraction — local cache, Spoonacular API, hybrid *(Milestone 2)* |
| `app/llm/` | Claude API wrapper *(Milestone 3)* |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| HTTP client | httpx |
| LLM | Anthropic Claude (claude-sonnet-4-6) |
| Runtime | Python 3.13 |

---

## Data Models

### UserProfile
Long-term memory — dietary restrictions, cuisine preferences, disliked ingredients, adventurousness (1–5), household size.

### InventoryItem
Short-term state — ingredient name, quantity, unit, type (`perishable` / `shelf_stable` / `spice` / `frozen`), expiration date, soft-delete flag.

### Recipe *(normalized cache)*
Unified schema for all recipe sources. External API results are normalized into this format before the agent sees them. Stores `external_id` + `source` for idempotency and re-normalization.

### MealPlan
Multi-day plan with a JSON `meals` array (`[{date, slot, recipe_id, recipe_name, servings}]`), an `inventory_snapshot` at planning time, and a `constraint_summary` for user transparency.

### ShoppingList
Per-plan shopping list. Every item carries a `reason` field ("needed for Pasta Primavera on Day 3") and a `category` ("produce", "dairy", "pantry") for grouping in a real UI.

---

## API Reference

### Users
```
POST   /users/                          Create user
GET    /users/{user_id}                 Get profile
PATCH  /users/{user_id}/preferences    Update dietary/cuisine preferences
```

### Inventory
```
GET    /users/{user_id}/inventory               List active inventory (sorted by expiry)
POST   /users/{user_id}/inventory               Add item
PUT    /users/{user_id}/inventory/{item_id}     Update item
DELETE /users/{user_id}/inventory/{item_id}     Soft-delete item
POST   /users/{user_id}/inventory/bulk          Bulk upsert (after a shopping trip)
```

### Plans
```
POST   /users/{user_id}/plans                   Trigger planning agent → MealPlan + ShoppingList
GET    /users/{user_id}/plans                   List past plans
GET    /users/{user_id}/plans/{plan_id}         Get plan detail
POST   /users/{user_id}/plans/{plan_id}/confirm Confirm plan → deduct inventory
DELETE /users/{user_id}/plans/{plan_id}         Cancel draft plan
```

### Shopping
```
GET    /users/{user_id}/plans/{plan_id}/shopping-list
PATCH  /users/{user_id}/plans/{plan_id}/shopping-list/mark-purchased
```

---


## Example Workflow *(once fully implemented)*

```
POST /users/{id}/plans
{
  "days": 5,
  "meals_per_day": ["dinner"],
  "cuisine_override": ["italian", "thai"],
  "extra_constraints": "no nuts this week"
}
```

System internally:
1. Retrieves inventory — sorts by expiration date ascending
2. Retrieves user preferences
3. Queries Spoonacular API filtered by cuisine + dietary tags
4. Normalizes results into internal `Recipe` schema, caches locally
5. Claude ranks ~20 candidates against constraints (one bounded API call)
6. Constraint filter: hard-excludes dietary violations, scores expiry urgency + inventory coverage
7. Assembles 5-day meal plan — expiring ingredients used earliest
8. Generates shopping list — delta between plan needs and current inventory
9. Returns `MealPlan` + `ShoppingList` as draft

User confirms → inventory is deducted.

---

## Project Roadmap

| Milestone | Status | Description |
|-----------|--------|-------------|
| **M1 — Foundation** | ✅ Complete | Models, schemas, DB, User + Inventory CRUD |
| **M2 — Recipe Layer** | 🔄 Next | `RecipeProvider` interface, Spoonacular adapter, local cache |
| **M3 — Agent Core** | ⏳ Pending | Orchestrator pipeline, constraint filtering, LLM ranking |
| **M4 — Planning API** | ⏳ Pending | `POST /plans` wired to agent, shopping list generation, inventory deduction |
| **M5 — Hardening** | ⏳ Pending | Unit tests, error handling, substitution logic, rate limiting |

---

## Project Structure

```
meal-planner/
├── app/
│   ├── main.py                 # FastAPI app entry + lifespan
│   ├── config.py               # Settings via pydantic-settings
│   ├── database.py             # Async SQLAlchemy engine + session
│   ├── models/                 # ORM models
│   ├── schemas/                # Pydantic schemas
│   ├── api/                    # FastAPI routers
│   ├── services/               # Business logic
│   ├── agent/                  # Planning orchestrator (M3)
│   ├── recipes/                # RecipeProvider abstraction (M2)
│   └── llm/                    # Claude API client (M3)
├── tests/
├── alembic/                    # DB migrations
├── requirements.txt
└── .env.example
```

---

## Contributing

This project is under active development... 
Last edited by: 4/1/2026

---

## License

MIT
