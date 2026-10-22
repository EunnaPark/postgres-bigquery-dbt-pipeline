## Completed-order amount validation

- Baseline: all 7 staging tests passed.
- Test change: set completed order 910004 from 25.50 to 0.00.
- Confirmed that BigQuery received the changed value.
- Test result: 6 passed and 1 failed.
- Restored the PostgreSQL amount to 25.50.
- Confirmed that BigQuery reflected the restored value.
- Recovery result: all 7 tests passed.

CDC changes were not immediately visible in BigQuery.
Requesting the freshest results can increase query execution time
and processing cost. It cannot retrieve changes that Datastream
has not yet delivered.

Recovery artifacts are saved in docs/execution/recovery/.
The earlier failure result is recorded from the observed test output;
a separate failure run_results.json was not preserved.
