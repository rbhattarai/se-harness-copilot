# GitHub Repo Search — se-harness Trial Targets

Compiled: 2026-09-30 (UTC) across 5 research rounds.
Purpose: find public web-app products to trial **se-harness** (graphify → AI-agent memory
from code + non-code artifacts → story assistance), as an analogue for an internal
fixed-income SMA platform (Angular + .NET Core + MSSQL, multi-repo, per-env config,
PCF manifests / compose / Helm, NAS docs + Confluence/SharePoint + JIRA).

Related repos: [se-harness](https://github.com/rbhattarai/se-harness),
[demo-loan-app](https://github.com/rbhattarai/demo-loan-app) (loan demo lacks
docs/images/roadmap — the gap this search fills).

Legend: ✅ verified via raw README/docs fetch · 🔍 via search snippets only.

---

## Round 1 — Multi-repo / multi-service web products (any domain)

Criteria: multiple repos or services, `docker compose` with multiple Dockerfiles/services,
web UI with login, product docs/images/videos for graphify.

### Top picks
1. **Saleor (e-commerce)** ✅
   - Repos: [saleor/saleor](https://github.com/saleor/saleor),
     [saleor-dashboard](https://github.com/saleor/saleor-dashboard),
     [saleor-platform](https://github.com/saleor/saleor-platform) (one compose for all services)
   - Compose: API + Dashboard + Postgres + Redis/Valkey + Celery worker/beat + Mailpit + Jaeger
   - Login: Dashboard `http://localhost:9000`, seeded `admin@example.com` / `admin`;
     live demo `demo.saleor.io`
   - Graphify fuel: docs site, README screenshots, blog, API reference
2. **ERPNext / Frappe (accounting, inventory, HR, CRM)** ✅
   - Repos: [frappe/erpnext](https://github.com/frappe/erpnext),
     [frappe/frappe](https://github.com/frappe/frappe),
     [frappe/frappe_docker](https://github.com/frappe/frappe_docker)
   - Compose: backend, frontend, workers, scheduler, websocket, Redis, MariaDB/Postgres
   - Login: `:8080`, `Administrator` / `admin`
   - Graphify fuel: huge docs, wiki, YouTube walkthroughs
3. **dotnet/eShop (.NET reference)** ✅
   - Repo: [dotnet/eshop](https://github.com/dotnet/eshop) — monorepo, services-based,
     `img/eshop_architecture.png` + homepage screenshot in-repo
   - Caveat: `main` boots via .NET Aspire (`aspire run`); use `release/8.0` for compose files

### More candidates (Round 1)
- **Google Online Boutique** ✅ [GoogleCloudPlatform/microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo):
  11 polyglot gRPC services, per-service Dockerfiles, architecture diagram + screenshots.
  No real login (auto session IDs).
- **Robot Shop (Instana)** ✅ [instana/robot-shop](https://github.com/instana/robot-shop):
  Node/Java/Python/Go/PHP + Mongo/Redis/MySQL/RabbitMQ/Nginx, `docker-compose up`,
  storefront `:8080`. Browse-only, patchy auth by design.
- **Sock Shop** ✅ [microservices-demo/microservices-demo](https://github.com/microservices-demo/microservices-demo):
  Spring/Go/Node, `deploy/docker-compose`, register/login + cart/orders, screenshots.
  Flag: repo marked DEPRECATED, runs from prebuilt images.
- **Medusa** 🔍 [medusajs/medusa](https://github.com/medusajs/medusa): commerce monorepo
  (backend + admin + storefront), compose quickstart, admin login, strong docs.
- **Spree** ✅ [spree/spree](https://github.com/spree/spree) (+
  [spree/storefront](https://github.com/spree/storefront)): marketplace/B2B, Rails + Next.js,
  compose overlay, admin login, demo `demo.spreecommerce.org`, screenshot-rich docs.
- **OpenEMR (healthcare EHR)** ✅ [openemr/openemr](https://github.com/openemr/openemr) (+
  [openemr-devops](https://github.com/openemr/openemr-devops)): Docker + compose under `docker/`,
  `admin` / `pass`, demo `one.openemr.io`, wiki + videos. Monolith-plus-modules.
- **Travel**: [Microarchitecturovisco/travel-api](https://github.com/Microarchitecturovisco/travel-api) +
  [travel-ui](https://github.com/Microarchitecturovisco/travel-ui): Java tour-booking
  microservices + separate frontend repo, compose backend. Small community project.

Round 1 trial order: Saleor → ERPNext → Online Boutique / Robot Shop.

---

## Round 2 — FISMA-stack matches (.NET + Angular + MSSQL + shared libs)

Criteria: stack similarity to fisma-frontend (Angular/TS), fisma-backend-core/integration
(.NET/C#), fisma-database (MSSQL), fisma-config (per-env), shared libs, manifests/compose/Helm.

1. **eShopOnContainers** ✅ [dotnet-architecture/eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers)
   (archived; successor `dotnet/eShop`)
   - .NET microservices + **Angular SPA** (`img/eshop-spa-app-home.png` verified) + MVC +
     SQL Server/Redis/RabbitMQ; `BuildingBlocks` ≈ fisma-common-library;
     compose + overrides per env; K8s/Helm. Identity-service login.
   - Non-code: `img/` screenshots, Wiki, **.NET microservices e-book (PDF)** on MS Learn, videos.
   - Caveat: archived, heavy to boot; use `dev` branch for Angular SPA flavor.
2. **Mifos X / Apache Fineract (core banking)** ✅
   [apache/fineract](https://github.com/apache/fineract) +
   [openmf/web-app](https://github.com/openmf/web-app)
   - Angular + TS + Material frontend; `environment.ts` vs `environment.prod.ts` (per-env analogue);
     Docker Compose full-stack; K8s via mifos-gazelle. Closest **domain** match
     (loans, deposits, accounting, funds).
   - Login: `sandbox.mifos.community`, `mifos` / `password`, tenant `default`.
   - Non-code: docs site, **Confluence wiki**, **public JIRA boards** (linked in README),
     Swagger-UI YouTube demo.
   - Caveat: backend is **Java**, DB is **MySQL/Postgres** — domain/process fit, not stack fit.
3. **QuickApp** ✅ [emonney/QuickApp](https://github.com/emonney/QuickApp)
   - **Angular 21 + ASP.NET Core 10 + SQL Server**, OpenIddict/OAuth2 + JWT, full
     user/role/permission UI. [Live demo](https://quickapp-standard.ebenmonney.com).
   - Non-code: YouTube channel + video demo + demo GIF, docs/wiki.
   - Caveat: starter kit (no business domain); single repo; thin Helm story.
4. **eShopOnAbp** ✅ [abpframework/eShopOnAbp](https://github.com/abpframework/eShopOnAbp)
   - ABP microservices + `apps/angular` + AuthServer, SQL Server/Redis/RabbitMQ,
     Docker, **Helm for local K8s** (verified roadmap), `docs/roadmap/Phase_1.png`.
   - Caveat: README says **outdated**; ABP points to its Microservice Solution Template.
   - Note: predecessor `abp-samples/MicroserviceDemo` is deprecated in favor of this.
5. **SimplCommerce** 🔍 [simplcommerce/SimplCommerce](https://github.com/simplcommerce/SimplCommerce)
   - Modular .NET commerce, SQL Server, Docker, `/Admin`
     `admin@simplcommerce.com` / `1qazZAQ!`, docs site + Wiki Roadmap.
   - Caveat: modulith, commerce domain.
6. **QuantConnect Lean (trading)** 🔍 [QuantConnect/Lean](https://github.com/QuantConnect/Lean)
   - C# algo-trading engine, Docker images, `lean.json` per-algo config,
     pluggable data/brokerage handlers; outstanding docs/research/videos.
   - Caveat: **no login web UI** (engine + CLI + cloud IDE) — docs corpus only.

Round 2 trial order: eShopOnContainers → Fineract/web-app → QuickApp.

---

## Round 3 — Node.js-primary microservices (Angular/React/Express + Postgres/Mongo)

Criteria: Node/TS stack, `docker compose up` deploys all services, quick test, user
docs/PDFs/videos/images for graphify; AI-chat support = bonus.

1. **Ever Gauzy (ERP/CRM/HRM/ATS/PM)** ✅ [ever-co/ever-gauzy](https://github.com/ever-co/ever-gauzy)
   - NestJS + Angular, TS, PostgreSQL; Nx monorepo, multiple compose files
     (`docker-compose.demo.yml` seeds demo data).
   - Login: `admin@ever.co` / `admin`, `employee@ever.co` / `12345678` (`DEMO=true`).
   - Graphify fuel: [docs site](https://docs.gauzy.co) + Wiki, screenshots,
     headless API docs, YouTube demos. AI-adjacent siblings (Ever Teams/Works);
     in-app AI chat not verified.
2. **ToolJet (low-code internal tools — best AI match)** ✅ [ToolJet/ToolJet](https://github.com/ToolJet/ToolJet)
   - NestJS + React, Postgres + Redis + workers; `docker compose up` (`:8082`).
   - Instance signup/admin; build panels/dashboards on DBs/APIs/SaaS.
   - Graphify fuel: versioned [docs](https://docs.tooljet.com), screenshots, YouTube, plugin guides.
   - AI (verified): **ToolJet AI** (prompt → pages/queries/components) + official **MCP server**
     for Claude Code / Copilot / Cursor.
3. **Twenty (CRM)** ✅ [twentyhq/twenty](https://github.com/twentyhq/twenty)
   - NestJS + React + TS, Postgres + Redis; server + worker (BullMQ) + db + redis compose
     (`packages/twenty-docker/docker-compose.yml`); Helm chart in-repo.
   - `cp .env.example .env && docker compose up -d` → `:3000`, workspace signup.
   - Graphify fuel: [docs](https://docs.twenty.com), public roadmap, Figma, Discord, YouTube.
   - AI: verified **agent skills** for coding agents + workflow engine; in-app AI chat not claimed.
4. **Rocket.Chat (team chat)** ✅ [RocketChat/Rocket.Chat](https://github.com/RocketChat/Rocket.Chat)
   - TypeScript/Node + MongoDB, microservices layout, Apps-Engine extensions.
   - `docker compose up -d`, setup-wizard admin account.
   - Graphify fuel: extensive [docs](https://docs.rocket.chat), screenshots, videos, marketplace docs.
   - AI via Apps-Engine bots/integrations (ecosystem, not built-in).
5. **Vendure (headless commerce)** 🔍 [vendurehq/vendure](https://github.com/vendurehq/vendure) ·
   demo: [vendurehq/vendure-demo](https://github.com/vendurehq/vendure-demo)
   - Node/NestJS/GraphQL + React admin, TS end-to-end, Postgres; worker process beside server.
   - Demo repo: `docker compose up --build` (db + server + storefront, seeds products).
   - Graphify fuel: [docs](https://docs.vendure.io), guides, videos, Discord. No AI in core (verified absence).
6. **Cal.com (scheduling)** 🔍 [calcom/cal.com](https://github.com/calcom/cal.com)
   - Node/TS Turborepo, Postgres + Prisma; `docker compose up -d` (web + db + Prisma Studio).
   - Signup login; event types, bookings, teams, routing forms, webhooks.
   - Graphify fuel: docs, self-host guides, YouTube, blog. Cal.ai phone agents are commercial-ecosystem only.

Round 3 trial order: Gauzy → ToolJet (if AI-chat matters) → Twenty.

---

## Round 4 — Fixed income / FI-SMA specific: direct answer = none exist

**No open-source repo implements a fixed-income SMA product** (account onboarding, model
portfolios, customization, drift/rebalancing, trading, billing, statements).
Verified fragments:

- **Finance Portal** ✅ [trkbyzc/finance-portal](https://github.com/trkbyzc/finance-portal):
  Spring Boot + React + Postgres + Redis + Kafka + Keycloak (`demouser` / `test123`),
  Compose + K8s, screenshots, live demo; covers bonds/eurobonds/DİBS among 19 domains;
  built-in **AI assistant (LLM tool-calling)**. Personal tracker, not SMA — closest runnable+FI+AI combo.
- **BondScope Pro** ✅ [olivermorid/bondscope-pro](https://github.com/olivermorid/bondscope-pro):
  pure FI app (FastAPI + Next.js + SQLite): screener, portfolio builder, Treasury ladder
  builder, stress tests, real public data. No login/compose; single-dev scope.
- **QuantLib** 🔍 [lballabio/QuantLib](https://github.com/lballabio/QuantLib): industry-standard
  OSS FI engine (bonds, cash flows, day counts, curves, duration/convexity). Library only.
- [renatopalmavalencia/fixed-income-analytics](https://github.com/renatopalmavalencia/fixed-income-analytics) 🔍:
  pricing/YTM/duration/convexity/DV01 + bootstrapping + **companion PDF** + notebooks — ideal graphify pairing.
- [m47h13uk/cpp-fixed-income-analytics](https://github.com/m47h13uk/cpp-fixed-income-analytics) 🔍:
  C++20 → **WASM + React/TS frontend** + live demo. Only full-stack FI analytics app found.
- Also: `txmpeer/bondlab`, `shen-jun/fixed-income`, `domokane/FinancePy`.
- **FINOS CDM** ✅ [finos/common-domain-model](https://github.com/finos/common-domain-model):
  ICMA/ISDA machine-readable model, **CDM for Repo and Bonds** initiative, huge versioned docs.
  Best FI domain-language corpus (Confluence-stand-in). No app.
- **BlackRock Advisor Center Skills** ✅
  [blackrock/advisor-center-agent-skills](https://github.com/blackrock/advisor-center-agent-skills):
  Apache-2.0 skills incl. **SMA/MMA enrollment + servicing routing** via Advisor Center 360° MCP.
  Requires BlackRock access; no standalone app/data.
- **SEC Form ADV tooling** 🔍 [sec-api-io/sec-api-node](https://github.com/sec-api-io/sec-api-node):
  reads advisers' **Schedule D SMA disclosures** — real SMA *data* source, not a product.

Suggested composition: finance-portal (runnable) + FINOS CDM docs (domain language) +
fixed-income-analytics PDF/notebooks (theory) + BlackRock SMA skills (workflow reference).

## Round 5 — InvestorTools Perform / CreditScope: direct answer = none exist

**Zero GitHub repos** integrate with, extend, or client-drive InvestorTools Perform or
CreditScope (verified via multiple searches; `investor-tools` hits are unrelated personal repos).
Both are closed commercial products with no public developer program/SDK:
- **Perform**: portfolio management (analytics, trade allocation, compliance) + Dealer Network;
  integrations are vendor partnerships only (Bloomberg FI trading, Tradeweb Ai-Price,
  SOLVE predictive pricing, ficc.ai muni pricing, KBRA ratings).
- **CreditScope**: credit analysis/surveillance (1M+ CUSIP→issuer linking, opinions/ratings/scores,
  exposure alerts, compliance docs) on Merritt Research Services data; pairs with Perform (FSD).
- Suggested workaround: ingest their **public** pages/award writeups/press releases as the
  non-code workflow corpus for graphify (legal, no proprietary access needed).

---

## Master trial shortlist (across all rounds)

| # | Target | Why |
|---|--------|-----|
| 1 | eShopOnContainers (Round 2) | Closest .NET + Angular + MSSQL + shared-lib + compose/Helm slice of FISMA |
| 2 | Fineract + web-app (Round 2) | Banking domain + Angular + public JIRA/wiki/video artifacts |
| 3 | Ever Gauzy (Round 3) | Richest Node domain + seeded demo + most artifact types |
| 4 | ToolJet (Round 3) | Best AI-chat angle (ToolJet AI + MCP server) |
| 5 | finance-portal + FINOS CDM + FI PDF (Round 4) | Only FI-flavored runnable + corpus composition |
| 6 | Saleor / ERPNext (Round 1) | Backups: strongest multi-repo + login + docs depth |

Staging tip: per trial, check out code + a `noncode/` folder (e-book/wiki PDFs, screenshots,
video links/transcripts, JIRA/roadmap exports) so graphify ingests both sides the way
NAS + Confluence + JIRA would feed it.
