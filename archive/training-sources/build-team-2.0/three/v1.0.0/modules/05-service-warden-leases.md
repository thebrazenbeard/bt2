# THREE-TRAIN-05 — Service Warden Lease Administration

## Learning objective
Safely administer Supabase/WoWSQL mutation authority.

## Exercise
A producer requests permission to modify three database objects.

Construct a bounded lease containing at minimum: service; exact project/target identity; holder; observed base/currentness; exact schemas/objects; exact allowed operations; migration/transaction identity where applicable; forbidden effects; validity/staleness rule; stop conditions; verification/readback requirements; independent-review requirements where applicable.

Adjudicate:
1. Target schema moves after lease issuance.
2. Producer discovers a fourth table must change.
3. Write returns a deterministic permission error.
4. Write times out with unknown commit state.
5. Readback proves exact intended commit despite transport timeout.
6. Readback shows only half of an allegedly atomic operation occurred.
7. Producer has admin credentials but no current lease.

## Pass standard
Blind retry, scope creep, or capability-as-authority is automatic failure.