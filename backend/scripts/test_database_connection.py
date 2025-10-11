#!/usr/bin/env python3
"""
Phase 4: Database Vector Setup - Connection Test Script
Tests SQLite and Redis connections
"""

import sqlite3
import sys
from pathlib import Path

import redis

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_sqlite_connection():
    """Test SQLite database connection and query"""
    print("🔍 Testing SQLite connection...")

    try:
        # Connect to database
        db_path = "data/autoforge_dev.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT COUNT(*) FROM test_prompts")
        count = cursor.fetchone()[0]
        print("✅ SQLite connection successful!")
        print(f"   - Database: {db_path}")
        print(f"   - Test prompts count: {count}")

        # Show sample data
        cursor.execute("SELECT id, name FROM test_prompts LIMIT 2")
        rows = cursor.fetchall()
        print("   - Sample data:")
        for row in rows:
            print(f"     • {row[0]}: {row[1]}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")

    try:
        # Connect to Redis
        r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

        # Test ping
        if r.ping():
            print("✅ Redis connection successful!")

            # Test set/get
            r.set("test_key", "AutoForgeNexus")
            value = r.get("test_key")
            print(f"   - Test set/get: {value}")

            # Clean up
            r.delete("test_key")

            # Show info
            info = r.info("server")
            print(f"   - Redis version: {info.get('redis_version', 'Unknown')}")
            print("   - Port: 6379")

            return True

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("\n🔍 Testing SQLAlchemy connection...")

    try:
        from sqlalchemy import create_engine, text

        # Create engine
        engine = create_engine("sqlite:///data/autoforge_dev.db")

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM test_users"))
            count = result.scalar()
            print("✅ SQLAlchemy connection successful!")
            print(f"   - Test users count: {count}")

        return True

    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False


def main():
    """Run all connection tests"""
    print("=" * 60)
    print("Phase 4: Database Vector Environment - Connection Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("SQLite", test_sqlite_connection()))
    results.append(("Redis", test_redis_connection()))
    results.append(("SQLAlchemy", test_sqlalchemy_connection()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("-" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name:15} : {status}")

    print("=" * 60)

    # Overall status
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n🎉 All database connections successful!")
        print("✅ Phase 4 Database Environment Setup Complete")
    else:
        print("\n⚠️ Some connections failed. Please check the configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
