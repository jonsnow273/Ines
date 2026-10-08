"""
Unit tests for Megan Authentication System.
Tests database initialization, user registration, validation, password hashing,
token creation/verification, per-user directory creation, and user management.
"""

import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from auth import (
    init_db,
    AuthService,
    UserCreate,
    UserLogin,
)
from auth.database import USERS_DB_PATH, USERS_DATA_DIR, ensure_user_data_dir
from pydantic import ValidationError


class TestAuthSystem(unittest.TestCase):
    TEST_USERS = ["alice_test", "bob_test", "charlie_test"]

    @classmethod
    def _cleanup_test_data(cls):
        from auth.database import get_db
        try:
            with get_db() as db:
                for u in cls.TEST_USERS:
                    db.execute("DELETE FROM users WHERE username = ?", (u,))
                db.commit()
        except Exception:
            pass
        for u in cls.TEST_USERS:
            d = USERS_DATA_DIR / u
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        # Initialize database and clean any previous test data
        init_db()
        cls._cleanup_test_data()

    @classmethod
    def tearDownClass(cls):
        cls._cleanup_test_data()

    def test_01_user_registration(self):
        """Test successful registration and directory creation."""
        test_user = UserCreate(
            username="alice_test",
            password="secretpassword123",
            display_name="Alice Wonderland",
        )
        user = AuthService.register(test_user)
        self.assertEqual(user.username, "alice_test")
        self.assertEqual(user.display_name, "Alice Wonderland")
        self.assertTrue(user.is_active)

        # Verify user data directories exist
        user_dir = USERS_DATA_DIR / "alice_test"
        self.assertTrue(user_dir.exists())
        self.assertTrue((user_dir / "memory").exists())
        self.assertTrue((user_dir / "organizer").exists())
        self.assertTrue((user_dir / "conversations").exists())
        self.assertTrue((user_dir / "settings").exists())

    def test_02_duplicate_username_rejected(self):
        """Test that registering duplicate username raises ValueError."""
        duplicate_user = UserCreate(
            username="alice_test",
            password="anotherpassword",
        )
        with self.assertRaises(ValueError):
            AuthService.register(duplicate_user)

    def test_03_invalid_username_validation(self):
        """Test that invalid usernames are rejected by Pydantic."""
        invalid_usernames = ["a", "123user", "user-with-dashes", "user with spaces", "u" * 35]
        for invalid_name in invalid_usernames:
            with self.subTest(username=invalid_name):
                with self.assertRaises(ValidationError):
                    UserCreate(username=invalid_name, password="validpassword123")

    def test_04_short_password_validation(self):
        """Test that short passwords (<6 chars) are rejected."""
        with self.assertRaises(ValidationError):
            UserCreate(username="bob_test", password="123")

    def test_05_authentication_success_and_failure(self):
        """Test authentication with correct and incorrect credentials."""
        bob = UserCreate(username="bob_test", password="bobs_secure_password")
        AuthService.register(bob)

        # Successful auth
        auth_user = AuthService.authenticate("bob_test", "bobs_secure_password")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.username, "bob_test")
        self.assertIsNotNone(auth_user.last_login)

        # Case-insensitive username login
        auth_user_upper = AuthService.authenticate("BOB_TEST", "bobs_secure_password")
        self.assertIsNotNone(auth_user_upper)

        # Failed auth - wrong password
        failed_auth = AuthService.authenticate("bob_test", "wrong_password")
        self.assertIsNone(failed_auth)

        # Failed auth - non-existent user
        non_existent = AuthService.authenticate("ghost_user", "password123")
        self.assertIsNone(non_existent)

    def test_06_login_and_token_flow(self):
        """Test full login method and token generation/verification."""
        login_res = AuthService.login("alice_test", "secretpassword123")
        self.assertIn("token", login_res)
        self.assertIn("user", login_res)

        token = login_res["token"]
        payload = AuthService.verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.sub, "alice_test")

        # Test invalid token
        invalid_token = token + "corrupted"
        self.assertIsNone(AuthService.verify_token(invalid_token))

        # Test malformed token
        self.assertIsNone(AuthService.verify_token("not-a-valid-token"))

    def test_07_user_lookup_and_listing(self):
        """Test user retrieval and listing."""
        user = AuthService.get_user_by_username("alice_test")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "alice_test")

        users = AuthService.list_users()
        usernames = [u.username for u in users]
        self.assertIn("alice_test", usernames)
        self.assertIn("bob_test", usernames)

    def test_08_deactivate_user(self):
        """Test user deactivation prevents future logins."""
        charlie = UserCreate(username="charlie_test", password="charlie_pass_123")
        AuthService.register(charlie)

        # Confirm can login
        self.assertIsNotNone(AuthService.authenticate("charlie_test", "charlie_pass_123"))

        # Deactivate
        self.assertTrue(AuthService.deactivate_user("charlie_test"))

        # Login should now fail
        self.assertIsNone(AuthService.authenticate("charlie_test", "charlie_pass_123"))

        # Lookup should return None for inactive user
        self.assertIsNone(AuthService.get_user_by_username("charlie_test"))


if __name__ == "__main__":
    print("\nRunning Megan Authentication Unit Tests...\n")
    unittest.main(verbosity=2)
