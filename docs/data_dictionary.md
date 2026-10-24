# Order pipeline data dictionary

The model and column descriptions in [orders_schema.yml](../models/orders_schema.yml)
are the maintained dbt definitions. This page adds a readable overview of lineage,
business meaning and validation coverage. Update both when a field or rule changes.

## Lineage and grain

| Dataset/model | Grain | Behavior |
| --- | --- | --- |
| PostgreSQL `test.orders` | One current record per `order_id` | Primary-key upsert; source of truth |
| BigQuery `datastream_raw.test_orders` | Replicated current order state | Asynchronous Datastream delivery and application |
| `stg_orders` | One current record per `order_id` | View; normalize status and retain every status |
| `fct_daily_sales` | One row per date with completed orders | Table rebuilt by dbt; no row for dates with no completed orders |

## Order fields

| Field | Source type | Meaning | Validation in this project |
| --- | --- | --- | --- |
| `order_id` | `bigint NOT NULL`, primary key | Order identity and upsert key | Python: positive integer, missing and duplicate text IDs; dbt: unique and not_null |
| `customer_id` | `bigint NOT NULL` | Synthetic customer identity | Python: required positive integer; no customer dimension or relationship test |
| `order_date` | `date NOT NULL` | Business date, not load date | Python: parse YYYY-MM-DD; dbt: not_null |
| `status` | `text NOT NULL` | Current lifecycle state, trimmed and lowercased | Python and dbt: pending/completed/cancelled/refunded; dbt also checks not_null |
| `amount` | `numeric(10,2) NOT NULL` | Order amount; synthetic single, unspecified currency | Python: numeric, nonnegative, positive if completed; dbt: not_null plus custom amount test |
| `updated_at` | `timestamptz NOT NULL` | Source modification time | Source insert default; loader explicitly updates it on conflict; no dbt timestamp test |

`updated_at` is not the BigQuery arrival timestamp. It cannot alone measure CDC lag.
The loader can change it even when business values remain unchanged.

## Daily measures

| Field | Definition | Interpretation |
| --- | --- | --- |
| `order_date` | Grouping date from staging | Only dates with completed orders appear |
| `order_count` | COUNT(*) WHERE status = 'completed' | Current completed-order count, not all orders |
| `completed_revenue` | SUM(amount) WHERE status = 'completed' | Excludes pending, cancelled and refunded orders; not accounting net revenue |

The current-state model means a later refund, cancellation, correction or deletion
can change a prior date's total on the next dbt run. There is no event history,
separate refund transaction, tax calculation or currency conversion.

## Validation evidence and boundaries

- Fixture: 11 CSV rows, 3 passing rows and 8 rejected rows; both instances of
  duplicate ID 910001 are rejected.
- Repeated load: selected PostgreSQL order count remained 3.
- Source and mart comparison: 2026-10-21 returned 1 completed order and 25.50.
- Staging tests: 7 passed, then 6 passed / 1 failed after a completed amount was
  set to zero, then 7 passed after restoration. See [validation](validation.md).
- These seven tests validate staging rules. Daily aggregation was compared manually;
  documenting a field does not create a test or enforce a database constraint.
- Numeric range/scale and equivalent textual IDs such as `01` and `1` are not fully
  covered by the learning validator. PostgreSQL constraints remain a separate layer.
- Recovery artifacts describe the earlier run, not a fresh run of this documentation update.

## Maintaining the dictionary

When a rule changes, update the column description, corresponding validation code
or test, and expected sample results in the same PR. Keep intended rules separate
from checks actually implemented. Preserve prior execution evidence rather than
rewriting it to look like a new run.

## Next exercise: orchestration (not implemented)

Before adding a local Airflow DAG, make ingestion callable without interactive input,
configure credentials outside code, and implement a bounded source-to-BigQuery
reconciliation check. A DAG should wait for matching keys and business values,
run staging tests, and only then rebuild the mart. A fixed sleep does not establish
CDC completion. Test retries and failure handling locally before claiming scheduling
or orchestration experience.
