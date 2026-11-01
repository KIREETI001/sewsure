# infrastructure

Owner: Kireeti. Agent: K5 Infra & DevOps (K7 for budgets and monitoring).

Azure via `azd` + Bicep: Container Apps (+ Jobs), PostgreSQL Flexible Server, private Blob Storage, Key Vault, managed identity, Application Insights, Cost Management budgets, Static Web Apps.

## Rules

- `staging/` is agent-editable through PRs (A1). `prod/` is blocked for agents by the project hook. Founders make those changes and tell all three first (A3).
- GitHub Actions authenticate with OIDC federated credentials. No stored cloud keys or connection strings anywhere in the repo.
- Blob containers are private. Access is through short-lived scoped SAS or managed identity.
- Every resource group has a budget alert. Start with the smallest SKUs and scale only on measured need.
- Never create, delete or resize real Azure resources from an agent session. Agents write Bicep and runbooks; a human runs `azd up` for new environments.
