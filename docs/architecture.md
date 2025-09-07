osint_crawler/
│
├── app/
│   ├── models/         # Data models (MongoDB schemas, SQLAlchemy models, etc.)
│   ├── views/          # API endpoints (Flask routes, JSON responses)
│   ├── controllers/    # Business logic (crawler orchestration, data processing)
│   ├── services/       # External integrations (scraping libs, APIs, ML modules)
│   ├── utils/          # Helper functions (logging, validators, etc.)
│   ├── __init__.py
│   └── config.py
│
├── crawler/            # Core crawling logic
│   ├── base_crawler.py
│   ├── web_crawler.py
│   ├── social_media_crawler.py
│   └── ...
│
├── tests/              # Unit tests
├── requirements.txt
└── run.py              # Flask entry point
