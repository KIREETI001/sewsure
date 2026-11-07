# Future live-network failure case — blocked, unexecuted

This is separate from intake/offline-draft.yaml, which tests local mock rejection only.
Do not put this case in the runnable mock suite or use mock signed-in seeds as real authentication.

Prerequisites: a reviewed live client and staging endpoint, a real authorized test session,
synthetic garment data, Android network controls and a defined upload timeout/retry policy.
No live client is implemented in the current intake API seam. Do not exercise production accounts.

1. Through normal UI, prepare a signed-in staging intake with confirmed values 52, 70, 45, 60 cm.
2. Disable network access, attempt Upload, and wait for the defined failure timeout.
3. Require failure wording, unchanged values/confirmations, and no successful receipt.
4. Stop/relaunch without clearing storage; walk back to Measurements and verify the draft.
5. Restore connectivity, retry, and verify the staging server receipt and payload equivalence.
6. Require live Uploaded wording, no Mock badge, and no duplicate server record under the agreed idempotency contract.
7. Restore network state even if a step fails. Record device/build, request trace and redacted logs.

Airplane mode alone may leave Wi-Fi active; verify connectivity is actually blocked.
Until the prerequisites exist, this is a planned case, not evidence of network resilience.
