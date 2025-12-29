# Data Insights

A Python data analysis tool for loading, processing, and analyzing phone call session data with conversation transcripts. Built with Pydantic for type-safe data modeling and validation.

## Features

- **Type-Safe Data Models**: Pydantic-based models with automatic validation
- **Efficient CSV Loading**: Fast CSV parsing with error handling for malformed data
- **Automatic Relationship Linking**: Automatically connects users → sessions → messages
- **Time-Based Filtering**: Filter users by registration date (configurable)
- **Data Export**: Export structured data to JSON format
- **Flexible Queries**: Quick lookups by UUID with optimized dictionaries

## Data Hierarchy

The system models a three-level hierarchical structure:

```
User (Account holder)
 │
 ├─► Session (Phone call instance)
 │    │
 │    ├─► SessionText (Individual message)
 │    ├─► SessionText (Individual message)
 │    └─► SessionText (Individual message)
 │
 ├─► Session (Phone call instance)
 │    │
 │    └─► SessionText (Individual message)
 │
 └─► Session (Phone call instance)
      └─► ...
```

**Relationships:**
- One User → Many Sessions (one-to-many)
- One Session → Many SessionTexts (one-to-many)
- Sessions belong to Users via `from_user_uuid`
- SessionTexts belong to Sessions via `session_uuid`

## Data Models

### User
Represents a user account in the system.

**Fields:**
- `uuid`: Unique identifier
- `nick_name`: Display name
- `email`: Email address
- `credits`: Account credit balance
- `registration_time`: When the user registered
- `sessions`: List of user's call sessions (auto-populated)

### Session
Represents a phone call session between parties.

**Fields:**
- `uuid`: Unique session identifier
- `from_user_uuid`: UUID of the caller
- `session_type`: Type of session (0 = standard call)
- `begin_at`: Call start time
- `end_at`: Call end time
- `duration`: Call duration in seconds
- `from_language`: Caller's language code
- `to_language`: Recipient's language code
- `is_paid`: Whether the call was paid (boolean)
- `is_translation_enabled`: Whether translation was active (boolean)
- `is_ai_call`: Whether this was an AI-assisted call (boolean)
- `messages`: List of conversation messages (auto-populated)

### SessionText
Represents individual messages within a conversation.

**Fields:**
- `id`: Numeric ID
- `uuid`: Unique message identifier
- `session_uuid`: Parent session UUID
- `start_at`: Message timestamp
- `text`: Original message text
- `text_translated`: Translated text (if applicable)
- `speaker`: Speaker identifier (1 = first party, 2 = second party)
- `is_input`: Input flag
- `type`: Message type

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd data_insights
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.10+
- pydantic >= 2.0.0

## Usage

### Basic Usage

```python
from models import DataLoader

# Initialize the loader with your data directory
loader = DataLoader("raw_data/")

# Load all data and establish relationships
loader.load_all()

# Access the data
print(f"Loaded {len(loader.users)} users")
print(f"Loaded {len(loader.sessions)} sessions")
print(f"Loaded {len(loader.session_texts)} messages")
```

### Working with the Data Hierarchy

```python
# Navigate the three-level hierarchy
for user in loader.users:
    print(f"User: {user.nick_name}")
    print(f"  Total Sessions: {len(user.sessions)}")
    
    for session in user.sessions:
        print(f"    Session: {session.uuid}")
        print(f"      Duration: {session.duration}s")
        print(f"      AI Call: {session.is_ai_call}")
        print(f"      Translation: {session.is_translation_enabled}")
        print(f"      Messages: {len(session.messages)}")
        
        for message in session.messages:
            print(f"        [{message.start_at}] Speaker {message.speaker}: {message.text[:50]}...")
```

### UUID Lookups

```python
from uuid import UUID

# Fast lookup by UUID using internal dictionaries
user = loader.get_user_by_uuid(some_uuid)
session = loader.get_session_by_uuid(session_uuid)
```

### Filtering and Analysis

```python
# Find AI calls
ai_sessions = [s for s in loader.sessions if s.is_ai_call]

# Find paid sessions
paid_sessions = [s for s in loader.sessions if s.is_paid]

# Find sessions with translation enabled
translated_sessions = [s for s in loader.sessions if s.is_translation_enabled]

# Find long calls (> 30 minutes)
long_calls = [s for s in loader.sessions if s.duration > 1800]

# Find users with multiple sessions
active_users = [u for u in loader.users if len(u.sessions) > 5]
```

### Statistics

```python
# Get overview statistics
stats = loader.stats
print(stats)
# Returns:
# {
#     'users': <count>,
#     'sessions': <count>,
#     'session_texts': <count>,
#     'users_with_sessions': <count>,
#     'sessions_with_messages': <count>
# }
```

### Export to JSON

```python
import json

# Export structured data
export_data = {
    "stats": loader.stats,
    "users": []
}

for user in loader.users[:10]:  # Sample of users
    user_data = {
        "uuid": str(user.uuid),
        "nick_name": user.nick_name,
        "session_count": len(user.sessions),
        "sessions": [
            {
                "uuid": str(session.uuid),
                "duration": session.duration,
                "is_ai_call": session.is_ai_call,
                "message_count": len(session.messages)
            }
            for session in user.sessions
        ]
    }
    export_data["users"].append(user_data)

with open("export.json", "w") as f:
    json.dump(export_data, f, indent=2)
```

## Configuration

Edit `config.py` to customize behavior:

```python
# Number of days to look back for user registrations
# Only users registered within this period will be loaded
REGISTRATION_DAYS = 45
```

## Project Structure

```
data_insights/
├── raw_data/              # CSV data files
│   ├── user.csv          # User records
│   ├── session.csv       # Session/call records
│   └── session_text.csv  # Conversation messages
├── models/                # Data models
│   ├── __init__.py       # Package initialization
│   ├── user.py           # User model
│   ├── session.py        # Session model
│   ├── session_text.py   # SessionText model
│   └── loader.py         # DataLoader for loading and linking
├── config.py             # Configuration settings
├── test_models.py        # Example usage and testing
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Data Format

### CSV Files

Place your CSV files in the `raw_data/` directory:

- **user.csv**: Must contain columns: `uuid`, `nick_name`, `email`, `credits`, `created_at`
- **session.csv**: Must contain columns: `uuid`, `from_user_uuid`, `session_type`, `begin_at`, `end_at`, `duration`, `from_language`, `to_language`, `is_paid`, `is_translation_enabled`, `is_ai_call`
- **session_text.csv**: Must contain columns: `id`, `uuid`, `session_uuid`, `start_at`, `text`, `text_translated`, `speaker`, `is_input`, `type`

### Boolean Fields

Boolean fields in CSV (like `is_paid`, `is_translation_enabled`, `is_ai_call`) can be:
- `0` or `1`
- `true` or `false`
- `yes` or `no`

They will be automatically converted to Python boolean values.

## How It Works

1. **Loading**: CSV files are parsed into Pydantic models with validation
2. **Filtering**: Users are filtered by registration date (configurable via `REGISTRATION_DAYS`)
3. **Indexing**: Internal dictionaries are built for fast UUID lookups
4. **Linking**: Relationships are established:
   - SessionTexts are grouped by `session_uuid` and assigned to Sessions
   - Sessions are grouped by `from_user_uuid` and assigned to Users
5. **Sorting**: 
   - Messages within sessions are sorted by `start_at` timestamp
   - Sessions within users are sorted by `begin_at` timestamp

## Running Tests

Run the included test script to verify everything works:

```bash
python3 test_models.py
```

This will:
1. Load all data from CSV files
2. Display statistics
3. Show sample data structure
4. Export a sample to `models/models_export.json`

## Error Handling

The loader gracefully handles common data issues:
- **Malformed rows**: Skipped automatically
- **Missing values**: Use sensible defaults (empty strings, 0, None)
- **Invalid UUIDs**: Rows with invalid UUIDs are skipped
- **Invalid dates**: Set to None if unparseable
- **Invalid numbers**: Default to 0 or 0.0

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
