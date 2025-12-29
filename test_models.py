"""Simple test to load all three models."""

import json
from pathlib import Path
from models import DataLoader

# Load all data
loader = DataLoader("raw_data/")
loader.load_all()
 
# Print stats
print("=== Data Loaded ===")
print(f"Users: {loader.stats['users']}")
print(f"Sessions: {loader.stats['sessions']}")
print(f"Session Texts: {loader.stats['session_texts']}")
print(f"Users with sessions: {loader.stats['users_with_sessions']}")
print(f"Sessions with messages: {loader.stats['sessions_with_messages']}")

# Show first user with sessions
print("\n=== Sample User ===")
for user in loader.users[:3]:
    if user.sessions:
        print(f"User: {user.nick_name} (uuid={user.uuid})")
        print(f"  Email: {user.email}")
        print(f"  Credits: {user.credits}")
        print(f"  Registration Time: {user.registration_time}")
        print(f"  Sessions: {len(user.sessions)}")
        if user.sessions[0].messages:
            print(f"  First session messages: {len(user.sessions[0].messages)}")
        break

# Export models to JSON for validation
print("\n=== Exporting Models to JSON ===")
output_file = Path("models") / "models_export.json"

# Export first 5 users with their sessions and messages
export_data = {
    "stats": loader.stats,
    "sample_users": []
}

for user in loader.users[:5]:
    user_data = {
        "uuid": str(user.uuid),
        "nick_name": user.nick_name,
        "email": user.email,
        "credits": user.credits,
        "registration_time": user.registration_time.isoformat() if user.registration_time else None,
        "sessions": []
    }
    
    for session in user.sessions[:3]:  # First 3 sessions per user
        session_data = {
            "uuid": str(session.uuid),
            "from_user_uuid": str(session.from_user_uuid) if session.from_user_uuid else None,
            "session_type": session.session_type,
            "begin_at": session.begin_at.isoformat() if session.begin_at else None,
            "end_at": session.end_at.isoformat() if session.end_at else None,
            "duration": session.duration,
            "from_language": session.from_language,
            "to_language": session.to_language,
            "is_paid": session.is_paid,
            "is_translation_enabled": session.is_translation_enabled,
            "is_ai_call": session.is_ai_call,
            "messages": []
        }
        
        for message in session.messages[:5]:  # First 5 messages per session
            message_data = {
                "uuid": str(message.uuid),
                "session_uuid": str(message.session_uuid),
                "start_at": message.start_at.isoformat() if message.start_at else None,
                "text": message.text,
                "text_translated": message.text_translated,
                "speaker": message.speaker,
                "is_input": message.is_input,
                "type": message.type
            }
            session_data["messages"].append(message_data)
        
        user_data["sessions"].append(session_data)
    
    export_data["sample_users"].append(user_data)

# Write to JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(export_data, f, indent=2, ensure_ascii=False)

print(f"Models exported to: {output_file}")
print(f"Exported {len(export_data['sample_users'])} users with their sessions and messages")

