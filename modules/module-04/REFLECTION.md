# Module 4 — Reflection

**Team name**: _______________
**Branch**: `module-04/<team-name>`
**Submitted**: before Module 5 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

In Module 3, services called each other directly over HTTP. Now activity-service drops a message into a broker and moves on — it never waits for a reply.

**What does the activity-service gain by not waiting? And what does the notification-service gain by consuming at its own pace?**

Think about what happens under load, or when notification-service is temporarily down.

> *Your answer: The publisher catches all exceptions and logs it then the activity creation still succeeds even if RabbitMQ is down since saving an activity is the user's action, sending a notification is a side effect and one should not block the other*

---

## 2. Your choice

In Module 3 you already knew how to call another service directly over HTTP — you did it for user validation and game enrichment.

**Why not use the same approach for notifications? What does introducing a broker give you that a direct HTTP call doesn't?**

Think about what happens if notification-service is slow, or crashes mid-message.

> *Your answer: With HTTP, activity-service would need notification-service to be alive and responsive at the exact moment the activity is created. A broker removes that dependency entirely. The message sits in the queue until notification-service is ready to consume it.*

---

## 3. The tradeoff

With synchronous REST, you get an immediate answer: success or failure. With async messaging, the activity is saved and the message is sent — but you have no idea if the notification was ever delivered.

**How would a user know if their notification was never sent? How would you know as a developer?**

What visibility do you lose when you go async?

> *Your answer: The user would have no idea they only get a successful response from the activity creation. As a developer, you would only find out through HTTP immediate status code if the call succeeded or failed or by checking logs, monitoring the queue depth in the RabbitMQ UI, or setting up alerts on unacknowledged messages. Without those tools in place, a failed notification is completely invisible.*

---

*Keep this file. You will refer back to it during the oral presentation.*
