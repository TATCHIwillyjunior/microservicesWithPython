# Module 2 — Reflection

**Team name**: _______________
**Branch**: `module-02/<team-name>`
**Submitted**: before Module 3 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You built a service with distinct layers: models, schemas, repository, service, and routes — each with a single responsibility.

**Why not just put everything in one file and call it done?**

Think about what happens six months later when someone new joins the team, or when you need to swap SQLite for PostgreSQL. What does the layered structure protect you from?

> *Your answer: Swapping SQLite for PostgreSQL means hunting through mixed concerns instead of changing one file. Each layer has one job — routes don't touch SQL, the repository doesn't know about HTTP so a change in one place can't silently break another. * 

---

## 2. Your choice

Each service owns its data exclusively — no other service is allowed to touch its database directly.

**Pick one entity your service owns (e.g. `User`, `Game`). What would go wrong if another service could write to that table directly?**

Give a concrete scenario, not a general principle.

> *Your answer: If a stats-service writes directly to the games table and adds a NOT NULL column without telling game-service, every INSERT from game-service starts failing at runtime. One service changed the schema, the other paid the price with no warning and no migration history to trace back *

---

## 3. The tradeoff

You now have models, schemas, a repository, a service, and routes — five layers for what is essentially a CRUD service.

**For a system this small, what is the cost of all this structure?**

And at what point does the complexity start to pay off? Where is the tipping point?

> *Your answer: For a small CRUD service, five layers is genuine overhead more files to open, more imports to trace. It starts paying off the moment a second developer joins or the service outlives a demo: you know exactly which file to change and what you're not allowed to break. *

---

*Keep this file. You will refer back to it during the oral presentation.*
