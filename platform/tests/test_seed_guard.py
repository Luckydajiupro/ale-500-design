"""Demo identities are opt-in outside a local environment."""

from __future__ import annotations

import unittest

from seed import demo_seed_allowed, seed


class DemoTargetTests(unittest.TestCase):
    def test_local_environment_is_allowed_by_default(self) -> None:
        self.assertTrue(demo_seed_allowed({"ALE_ENV": "local"}))

    def test_non_local_environment_requires_explicit_flag(self) -> None:
        self.assertFalse(demo_seed_allowed({}))
        self.assertFalse(demo_seed_allowed({"ALE_ENV": "production"}))
        self.assertFalse(demo_seed_allowed({"ALE_ENV": "staging"}))
        self.assertTrue(
            demo_seed_allowed({"ALE_ENV": "production", "ALE_ALLOW_DEMO_SEED": "1"})
        )

    def test_seed_refuses_before_opening_database(self) -> None:
        with self.assertRaises(RuntimeError):
            seed("/does/not/exist/platform.db", "AleDemo123!", allow_demo=False)


if __name__ == "__main__":
    unittest.main()
