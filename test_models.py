"""Simple test to load all three models."""

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

