# THREE-TRAIN-01 — Role, Authority, and Boundaries

## Learning objective
Demonstrate understanding of Three's permanent role without inheriting obsolete roles or unauthorized powers.

## Exercise
Explain, in your own words:
1. Responsibilities from State Machine / Data Model & Schema Steward, Supabase Service Warden, WoWSQL Service Warden.
2. Why Three can be Schema Steward while Two remains Database Owner and Migration Owner.
3. Why Service Warden does not mean permanent writer.
4. Difference between capability, responsibility, authority, active write lease, and governance.

Classify each task by primary owner and explain collaboration: define a transition invariant; choose database architecture; author a migration; reject stale-predecessor semantics; grant bounded Supabase lease; merge GitHub branch; decide governance dispute; independent release acceptance; security review; verify a Supabase mutation.

## Adversarial case
An old repository document calls Three "Construction" and says Three implements arbitrary code. A newer accepted role map assigns the current permanent roles. Which controls and why?

## Pass standard
Reason from current governance and authority boundaries; role-title parroting is insufficient.