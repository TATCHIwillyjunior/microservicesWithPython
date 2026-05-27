# Module 3 — Reflection

**Team name**: _______________
**Branch**: `module-03/<team-name>`
**Submitted**: before Module 4 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

All client requests now go through the gateway. No client ever calls a service directly.

**Why does that single entry point exist? What would the client's life look like without it?**

Think about what the client would need to know and manage if it talked to each service on its own port.

> *Your answer: Without a gateway, the client would need to know the port of every service, update its own routing table every time a service moves or a new one is added, and handle retries independently per target. With a single entry point on port 8000, the client knows exactly one address — the internal topology is invisible to it, and we can add, move, or replace services without touching the client.*

---

## 2. Your choice

The activity-service makes two outbound calls: one to validate the user (with retry logic), one to fetch game data (with a null fallback if it fails).

**Why are these two calls treated differently? Why does one retry and the other just give up gracefully?**

What is the consequence for the user in each case if the downstream service is unavailable?

> *Your answer: User validation is a hard dependency — creating an activity for a user that doesn't exist would corrupt the data. A transient network blip shouldn't silently produce bad records, so one retry is worth it before failing the whole request. Game enrichment is cosmetic — the activity is already saved and meaningful without it. Blocking or retrying on a non-critical call would make the user pay the cost of a downstream outage for something optional, which is worse than returning null.*

---

## 3. The tradeoff

Every time a client creates an activity, three services are involved synchronously. They all have to be running, healthy, and fast.

**What is the systemic risk of chaining synchronous calls like this?**

What happens to the user experience if the slowest service in the chain takes 3 seconds to respond?

> *Your answer: Every synchronous hop adds latency and a new failure point. If the slowest service takes 3 seconds, the user waits at least 3 seconds regardless of how fast the others are — the chain is as slow as its weakest link. One service being slow or down can cascade: activity-service stalls waiting for user-service, which backs up connections in the gateway, which makes everything else slow too. This is the core argument for async messaging once you care about resilience and latency.*

---

*Keep this file. You will refer back to it during the oral presentation.*
