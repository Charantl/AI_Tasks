#!/usr/bin/env python3
"""
Verify that all database tables were created successfully.
"""

from app.db.session import engine
from sqlalchemy import text

def verify_tables():
    """Verify that all expected tables exist in the database."""
    expected_tables = [
        'users', 'artists', 'albums', 'songs', 'playlists', 'playlist_songs',
        'subscriptions', 'comments', 'liked_songs', 'play_history', 
        'analytics', 'embeddings'
    ]
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            existing_tables = [row[0] for row in result]
            
            print("✅ Database connection successful")
            print(f"📋 Found {len(existing_tables)} tables in database:")
            
            for table in existing_tables:
                print(f"   - {table}")
            
            print(f"\n🔍 Checking for expected tables:")
            missing_tables = []
            for expected_table in expected_tables:
                if expected_table in existing_tables:
                    print(f"   ✅ {expected_table}")
                else:
                    print(f"   ❌ {expected_table} (missing)")
                    missing_tables.append(expected_table)
            
            if not missing_tables:
                print(f"\n🎉 All {len(expected_tables)} expected tables were created successfully!")
                return True
            else:
                print(f"\n⚠️  {len(missing_tables)} tables are missing: {missing_tables}")
                return False
                
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    verify_tables() 