---
name: Pydantic Data Models
overview: "Create Pydantic data models for User, Session, and SessionText with CSV loading functionality. The models will represent the hierarchical relationship: User -> Sessions -> SessionTexts."
todos:
  - id: create-models-dir
    content: Create models/ directory structure with __init__.py
    status: completed
  - id: session-text-model
    content: Create SessionText Pydantic model with CSV loader
    status: completed
    dependencies:
      - create-models-dir
  - id: session-model
    content: Create Session Pydantic model with messages list and CSV loader
    status: completed
    dependencies:
      - session-text-model
  - id: user-model
    content: Create User Pydantic model with sessions list and CSV loader
    status: completed
    dependencies:
      - session-model
  - id: data-loader
    content: Create DataLoader class to load and link all models
    status: completed
    dependencies:
      - user-model
  - id: requirements
    content: Create requirements.txt with pydantic dependency
    status: completed
---

# Pydantic Data Models for Data Analysis

## Data Model Architecture

```mermaid
classDiagram
    class User {
        +int id
        +UUID uuid
        +str nick_name
        +datetime created_at
        +str email
        +list~Session~ sessions
        +load_from_csv()
    }
    class Session {
        +int id
        +UUID uuid
        +UUID from_user_uuid
        +datetime created_at
        +float duration
        +str summary
        +list~SessionText~ messages
        +load_from_csv()
    }
    class SessionText {
        +int id
        +UUID uuid
        +UUID session_uuid
        +datetime start_at
        +str text
        +str text_translated
        +int speaker
        +load_from_csv()
    }
    User "1" --> "*" Session : has many
    Session "1" --> "*" SessionText : has many
```



## File Structure

```javascript
models/
  __init__.py          # Export all models
  session_text.py      # SessionText model
  session.py           # Session model  
  user.py              # User model
  loader.py            # CSV loading utilities
```



## Implementation Details

### 1. SessionText Model (`models/session_text.py`)

- Fields from `session_text.csv`: id, uuid, session_uuid, start_at, text, text_translated, speaker, is_input, type
- Class method `load_from_csv()` to parse CSV file

### 2. Session Model (`models/session.py`)

- Fields from `session.csv`: id, uuid, from_user_uuid, session_type, session_status, created_at, duration, summary, etc.
- A `messages: list[SessionText]` field to hold conversation history
- Class method `load_from_csv()` to parse CSV file

### 3. User Model (`models/user.py`)

- Fields from `user.csv`: id, uuid, nick_name, created_at, email, credits, etc.
- A `sessions: list[Session]` field to hold user's sessions
- Class method `load_from_csv()` to parse CSV file

### 4. Data Loader (`models/loader.py`)

- `DataLoader` class to load all CSVs and link the relationships
- Method to populate User.sessions and Session.messages

## Dependencies