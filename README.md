bank_statement_analyzer/
├── apps/
│   ├── __init__.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   └── urls.py
│   ├── banks/
│   │   ├── __init__.py
│   │   ├── bank_router.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── hdfc.py
│   │   │   ├── icici.py
│   │   │   └── axis.py
│   ├── statements/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── storage.py
│   │   └── tasks.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── summary.py
│   │   ├── anomaly.py
│   │   └── classifier.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── middleware.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── utils.py
│   │   ├── constants.py
│   │   ├── enums.py
│   │   └── decorators.py
│   ├── webhooks/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   └── dispatcher.py
│   └── ai_models/
│       ├── __init__.py
│       ├── layout_parser.py
│       └── classifier_model.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── prod.py
│   │   └── celery.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── cronjobs/
│   ├── __init__.py
│   ├── retry_failed_uploads.py
│   ├── transaction_cron.py
│   └── celery_tasks.py
├── scripts/
│   ├── ingest_samples.py
│   ├── migrate_uploads.py
│   └── seed_clients.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/
├── media/
├── static/
├── templates/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── celery_worker.dockerfile
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env
├── .gitignore
├── manage.py
├── README.md

# config/settings/base.py
- Common Django settings including:
  - INSTALLED_APPS with custom apps from "apps/"
  - Middleware
  - TEMPLATES
  - REST_FRAMEWORK config
  - AWS/S3 config placeholders

# config/settings/local.py
- DEBUG = True
- DATABASES with local PostgreSQL
- Local file storage

# config/settings/prod.py
- DEBUG = False
- ALLOWED_HOSTS
- AWS S3 storage settings
- Security settings

# config/settings/celery.py
- CELERY_BROKER_URL (Redis)
- CELERY_ACCEPT_CONTENT = ['json']
- CELERY_TASK_SERIALIZER = 'json'

# .env
- SECRET_KEY
- DEBUG
- DATABASE_URL
- ALLOWED_HOSTS
- AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_STORAGE_BUCKET_NAME
- CELERY_BROKER_URL

# docker/Dockerfile
- Based on python:3.11-slim
- Uses pip + poetry or requirements
- Collectstatic, migrate, runserver

# docker/celery_worker.dockerfile
- Same base as Dockerfile
- Starts Celery worker with Django context

# docker/docker-compose.yml
- django service
- celery worker
- redis
- postgres

Ready to generate exact contents for each file?
