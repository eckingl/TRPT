# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

农业土壤普查报告生成系统 (Agricultural Soil Survey Report Generation System) - A local desktop application that processes soil survey data and generates Word reports with charts. The system is designed to be packaged as a standalone Windows executable.

## Development Commands

### Backend (Python)
```bash
cd backend

# Run development server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Lint check
ruff check .

# Format code
ruff format .

# Type check
mypy .

# Run tests
pytest
pytest tests/test_health.py -v  # single test file
```

### Frontend (Vue 3 + Vite)
```bash
cd frontend

# Install dependencies
npm install

# Development server (port 5173)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Full Application
```bash
# Run from project root (after building frontend)
cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# Then visit http://localhost:8000
```

## Architecture

```
TRPC/
├── backend/                    # FastAPI backend (Python 3.11+)
│   ├── app/
│   │   ├── main.py            # FastAPI entry point, creates app
│   │   ├── config.py          # Global settings (paths, env vars)
│   │   ├── api/               # API route handlers
│   │   │   ├── upload.py      # File upload endpoints
│   │   │   ├── report.py      # Report generation endpoints
│   │   │   ├── config.py      # Configuration endpoints
│   │   │   └── data_manage.py # Data management endpoints
│   │   ├── core/              # Shared utilities
│   │   │   ├── data/          # CSV/Excel loading, data processing
│   │   │   ├── chart/         # matplotlib chart generation
│   │   │   ├── word/          # python-docx-template rendering
│   │   │   ├── ai/            # Qwen AI client integration
│   │   │   └── database.py    # SQLite database (aiosqlite)
│   │   ├── topics/            # Report topic modules
│   │   │   ├── base.py        # BaseTopic abstract class
│   │   │   └── attribute_map/ # Attribute map topic implementation
│   │   └── models/            # Pydantic schemas
│   ├── templates/             # Word document templates (.docx)
│   ├── output/                # Generated reports
│   └── uploads/               # Uploaded data files
│
├── frontend/                   # Vue 3 frontend
│   └── src/
│       ├── views/             # Page components (Home, Upload, Config, Report)
│       ├── components/        # Reusable components
│       ├── api/index.js       # Axios API client
│       ├── stores/project.js  # Pinia state management
│       └── router/index.js    # Vue Router configuration
│
└── docs/技术路线.md            # Technical documentation
```

## Key Patterns

### Topic System
Topics are report types that follow a consistent pattern:
1. Extend `BaseTopic` class in `backend/app/topics/base.py`
2. Implement `process_data()`, `generate_charts()`, `generate_report()`
3. Register topic in `backend/app/topics/__init__.py`

### Data Flow
```
CSV/Excel upload → pandas DataFrame → data processing →
statistics dict → matplotlib charts → Word template rendering → .docx output
```

### API Conventions
- All API routes prefixed with `/api/`
- Use Pydantic models for request/response validation
- Async handlers with FastAPI

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + pandas + matplotlib + python-docx-template |
| Frontend | Vue 3 + Element Plus + Pinia + Vue Router |
| Database | SQLite (aiosqlite) |
| Build | Vite (frontend), PyInstaller (exe) |

## Code Style

### Python (PEP 8 + Ruff)
- Files: `snake_case.py`
- Functions: `snake_case`, verb prefix (`get_`, `calc_`, `validate_`)
- Classes: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Type hints required on all functions
- Maximum function length: 30 lines (50 absolute max)

### Frontend
- Vue 3 Composition API with `<script setup>`
- Element Plus components

## Quality Requirements

Before committing:
```bash
# Backend
ruff check . && ruff format . && mypy . && pytest

# Frontend
npm run build
```

Forbidden:
- `any` type (use `unknown`)
- `@ts-ignore` / `eslint-disable`
- Empty catch blocks
- Hardcoded credentials
- Bare `except:` clauses

## Current Stage: P6 完成

详细开发计划和架构说明请参考：`docs/开发阶段计划.md`
