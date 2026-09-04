# Example PR Description

Here is a realistic example of a Pull Request description written according to the `prfu` standard:

---

TL;DR: Replaces in-memory HTTP session tracking with Redis-backed storage to enable zero-downtime rolling deploys.

## Current Behavior
User session states are stored in-process within `SessionRegistry`. When backend application pods restart or deploy during traffic, active websocket connections and user sessions drop, forcing users to re-authenticate.

## Desired Change
Sessions persist in a shared Redis cluster (`RedisSessionStore`) with atomic TTL management. Application pods can restart independently without invalidating user sessions or disconnecting authenticated streams.

## Implementation Strategy
We introduce a `SessionStore` interface and implement `RedisSessionStore` using connection pooling via `redis-py`. The authentication middleware is updated to fetch session state through the interface rather than the local singleton, using Redis pipelines to batch metadata updates and extend lease expirations in a single round-trip.

## Correctness Verification
- **Automated Tests**:
  - `pytest tests/auth/test_redis_session.py`: 14 passed.
  - `pytest tests/integration/test_rolling_restart.py`: 4 passed (simulated pod termination under simulated user request load).
- **Manual Verification**:
  - Spawned 2 local API instances behind an Nginx proxy.
  - Logged into web UI, killed instance 1 while sending periodic requests; observed zero 401s and seamless failover to instance 2.
- **Edge Cases Tested**:
  - Redis connection failure degrades gracefully by logging structured error and returning `503 Service Unavailable` instead of uncaught 500 panic.
  - Expired TTL cleanups verified using Redis keyspace notifications.

## Supporting Media / Data Tables
| Metric | In-Memory (Old) | Redis-Backed (New) | Delta |
| :--- | :--- | :--- | :--- |
| P99 Auth Overhead | 0.4ms | 1.8ms | +1.4ms (within 5ms SLO) |
| Dropped Sessions on Deploy | ~100% per pod | 0% | -100% |

## Appendix: Redis Failure Mode Rationale
We evaluated whether to fall back to local in-memory storage if the Redis cluster becomes completely unreachable. We opted against fallback: having split-brain session states across pods during a cache partition causes subtle session desync bugs that are significantly harder to debug and detect than a clean 503 response.
