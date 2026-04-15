# Environment and Configuration

## Purpose

This document defines how AION manages environment variables and configuration.

Proper configuration ensures:

- security  
- flexibility  
- scalability  
- clean deployment  

Without it:

- secrets leak  
- code becomes hardcoded  
- environments break  

---

## Core Principle

Configuration must be external.

Never hardcode:

- API keys  
- database credentials  
- tokens  
- environment-specific values  

---

## Environment File

Use `.env` file for local development.

Example:

OPENAI_API_KEY=your_openai_key  
TELEGRAM_BOT_TOKEN=your_telegram_token  
DATABASE_URL=postgresql://user:password@db:5432/aion  
APP_ENV=development  
APP_PORT=8000  

---

## Required Variables

### Core

OPENAI_API_KEY  
Used for LLM calls  

---

TELEGRAM_BOT_TOKEN  
Used for Telegram bot  

---

DATABASE_URL  
Used for PostgreSQL connection  

---

APP_ENV  
Defines environment:

- development  
- staging  
- production  

---

APP_PORT  
Port for FastAPI server  

---

## Optional Variables

REDIS_URL  
Used if Redis is added  

---

LOG_LEVEL  
Options:

- debug  
- info  
- warning  
- error  

---

REFLECTION_INTERVAL  
Controls background loop frequency  

---

PROACTIVE_ENABLED  
Enable/disable proactive system  

---

## Configuration Loading

Use a config loader in Python.

Example:

- pydantic settings  
- dotenv  

Config should be loaded once at startup.

---

## Config Structure (Example)

config:

- api_keys  
- database  
- runtime  
- features  

---

## Example Config Object

{
  "api_keys": {
    "openai": "...",
    "telegram": "..."
  },
  "database": {
    "url": "..."
  },
  "runtime": {
    "env": "development",
    "port": 8000
  }
}

---

## Environment Separation

Different environments must have different configs.

### Development

- local DB  
- debug logs  
- test keys  

---

### Staging

- production-like setup  
- limited access  

---

### Production

- real keys  
- secure environment  
- optimized settings  

---

## Secrets Management

Never:

- commit `.env` to Git  
- expose keys in logs  
- share credentials  

Use:

- .env locally  
- environment variables in VPS  
- secret managers in future  

---

## Docker Integration

Pass variables via:

- docker-compose.yml  
- environment section  

Example:

environment:
- OPENAI_API_KEY=${OPENAI_API_KEY}
- DATABASE_URL=${DATABASE_URL}

---

## Validation

At startup, system must:

- check required variables  
- fail fast if missing  
- log clear error  

---

## Default Values

Only safe defaults allowed:

- port  
- log level  

Never default:

- API keys  
- database credentials  

---

## Feature Flags

Use config to enable/disable features.

Examples:

- proactive system  
- reflection loop  
- debug mode  

---

## Runtime Access

All modules should access config through:

- central config object  
- not directly from environment  

---

## Logging Config

Config should define:

- log level  
- output format  
- debug mode  

---

## Example Usage

Instead of:

hardcoded API key  

Use:

config.api_keys.openai  

---

## Future Extensions

- config versioning  
- dynamic config reload  
- remote config service  

---

## Final Principle

Configuration separates system from environment.

If config is clean:

- deployment is easy  
- scaling is easy  
- debugging is easier  

If config is messy:

- everything becomes fragile