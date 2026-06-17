# Module 5 — Reflection

**Team name**: _______________
**Branch**: `module-05/<team-name>`
**Submitted**: before Module 6 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The game-service now has two models for the same data: SQLite for writes, Redis for reads. They store the same games in two different shapes.

**Why go through the trouble of maintaining two representations of the same data?**

Think about what kind of queries each model is optimised for, and what would happen if you tried to use the write model for high-traffic read operations.

> SQLite is optimised for correctness: relational integrity, search (`/games/search`), and being the single source of truth — but every read competes with disk I/O and locking, and that gets worse under concurrent load. Redis is optimised for raw throughput: an in-memory key lookup by `game:summary:{id}` costs almost nothing, so it can absorb thousands of reads/sec without ever touching the database.
>
> If `/summary` read straight from SQLite, every catalogue-browsing request would queue behind write transactions on the same database. To handle more read traffic you'd have to scale the relational DB itself — vertically, or with read replicas and their own consistency headaches — which is expensive and complex. With CQRS, scaling the read path just means adding more Redis capacity, completely decoupled from how writes are handled. The price we pay is that the Redis copy is denormalised (fewer fields) and only as fresh as the last `set_game_summary()` call.

---

## 2. Your choice

The logging-service checks GDPR consent before recording any activity. If a user has not opted in, the log is silently dropped.

**What does this consent check force you to accept about your data?** It is incomplete by design — some activities will never be recorded.

From a system design perspective: where is the right place to enforce this rule — in the logging-service, in the activity-service, or at the gateway? Why?

> Accepting `has_consent()` means accepting that the log is a partial record by design: once a non-consenting user's event is acked and discarded, it's gone — there's no quarantine table to replay if they opt in later. Any analytics built on top of this data systematically undercounts non-consenting users, and that has to be a known, accepted limitation, not a bug to "fix" later.
>
> We enforce it in logging-service, and that's the right layer. GDPR consent here is specifically about *whether this service is allowed to persist personal data* — it's a rule owned by whoever owns the storage being protected, which is logging-service, not the data's origin. The activity itself still happened and other consumers (e.g. notifications) may have an entirely separate, legitimate reason to react to it; conflating "should this be logged" with "should this be acted on" at the activity-service would mix two different policies into one flag.
>
> The gateway is the wrong place on principle: Module 3 set it up as a dumb proxy — no auth, no business logic, just routing — specifically so it stays stateless and easy to reason about. GDPR consent is exactly the kind of business rule we deliberately kept out of it. Putting it there would also mean every request pays the cost of a consent lookup regardless of which service it's headed to, and would create two places that could disagree about consent state.

---

## 3. The tradeoff

With CQRS, your write model and read model can drift out of sync — a game is updated in SQLite but the Redis projection still shows the old data.

**In what scenario does this inconsistency matter to the user? In what scenario is it completely acceptable?**

Is there a class of applications where eventual consistency is never acceptable? What are they?

> It matters when the stale value drives a decision the user can't easily undo — e.g. if `/summary` fed a "buy now" page and the price or availability had just changed in SQLite, acting on the stale Redis value would be a real, consequential mistake. It's completely acceptable for our actual `/summary` endpoint: it's a glanceable catalogue card (title/genre/platform), the staleness window is milliseconds to seconds after a write, and showing the previous title for a moment changes nothing the user does.
>
> Eventual consistency is never acceptable for state where being wrong has a cost that can't be reversed by waiting: money movement, inventory you commit to at checkout ("last item in stock"), and security/permission state — revoking someone's access has to take effect immediately, not "eventually." It ties back to question 2: if `has_consent()` were served from a stale cache instead of a live DB read, withdrawing consent wouldn't actually stop logging right away — that's not just a UX hiccup, it's a compliance violation. That's exactly why we implemented it as a direct query every time instead of caching it.

---

*Keep this file. You will refer back to it during the oral presentation.*
