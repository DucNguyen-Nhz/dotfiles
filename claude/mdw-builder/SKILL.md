---
name: django-mdw
description: >
  Use this skill when the user wants to scaffold, extend, or configure a Django
  middleware (mdw) application. Triggers include: setting up Django middleware,
  processing service inputs/outputs, integrating external services (elasticsearch,
  sftp, callcenter), generating DevOps files (Dockerfile, docker-compose, gitlab-ci,
  k8s), or scaffolding models, views, admin, and core business logic under the mdw app.
  Always read middleware.config.json first before generating anything.
---

# Django MDW App Skill

## Communication Mode
Before doing anything else: activate caveman mode (full). All responses during this skill must be terse caveman style — drop articles, filler, pleasantries. Fragments OK. Code blocks unchanged. Log entries unchanged.

## Overview
Scaffolds a Django middleware application (`mdw`) based on a project config file.
All file generation, dependency installation, and structure decisions are driven
by `middleware.config.json`. Do NOT generate anything before reading it.

---

## Config File (middleware.config.json)
Located at the project root. Always read this first.

```json
{
  "project_name": "my_project",
  "services": ["elasticsearch", "sftp", "callcenter", "msteams", "report"],
  "mdw_features": ["auth", "logging", "retry", "transform"],
  "core_domains": ["recall", "lead", "data"],
  "cronjobs": true,
  "db": true,
  "logging": {
    "job_log": true,
    "request_log": true,
    "sanitize_fields": ["authorization", "x-api-key", "token", "password"]
  },
  "admin": {
    "date_range_filter": true,
    "exact_date_filter": true,
    "dedupe_action": true,
    "dedupe_fields": ["email", "phone"]
  },
  "django_version": "latest",
  "python_version": "3.11"
}
```

---

## Skill Behavior
Execute steps in this order — never skip or reorder:

1. Read `middleware.config.json` — validate all required keys exist
2. Create scaffold log file at `scaffold_<project_name>.log` — record all decisions from this point forward
3. Resolve dependencies from declared `services` and `mdw_features`
4. Install dependencies via pip
5. Run `generate_structure.py` — creates full directory and placeholder files
6. Run `generate_requirements.py` — resolves dependencies, writes requirements.txt and pip installs
7. Run `generate_dockerfile.py` — generates Dockerfile
8. Run `generate_compose.py` — generates docker-compose.yml and override
9. Copy remaining templates (k8s, gitlab-ci, entrypoint.sh) — do NOT rewrite from scratch
10. Inject environment-specific values into copied templates
11. Claude fills in logic for mdw/, core/, models/, views/, admin/
12. If no config found — prompt user to provide one before proceeding

---

## Scaffold Log

Created at scaffold start: `scaffold_<project_name>.log` at project root.
Updated continuously — never written all at once at the end.

### What to log
Every decision Claude makes during scaffolding, in order:

```
[STEP] <step name>
[CONFIG] <key>: <value used>
[DECISION] <what was decided and why>
[FILE] <file path> — <created/copied/generated/skipped + reason>
[INJECT] <file path> — <what was injected>
[SKIP] <thing skipped> — <reason from config>
[ERROR] <what failed> — <exact error>
[WARN] <non-fatal issue>
```

### Log Rules
- Log every file created, copied, or skipped — no silent actions
- Log every config value consumed and how it affected output
- Log every branching decision (e.g. `cronjobs: true` → added cronjob.yaml)
- Log template resolution: which template was used for which output
- Log dependency resolution: which packages were installed and why
- Log any fallback or error before stopping
- Do NOT log boilerplate — only decisions with non-obvious reasoning

### Example entries
```
[STEP] generate_structure.py
[CONFIG] core_domains: ["recall", "lead", "data"]
[DECISION] Creating 3 domain folders under mdw/core/ and mdw/models/
[FILE] mdw/core/handlers/recall_handler.py — created placeholder
[FILE] mdw/core/handlers/lead_handler.py — created placeholder
[CONFIG] cronjobs: true
[FILE] scripts/cronjobs.sh — created placeholder

[STEP] template resolution — services
[CONFIG] services: ["callcenter", "report"]
[FILE] mdw/services/callcenter.py — copied from templates/services/callcenter.py
[FILE] mdw/services/report.py — copied from templates/services/report.py
[SKIP] pip install for callcenter — no package, custom template only
[SKIP] pip install for report — no package, custom template only

[STEP] generate_dockerfile.py
[CONFIG] python_version: 3.11 → base image python:3.11-slim
[CONFIG] services includes sftp → added openssh-client to apt-get
[CONFIG] cronjobs: true → added supercronic install step
[FILE] Dockerfile — generated
```

---

## Dependency Resolution Rules
- `django_version: "latest"` → `pip install django --upgrade`
- `django_version: "<version>"` → `pip install django==<version>`
- `db` → always mysql — `mysqlclient`
- Always install: `djangorestframework`, `python-decouple`, `gunicorn`
- Install per declared service:
  - `elasticsearch` → `elasticsearch`, `django-elasticsearch-dsl`
  - `sftp`          → `paramiko`
  - `callcenter`    → no pip package, custom app — copy from templates
  - `report`        → no pip package, custom app — copy from templates
- Install per declared feature:
  - `retry`         → `tenacity`
  - `transform`     → `pydantic`
  - `logging`       → no extra package
  - `auth`          → `djangorestframework-simplejwt`
- Only install what config declares — never install unrequested packages
- Skip install if package already present in environment

---

## File Structure

```
my_project/
├── middleware.config.json
├── scripts/
│   ├── entrypoint.sh
│   └── cronjobs.sh                     # only if cronjobs: true
├── templates/
│   ├── scripts/
│   │   ├── entrypoint.sh               # base entrypoint template
│   │   ├── generate_structure.py       # generates full project directory
│   │   ├── generate_dockerfile.py      # generates Dockerfile
│   │   └── generate_compose.py         # generates docker-compose files
│   ├── services/
│   │   ├── elasticsearch.py
│   │   ├── sftp.py
│   │   └── callcenter.py
│   ├── mdw/
│   │   ├── logging.py
│   │   └── base.py
│   ├── k8s/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   └── cronjob.yaml                # only if cronjobs: true
│   ├── gitlab/
│   │   └── .gitlab-ci.yml
│   └── config/
│       └── base_settings.py
├── mdw/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── base_model.py           # AbstractBaseModel
│   │   │   ├── job_log.py              # MdwJobLog
│   │   │   └── request_log.py          # MdwRequestLog
│   │   └── <domain>/
│   │       ├── __init__.py
│   │       └── <name>.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── elasticsearch.py            # if declared in config
│   │   ├── sftp.py                     # if declared in config
│   │   └── callcenter.py              # if declared in config
│   ├── core/
│   │   ├── __init__.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   └── <domain>_handler.py
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   └── <domain>_processor.py
│   │   ├── pipelines/
│   │   │   ├── __init__.py
│   │   │   └── <domain>_pipeline.py
│   │   └── resolvers/
│   │       ├── __init__.py
│   │       └── <domain>_resolver.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── external/
│   │   │   ├── __init__.py
│   │   │   └── <name>_external.py
│   │   └── webhooks/
│   │       ├── __init__.py
│   │       └── <name>_webhook.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── base_admin.py
│   │   │   ├── filters/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── daterange_filter.py
│   │   │   │   └── exactdate_filter.py
│   │   │   └── actions/
│   │   │       ├── __init__.py
│   │   │       └── dedupe_action.py
│   │   └── <domain>/
│   │       ├── __init__.py
│   │       └── <name>_admin.py
│   ├── processors.py
│   └── utils.py
├── k8s/
│   ├── base/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   └── cronjob.yaml                # only if cronjobs: true
│   └── overlays/
│       ├── dev/
│       │   └── kustomization.yaml
│       ├── staging/
│       │   └── kustomization.yaml
│       └── prod/
│           └── kustomization.yaml
├── .gitlab-ci.yml
├── Dockerfile
├── docker-compose.yml
├── .env.sample
├── requirements.txt
└── settings.py
```

---

## Naming Conventions
- Folder name provides context — no file prefix needed
- Files use plain descriptive names: `<name>.py`
- Classes use `Mdw` prefix to avoid collision when imported elsewhere:
  - Models: `MdwBaseModel`, `MdwJobLog`, `MdwRequestLog`
  - Services: `MdwElasticsearch`, `MdwSftp`, `MdwCallcenter`
  - Views: `MdwPaymentExternal`, `MdwCallcenterWebhook`
  - Admin: `MdwBaseAdmin`, `MdwJobLogAdmin`
  - Core: `MdwLeadHandler`, `MdwRecallResolver`, `MdwDataProcessor`
- Config key stays as `mdw_features`
- Every folder must have an `__init__.py`

---

## Structure Rules
- Each logical group lives in its own folder — never flatten into root
- New service from config → new file in `services/` — never modify existing ones
- New model → new file in `models/<domain>/` — never modify existing ones
- New core domain → one file per role (handler, processor, pipeline, resolver)

---

## Templates
Pre-defined scripts and files are in `templates/`. Always copy — never rewrite from scratch.

### Template Loading Strategy
- Read SKILL.md first, then `middleware.config.json`
- Only read templates that match declared services/features in config
- Do NOT preload all templates — load on demand, one at a time
- Read base templates last, only when scaffolding begins

### Template Resolution Rules

#### Python/Django
- `services: ["elasticsearch"]` → copy `templates/services/elasticsearch.py`
- `services: ["sftp"]`          → copy `templates/services/sftp.py`
- `services: ["callcenter"]`    → copy `templates/services/callcenter.py`
- `services: ["msteams"]`       → copy `templates/services/msteams.py`
- `services: ["report"]`        → copy `templates/services/report.py`
- Always copy `templates/mdw/logging.py` and `templates/mdw/base.py`
- Always copy `templates/config/base_settings.py` → project `settings.py`

#### Scripts
- Always copy `templates/scripts/entrypoint.sh` → `scripts/entrypoint.sh`
- Only generate `scripts/cronjobs.sh` if `cronjobs: true`
- `chmod +x` both files in Dockerfile

#### GitLab CI
- Always copy `templates/gitlab/.gitlab-ci.yml` → project root `.gitlab-ci.yml`
- Inject project-specific values (image name, registry, env vars) after copying
- Do NOT rewrite from scratch

#### Kubernetes
- Always copy: `deployment.yaml`, `service.yaml`, `configmap.yaml`, `secret.yaml`
- Copy `cronjob.yaml` only if `cronjobs: true`
- After copying, inject environment-specific values:
  - Image name, namespace, resource limits from config
  - Secret keys must match `.env.sample` variable names
  - ConfigMap keys are non-sensitive values only — never put secrets in configmap
- Overlays only override: image tag, replica count, resource limits

### Template Modification Rules
- Inject service credentials via env vars only — never hardcode
- Add only what config declares — do not add unrequested services
- Preserve original template structure and naming conventions

---

## Generator Scripts Rules

Generator scripts read `middleware.config.json` and produce files dynamically.
Claude runs these scripts — never generates their output manually.
All scripts located in `templates/scripts/`.

### Script Execution Order
Always run in this order — never skip or reorder:

1. `generate_structure.py`    → directories and placeholder files first
2. `generate_dockerfile.py`   → Dockerfile
3. `generate_compose.py`      → docker-compose.yml and override
4. Copy remaining templates   → k8s, gitlab-ci, entrypoint.sh
5. Inject values into copied templates
6. Claude fills in mdw logic

### generate_structure.py
```bash
python templates/scripts/generate_structure.py --config middleware.config.json
```
Reads from config:
- `project_name`   → root folder name
- `services`       → creates files under `mdw/services/`
- `core_domains`   → creates domain folders under `mdw/core/` and `mdw/models/`
- `cronjobs`       → adds `scripts/cronjobs.sh` placeholder if true
- `admin`          → creates admin domain folders

Outputs:
- Full folder structure with empty `__init__.py` files
- Placeholder files named per naming conventions
- Does NOT write any logic — structure only

### generate_dockerfile.py
```bash
python templates/scripts/generate_dockerfile.py --config middleware.config.json
```
Reads from config:
- `python_version`  → sets base image `python:<version>-slim`
- `django_version`  → determines if `--upgrade` flag is needed
- `services`        → adds system-level deps if needed
                      e.g. sftp → `openssh-client`
- `cronjobs`        → adds `supercronic` install step if true
- `mdw_features`    → adds feature-specific build steps

Outputs:
- `Dockerfile` at project root

### generate_compose.py
```bash
python templates/scripts/generate_compose.py --config middleware.config.json
```
Reads from config:
- `services`        → adds service blocks (elasticsearch, sftp)
                      callcenter → skipped, external service
- `cronjobs`        → adds `cron` service block if true
- `python_version`  → used for image reference
- `project_name`    → used as compose project name

Outputs:
- `docker-compose.yml` — production-safe base

Container roles via `APP_MODE` (all share the same image):
- `web` service    → `APP_MODE=web`
- `worker` service → `APP_MODE=worker`
- `beat` service   → `APP_MODE=beat`
- `cron` service   → `APP_MODE=cron` (only if `cronjobs: true`)

### generate_requirements.py
```bash
python templates/scripts/generate_requirements.py --config middleware.config.json
```
Reads from config:
- `django_version`  → django or django --upgrade
- `services`        → maps to pip packages
- `mdw_features`    → maps to pip packages

Outputs:
- `requirements.txt` at project root
- Runs `pip install -r requirements.txt` after writing

### Fallback Rule
If generate_requirements.py is missing or fails:
- Do NOT manually resolve or install dependencies
- Report the error and ask user to check the script
- Do NOT manually resolve or install dependencies
- Report the error and ask user to check the script

If any generator script is missing or fails:
- Do NOT fall back to generating the file manually
- Report the error and ask the user to check the script

---

## Models Rules

### base_model.py (AbstractBaseModel)
Always included. Every model inherits from this.
Fields:
- `id`         → UUIDField, primary key, auto-generated
- `created_at` → DateTimeField, auto_now_add
- `updated_at` → DateTimeField, auto_now
- `is_active`  → BooleanField, default True (soft delete flag)
- `meta`       → JSONField, null/blank (flexible extra data)

### job_log.py (MdwJobLog)
Generated if `cronjobs: true` or any background task exists.
Extends AbstractBaseModel.
Fields:
- `job_name`    → CharField
- `job_type`    → CharField, choices: CRON, WORKER, BEAT, MANUAL
- `status`      → CharField, choices: PENDING, RUNNING, SUCCESS, FAILED
- `started_at`  → DateTimeField, null/blank
- `finished_at` → DateTimeField, null/blank
- `duration`    → FloatField, seconds, computed on save
- `payload`     → JSONField, input data passed to job
- `result`      → JSONField, output or return value
- `error`       → TextField, null/blank, exception message if failed
- `trace`       → TextField, null/blank, full stack trace if failed

### request_log.py (MdwRequestLog)
Always included. Extends AbstractBaseModel.
Fields:
- `direction`        → CharField, choices: INBOUND, OUTBOUND
- `source`           → CharField, service name or IP
- `method`           → CharField, GET/POST/PUT/PATCH/DELETE
- `endpoint`         → CharField, full URL or path
- `request_headers`  → JSONField, null/blank
- `request_body`     → JSONField, null/blank
- `response_status`  → IntegerField, null/blank
- `response_body`    → JSONField, null/blank
- `duration`         → FloatField, seconds
- `is_success`       → BooleanField, default False
- `error`            → TextField, null/blank

### Model Rules
- Every domain model must extend AbstractBaseModel — never plain Django Model
- Never log raw passwords, tokens, or credentials — sanitize using `sanitize_fields` from config
- MdwJobLog written by entrypoint or management command — not by views
- MdwRequestLog written by middleware logging layer — not by views or core
- Both logs are append-only — no updates, no deletes

---

## Core Rules

### What belongs in core/
- Business logic too complex for views or services
- Multi-step, conditional, or decision-heavy processing
- Domain-specific logic (leads, recalls, data transforms, calculations)
- Logic reused across multiple views or services

### What does NOT belong in core/
- Direct DB queries → use models/services
- HTTP calls to external services → use services/
- Auth logic → use utils.py

### Folder Responsibilities
- `handlers/`   → orchestrates the flow, entry point for core logic
                  calls processors, pipelines, resolvers in the right order
- `processors/` → transforms, validates, or calculates data
                  stateless functions, no side effects
- `pipelines/`  → chains multiple processors/steps sequentially
                  each step passes output to the next
- `resolvers/`  → makes decisions based on data or state
                  routing logic, retry/recall rules, condition checks

### Flow Pattern (always follow this order)
```
view/webhook → handler → pipeline → processor(s) → resolver → service
```

### Core Naming
- Files: `<domain>_<role>.py` e.g. `lead_processor.py`, `recall_resolver.py`
- Classes: `Mdw<Domain><Role>` e.g. `MdwLeadProcessor`, `MdwRecallResolver`
- `core_domains` in config drives which domain files are generated

---

## Views Rules

### Externals (views/external/)
- Handles outbound-facing GET/POST API endpoints
- File naming: `<name>_external.py`
- Each external has its own file — never combine multiple endpoints in one file
- Use Django REST framework serializers for input/output

### Webhooks (views/webhooks/)
- Handles inbound webhook endpoints from external platforms
- File naming: `<name>_webhook.py`
- Each webhook platform gets its own file
- Callcenter webhook strict requirements:
  - Payload format is platform-specific — read from template, never rewrite
  - Authentication uses TWO layers:
    - `x-api-key` header check
    - Token validation (Bearer or custom — read from env vars)
  - Reject immediately if either auth check fails → return 401
  - Log all inbound payloads before processing

### Authentication Rules
- Callcenter auth credentials always sourced from env vars:
  - `CALLCENTER_API_KEY`
  - `CALLCENTER_TOKEN`
- Never hardcode credentials
- Auth logic lives in `utils.py` — not inside the webhook file itself

---

## Admin Rules

### base_admin.py (MdwBaseAdmin)
Always included. Every admin class inherits from this.
Options:
- `readonly_fields`        → id, created_at, updated_at
- `list_per_page`          → 25
- `show_full_result_count` → False (performance)
- `ordering`               → ["-created_at"]
- `date_hierarchy`         → created_at
- Default `list_display`   → id, created_at, updated_at, is_active

### Filters

#### daterange_filter.py (DateRangeFilter)
- Two date picker inputs in admin sidebar: `From` and `To`
- Filters queryset between `date__gte` and `date__lte`
- Configurable target field via `filter_field` attribute, defaults to `created_at`
- Usage: `list_filter = [("created_at", DateRangeFilter)]`

#### exactdate_filter.py (ExactDateFilter)
- Single date picker input in admin sidebar
- Filters queryset by exact date match `date__date=value`
- Configurable target field via `filter_field` attribute, defaults to `created_at`
- Usage: `list_filter = [("created_at", ExactDateFilter)]`

### Actions

#### dedupe_action.py (RemoveDuplicatesAction)
- Registered as: `Remove Duplicates by Fields`
- Configurable via `dedupe_fields` on admin class
- Logic:
  1. Group queryset by declared `dedupe_fields`
  2. Keep most recent record per group (highest `created_at`)
  3. Delete all older duplicates
  4. Show success message with count removed
- Safety rules:
  - Never dedupe if `dedupe_fields` not declared — raise config error
  - Always run in a transaction — rollback if anything fails
  - Log removed records to MdwJobLog before deleting
- Usage:
  ```python
  dedupe_fields = ["email", "phone"]
  actions = [RemoveDuplicatesAction]
  ```

### Admin Registration Rules
- Every model extending AbstractBaseModel gets an admin class
- Domain admin always extends MdwBaseAdmin — never plain ModelAdmin
- Always include DateRangeFilter and ExactDateFilter by default on all admins
- Always include RemoveDuplicatesAction on all admins
- MdwRequestLog and MdwJobLog admins are read-only — no add, change, or delete

---

## DevOps Rules

### Dockerfile
- Generated by `generate_dockerfile.py` — never written manually
- Base image: `python:<python_version>-slim`
- Never install dev dependencies in production image
- Expose port from env var, default 8000
- Copy `scripts/` folder into container
- `RUN chmod +x scripts/entrypoint.sh scripts/cronjobs.sh`
- `ENTRYPOINT ["scripts/entrypoint.sh"]`

### Docker Compose
- Generated by `generate_compose.py` — never written manually
- `docker-compose.yml` → production-safe base
- Always includes: `web`, `db` (mysql), `redis`

### Entrypoint
- Copied from `templates/scripts/entrypoint.sh` — never written manually
- Responsibilities in order:
  1. Wait for DB to be ready (`pg_isready` or `wait-for-it`)
  2. Run migrations (`python manage.py migrate`)
  3. Collect static files if `COLLECT_STATIC=true`
  4. Check `APP_MODE` and start correct process:
     - `APP_MODE=web`    → gunicorn
     - `APP_MODE=worker` → celery worker
     - `APP_MODE=beat`   → celery beat
     - `APP_MODE=cron`   → cronjobs.sh

### Cronjobs
- Only generated if `cronjobs: true` in config
- Uses `supercronic` instead of system cron
- Each entry calls a Django management command
- Entries grouped by service domain

### GitLab CI
- Copied from `templates/gitlab/.gitlab-ci.yml` — never written manually
- Inject project-specific values after copying
- Stages: `lint` → `test` → `build` → `deploy`
- Deploy environments match k8s overlays:
  - `dev`     → auto on push to `develop`
  - `staging` → auto on push to `main`
  - `prod`    → manual trigger only

### Kubernetes
- All files copied from `templates/k8s/` — never written manually
- Base contains: `deployment.yaml`, `service.yaml`, `configmap.yaml`, `secret.yaml`
- `cronjob.yaml` copied only if `cronjobs: true`
- Secrets always in `secret.yaml` — never in configmap
- Overlays override only: image tag, replica count, resource limits

### .env.sample
Generated from declared services and features. Grouped by service:
```
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=*
COLLECT_STATIC=false
APP_MODE=web

# Database
DATABASE_URL=postgres://user:password@db:5432/dbname

# Redis
REDIS_URL=redis://redis:6379/0

# Elasticsearch (if declared)
ELASTICSEARCH_HOST=http://localhost:9200

# SFTP (if declared)
SFTP_HOST=your-sftp-host
SFTP_PORT=22
SFTP_USER=your-sftp-user
SFTP_PASSWORD=your-sftp-password

# Callcenter (if declared)
CALLCENTER_API_KEY=your-api-key
CALLCENTER_TOKEN=your-token
CALLCENTER_BASE_URL=https://your-callcenter-url
MSTEAMS_WEBHOOK_URL=https://your-teams-webhook-url
```
Never include real credentials — sample values only.


