# Module 6 — Reflection

**Team name**: _______________
**Branch**: `module-06/<team-name>`
**Submitted**: before Module 7 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The gateway now validates every JWT before forwarding a request. Individual services no longer need to check identity themselves.

**What does centralising authentication at the gateway buy you?** What would the alternative look like — if every service validated tokens on its own?

Think about what happens when you need to rotate the secret key, or add a new service to the system.

> It buys you one enforcement point instead of N. Right now `_has_valid_token()` in `gateway/app/main.py` is the only place that decides "is this even a legitimately signed token" — every service behind it (user, game, activity, logging) trusts that work is already done and never has to reimplement JWT decoding. If every service validated independently, that logic (and the `python-jose` dependency, and the bug surface around it) would be duplicated N times, and it only takes one service forgetting the check — or implementing it slightly wrong — to open a hole.
>
> Adding a new service is just one line in `ROUTES`; it inherits perimeter security for free, it doesn't need to know anything about JWTs at all. Rotating `SECRET_KEY` is the clearer example of the cost going the other way: today it only has to change in two places (`gateway/app/config.py` and `auth-service/app/config.py`) and both can be redeployed together. If every service verified independently, rotating the key means redeploying *every* service in lockstep — any service that restarts a few seconds late is rejecting tokens signed with the new key, or worse, still accepting the old one.
>
> Important nuance though: the gateway only buys you *authentication* (is this signer legit), not *authorization* (what is this signer allowed to do). That's still `require_admin` living in game-service, checked locally, because only game-service knows which operations are admin-only.

---

## 2. Your choice

When activity-service calls user-service internally, it uses a Machine-to-Machine (M2M) token — not a user's token.

**Why can't it just reuse the user's token that arrived in the original request?**

What would break, or what door would you accidentally leave open, if services passed user tokens between themselves?

> Because the user's token answers "who is this request for" (`role: gamer`), not "what is making this specific internal call." `get_m2m_token()` fetches a *separate* token for `activity-service` itself, with `role: service` — so the call to user-service carries the identity of the calling service, not a borrowed identity that doesn't actually belong to it.
>
> If services just forwarded the user's token around, you'd lose the ability to tell "a gamer called this directly" apart from "this arrived as a side effect of some other request" — which matters the moment any service wants an endpoint that only trusted internal callers should reach. Without a distinct `service` role, there's no way to write that check, because every internal call would look identical to a direct user call carrying valid credentials. It also tangles the token's lifecycle to something it shouldn't depend on: if the user's token expires or gets revoked mid-chain, internal service-to-service plumbing would break for a reason that has nothing to do with whether the services themselves are allowed to talk to each other.

---

## 3. The tradeoff

The gateway and the auth-service share the same `SECRET_KEY` to verify tokens without making a network call on every request.

**What is the security risk of sharing this key?** What happens if it leaks?

And what would the alternative look like — verifying tokens by calling auth-service on every request instead? What does that cost you?

> Anyone who gets `SECRET_KEY` can mint a token offline with whatever claims they want — `{"sub": "anyone", "role": "admin"}` — sign it themselves, and the gateway will accept it as genuine, because signature validity is all it checks. It wouldn't show up as a breach anywhere: no failed login, no suspicious auth-service traffic, because the forged token never touches auth-service at all. That's the real risk of the leak — it's not just "this one service is compromised," it's "every service that trusts this key is compromised, silently." It's also why hardcoding `"dev-secret-change-in-production"` as the literal default in three different `config.py` files is fine for a course exercise but a real liability if it ever shipped: a secret that's also self-documenting as "change me" is one bad deploy away from being the actual production secret.
>
> The alternative — every gateway request makes a network call to auth-service to verify the token (introspection) — buys you the ability to revoke a token immediately and centrally, since auth-service can check a live state instead of just trusting a signature. It costs you: latency on literally every request in the system (not just `/v1/auth/*`), and a hard availability coupling — right now if auth-service goes down, only new logins fail; with introspection, *everything* fails, because no request can be validated without it. The JWT approach trades that availability risk for a different one: a leaked secret has blast radius across every service indefinitely until you rotate it, with no way to revoke a single already-issued token early.

---

*Keep this file. You will refer back to it during the oral presentation.*
