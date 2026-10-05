# 🔐 Local Account & User Isolation System

## Overview
Ines provides a local-first, privacy-preserving user authentication and data isolation system. All credentials, session tokens, and personal artifacts reside exclusively on the user's physical machine without any external telemetry or cloud identity providers.

---

## 🗄️ Architecture & Storage Layout

### 1. Database Schema (`data/users.db`)
User records are persisted in an embedded SQLite database (`users.db`) created under `DATA_DIR`:

```sql
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    display_name  TEXT    DEFAULT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    last_login    TEXT    DEFAULT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1
);
```

### 2. Password Hashing
- **Algorithm**: PBKDF2-HMAC-SHA256
- **Salt**: 16 cryptographically secure random bytes (`os.urandom(16)`)
- **Iterations**: 100,000 rounds
- **Format**: `<salt_hex>$<hash_hex>`
- Constant-time verification using `hmac.compare_digest` to prevent timing attacks.

### 3. Session Tokens
- **Format**: Signed URL-safe Base64 tokens: `<payload_b64>.<sig_b64>`
- **Signing**: HMAC-SHA256 signed with a persistent 256-bit machine secret key (`data/auth_secret.key`).
- **Validity**: 7 days default lifetime (`exp`).
- **Stateless & Fast**: Validated in-memory with constant-time HMAC check without requiring external JWT dependencies.

---

## 📂 Per-User Directory Isolation

When a user is created, Ines automatically generates isolated workspaces under `data/users/<username>/`:

```
data/
└── users/
    ├── alice/
    │   ├── memory/         # Digital Memory: screenshots, OCR text, vector store
    │   ├── organizer/      # File Organizer: user-specific audit logs & rules
    │   ├── conversations/  # Chat history & multi-turn state
    │   └── settings/       # Custom steering presets & user preferences
    └── bob/
        ├── memory/
        ├── organizer/
        ├── conversations/
        └── settings/
```

This guarantees that multiple users sharing the same computer have completely private memory databases and files.

---

## 🌐 API Endpoints (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register new account and initialize user workspace | No |
| `POST` | `/api/auth/login` | Authenticate with credentials and receive Bearer token | No |
| `GET`  | `/api/auth/me` | Fetch active user profile | Yes (Bearer) |
| `POST` | `/api/auth/logout` | Confirm session logout | Yes (Bearer) |
| `GET`  | `/api/auth/status` | Check authentication status | Optional |

### Usage with Authorization Header
Protected API endpoints accept the token in the HTTP `Authorization` header:
```http
GET /api/auth/me HTTP/1.1
Authorization: Bearer <your_session_token>
```

---

## 💻 Terminal CLI Commands

```bash
# Register a new local account
python main.py --register

# List registered local accounts
python main.py --list-users
```
