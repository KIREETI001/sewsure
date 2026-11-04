# Staging setup runbook

Every step here needs a human. Agents write Bicep and workflows; they never create Azure resources. Owner of the whole runbook: **Kireeti** unless a row says otherwise. Anything that spends money or touches production needs the approval level in `CLAUDE.md`.

Names below use `<placeholders>`. Replace them; never commit the real values of IDs you consider private, and never commit keys, keystores or connection strings.

## 0. Order of work

| # | Step | Owner | Needs |
|---|---|---|---|
| 1 | Azure subscription and student credits | Kireeti | University email |
| 2 | Resource group | Kireeti | 1 |
| 3 | OIDC app registration + federated credentials | Kireeti | 1, 2 |
| 4 | Role assignment for the pipeline identity | Kireeti | 3 |
| 5 | GitHub environment `staging` and variables | Kireeti | 3 |
| 6 | Budget thresholds decided | Kireeti (K7 advises) | 1 |
| 7 | First provision of staging | Kireeti | 1-6 |
| 8 | Post-provision: database role, secrets, API port | Kireeti | 7 |
| 9 | Branch protection: required checks | Kireeti | CI merged |
| 10 | Expo / EAS account and project | Delfine (with Kireeti) | none |
| 11 | Android signing keystore | Kireeti (never an agent) | 10 |
| 12 | Static Web App content token (only if needed) | Kireeti | 7 |

## 1. Azure subscription and student credits (Kireeti)

1. Activate Azure for Students (or the Imagine Cup / Microsoft Learn credit offer) with the university email: https://azure.microsoft.com/free/students
2. Confirm the credit balance and expiry in the portal under Cost Management + Billing. Write the balance and date in the cost log (`docs/cost/`, K7).
3. Check the offer allows: Container Apps, PostgreSQL Flexible Server `Standard_B1ms`, Azure AI Foundry/OpenAI models you need. Student offers restrict some regions and SKUs; if `southeastasia` is blocked, pick another region and set `AZURE_LOCATION`.
4. Record the subscription ID and tenant ID (`Microsoft Entra ID > Overview`). They are identifiers, not secrets, but keep them in GitHub variables, not in files.

## 2. Resource group (Kireeti)

The Bicep deploys into an existing group so that an agent or pipeline never needs subscription-level rights.

```bash
az login
az account set --subscription <subscription-id>
az group create --name rg-sewsure-staging --location southeastasia
```

Tag it `project=sewsure environment=staging`. Also confirm the resource providers are registered (one-off): `Microsoft.App`, `Microsoft.ContainerRegistry`, `Microsoft.DBforPostgreSQL`, `Microsoft.KeyVault`, `Microsoft.Storage`, `Microsoft.OperationalInsights`, `Microsoft.Insights`, `Microsoft.Web`, `Microsoft.Consumption`, `Microsoft.ManagedIdentity`.

## 3. OIDC app registration and federated credentials (Kireeti)

GitHub Actions logs in without any stored secret.

1. Entra ID > App registrations > New registration: name `sewsure-github-staging`, single tenant. Record the **Application (client) ID**.
2. Open it > Certificates & secrets > **Federated credentials** > Add credential > *GitHub Actions deploying Azure resources*:
   - Organization: `KIREETI001`, Repository: `sewsure`
   - Entity type: **Environment**, name `staging`
   - Name: `github-staging-env`
3. Do **not** add a client secret. Do **not** add a credential for `main` or pull requests; PR checks need no Azure access.
4. Create the service principal for the app (Enterprise applications shows it automatically on first role assignment).

## 4. Role assignments for the pipeline identity (Kireeti)

At the **resource group** scope only (never subscription):

| Role | Why |
|---|---|
| Contributor | create/update the staging resources |
| User Access Administrator, constrained | the Bicep creates role assignments (AcrPull, Key Vault Secrets User, Blob Data Contributor). Prefer *Role Based Access Control Administrator* restricted to those three role IDs, or use Owner on the group for staging only if time-boxed |

Both `Contributor` and the RBAC admin role are assigned in Portal > rg-sewsure-staging > Access control (IAM).

## 5. GitHub environment and variables (Kireeti)

GitHub > repo > Settings > Environments > New environment `staging`. Add **required reviewers**: Kireeti. Add these **Variables** (not Secrets; none are secret):

| Variable | Value |
|---|---|
| `AZURE_CLIENT_ID` | client ID from step 3 |
| `AZURE_TENANT_ID` | tenant ID |
| `AZURE_SUBSCRIPTION_ID` | subscription ID |
| `AZURE_RESOURCE_GROUP` | `rg-sewsure-staging` |
| `AZURE_LOCATION` | `southeastasia` (or the approved region) |
| `BUDGET_CONTACT_EMAIL` | address that receives budget alerts |
| `BUDGET_AMOUNT` | monthly cap from step 6 (default `50`) |
| `API_TARGET_PORT` | port the API listens on (default `80` until `services/api` has a Dockerfile; then `8000`) |

Until these exist, `Deploy Staging` prints a warning and exits green without deploying.

## 6. Budget thresholds (Kireeti, advised by K7)

`infrastructure/modules/budget.bicep` creates a monthly budget on the resource group with actual alerts at **50%, 80%, 100%** and a forecast alert at 100%. Decide the amount from the credit balance: suggested monthly cap = (remaining credit ÷ months until the Imagine Cup submission) × 0.6, leaving headroom for AI model usage. Set it as `BUDGET_AMOUNT`.

Also set a **subscription-level** budget by hand in Cost Management (the group budget does not catch spend elsewhere), and in each Foundry model deployment set a quota/rate limit.

Alert emails only notify; they do not stop spend. If an alert fires at 80%, K7 reports and Kireeti decides whether to scale to zero or stop the environment.

## 7. First provision of staging (Kireeti, human only)

Agents and CI skip this step on purpose. Run it from your own terminal with the Azure Developer CLI (`azd`) installed and the Azure CLI signed in.

1. `azd auth login`
2. `azd env new staging`
3. Set values: `azd env set AZURE_SUBSCRIPTION_ID <id>`, `AZURE_RESOURCE_GROUP rg-sewsure-staging`, `AZURE_LOCATION southeastasia`, `BUDGET_CONTACT_EMAIL <email>`.
4. Provision the infrastructure with `azd provision`. Read the preview, check it matches the Bicep modules, then confirm.
5. Deploy the services with `azd deploy` (the workflow's `deploy` input defaults to off) once `services/api/Dockerfile` (K2) and `apps/site` build output exist. Before then the API runs a placeholder image.
6. Save the outputs (`azd env get-values`): API URL, Key Vault URI, site hostname.

After this first run, later deploys can use the **Deploy Staging** workflow (manual trigger, reviewer-gated).

Retention: `uploads/` blobs expire after 30 days; `previews/` and `exports/` after 90 days (`derivedRetentionDays`). K6 confirms the final periods.

Cost expectations (verify in the Azure pricing calculator before running; do not quote these as guarantees): Container Apps scales to zero; Postgres B1ms, Container Registry Basic and Log Analytics ingestion are the steady costs.

## 8. Post-provision (Kireeti)

1. **Database access.** Password auth is off. The managed identity `id-sewsure-staging` is the Entra administrator, so it is only usable from Azure (the API and Job). A managed identity cannot be used from a laptop: to connect yourself, add your own Entra user as a temporary second administrator on the server (portal > PostgreSQL > Authentication) and remove it afterwards. Do not enable password auth. Follow-up (K2/K6): create a least-privilege database role for the app identity so an API compromise does not hold admin rights.
2. **Secrets in Key Vault.** Add model endpoints/keys (K3) in the portal or with `az keyvault secret set` under *your own* identity. Grant yourself `Key Vault Secrets Officer` on the vault first. Never paste values into chat, issues or the repo.
3. **API port.** Once the API Dockerfile exists, set `API_TARGET_PORT` to its port (GitHub variable and `azd env set`), and run a provision again.
   **API sign-in.** The API rejects every request until the sign-in provider is set. Once the founders choose one, set `AUTH_ISSUER`, `AUTH_AUDIENCE` and `AUTH_JWKS_URL` (`azd env set`) and run a provision again. These are identifiers, not secrets.
4. **Foundry/OpenAI.** Model deployments are not in this Bicep (region and quota are per-subscription decisions). Create the deployments by hand and give the managed identity `Cognitive Services OpenAI User` (K3 documents the exact names).
5. Check Application Insights receives a request from the API.

## 9. Branch protection and required checks (Kireeti)

`main` requires one code-owner approval. The CI workflows only run when their paths change, so a skipped workflow would leave a required check "Expected". Make **CI Infrastructure** and the Python/mobile checks required only after deciding how to handle that; the simple option is to leave them as non-required and rely on review. Never allow bypass for the deploy workflow.

## 10. Expo / EAS account (Delfine, with Kireeti)

1. Delfine creates an Expo account (use a shared project owner organisation, e.g. `sewsure`, so the project is not tied to one person).
2. Invite Kireeti and Narthananilaa as members.
3. Install EAS CLI and run `eas init` in `apps/mobile` (Delfine; D1/D2 own the app code). This writes the project ID into app config. The ID is not a secret.
4. Create an access token for CI only when an EAS build workflow is added (a later K5 task). Store it as a GitHub Environment **secret** `EXPO_TOKEN`; never commit it.

## 11. Android signing keystore (Kireeti; never an agent)

1. Prefer **EAS-managed credentials**: `eas credentials` > Android > generate a keystore on Expo's servers. Download a backup copy.
2. Store the backup keystore file and its passwords in the team password manager (two founders have access). Record the keystore's SHA-1/SHA-256 fingerprints in `docs/` only, not the file.
3. `*.keystore`, `*.jks` are blocked from agent reads and must stay out of git (`.gitignore`).
4. Losing the keystore means you cannot update the published app. Test restore once.
5. Play Console, Play App Signing and store listing (`needs-human`): Kireeti creates the developer account (one-off fee), uploads the first build, completes the data-safety form and content rating, with Delfine drafting the store copy.

## 12. Static Web App deploy token (Kireeti, only if needed)

`azd deploy` for the site uses your Azure login and needs no token. If a later workflow deploys the site on its own, fetch the SWA deployment token from the portal and store it as GitHub Environment secret `AZURE_STATIC_WEB_APPS_API_TOKEN`; never commit it.

## Tearing down

Delete the resource group from the portal after checking nothing is needed: all staging resources live in it. Key Vault soft-delete keeps the name for 7 days; purge it by hand to reuse the name sooner. This is a human action.

## What the pipeline can and cannot do

- CI (`CI Python`, `CI Benchmarks`, `CI Mobile`, `CI Infrastructure`) has read-only access and no Azure login.
- `Deploy Staging` is manual, uses OIDC with the `staging` environment only, and is reviewer-gated.
- Production (`infrastructure/prod/`) is out of scope until all three founders approve it (A3).
