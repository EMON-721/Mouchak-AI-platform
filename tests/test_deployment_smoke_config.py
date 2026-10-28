"""Configuration safety tests; real service checks run in Docker CI, never mock AI."""
import contextlib
import io
import json
import ssl
import unittest
from unittest.mock import patch
from services.model_worker.deployment_smoke import configuration, main, SmokeError


class DeploymentSmokeConfiguration(unittest.TestCase):
    def settings(self):
        return {"PRIVATE_API_URL": "https://backend.example.test", "PUBLIC_ORIGIN": "https://website.example.test",
                "PRIVATE_API_TOKEN": "owned-test-only-secret-" + "X" * 32}

    def test_tls_is_required_and_redirect_credentials_are_refused(self):
        for name in ["PRIVATE_API_URL", "PUBLIC_ORIGIN"]:
            for value in ["http://backend.example.test", "https://user:pass@backend.example.test", "https://backend.example.test/path",
                          "https://backend.example.test?secret=private", "https://backend.example.test/#secret", "https://backend.example.test:0"]:
                with self.subTest(name=name, value=value), self.assertRaises(SmokeError):
                    configuration({**self.settings(), name: value})

    def test_https_configuration_never_disables_certificate_verification(self):
        base, origin, _, context = configuration(self.settings())
        self.assertEqual(base, "https://backend.example.test")
        self.assertEqual(origin, "https://website.example.test")
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        with self.assertRaises(SmokeError):
            configuration({**self.settings(), "MOUCHAK_SMOKE_CA_FILE": "/nonexistent/owned-test-only.pem"})

    def test_invalid_tokens_are_rejected_before_network_access(self):
        for token in ["short", "X" * 513, "X" * 32 + "\n", "X" * 32 + " ", "X" * 32 + "বাংলা"]:
            with self.subTest(token_length=len(token)), self.assertRaises(SmokeError):
                configuration({**self.settings(), "PRIVATE_API_TOKEN": token})

    def test_cli_failure_output_excludes_secrets_and_driver_exception_text(self):
        secret = self.settings()["PRIVATE_API_TOKEN"]
        output = io.StringIO()
        with patch("services.model_worker.deployment_smoke.verify_backend", side_effect=RuntimeError(secret)), contextlib.redirect_stdout(output):
            self.assertEqual(main(), 1)
        self.assertNotIn(secret, output.getvalue())
        self.assertEqual(json.loads(output.getvalue())["secrets_logged"], False)
