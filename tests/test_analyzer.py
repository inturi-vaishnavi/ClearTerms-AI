import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import analyzer
from analyzer import (
    DEFAULT_MODEL,
    MAX_POLICY_LENGTH,
    AnalysisServiceError,
    MissingAPIKeyError,
    ModelConfigurationError,
    ModelResponseError,
    PolicyInputError,
    analyze_policy,
)


POLICY_TEXT = (
    "We collect your email address to create your account. "
    "We share usage data with Example Metrics."
)


def valid_model_response(evidence: str = "We collect your email address") -> str:
    stated_finding = {
        "explanation": "The service collects an email address.",
        "evidence": evidence,
        "status": "Explicitly stated",
    }
    not_found_finding = {
        "explanation": "No retention period was found in the supplied text.",
        "evidence": "",
        "status": "Not found in provided text",
    }
    return json.dumps(
        {
            "summary": stated_finding,
            "data_collected": stated_finding,
            "information_sharing": {
                "explanation": "Usage data is shared with an analytics provider.",
                "evidence": "We share usage data with Example Metrics.",
                "status": "Explicitly stated",
            },
            "retention_and_deletion": not_found_finding,
            "important_clauses": [],
        }
    )


def make_model_client(response_text: str):
    return SimpleNamespace(
        models=SimpleNamespace(
            generate_content=unittest.mock.Mock(
                return_value=SimpleNamespace(text=response_text)
            )
        )
    )


class AnalyzePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.environment_loader = patch("analyzer._load_environment")
        self.environment_loader.start()

    def tearDown(self) -> None:
        self.environment_loader.stop()

    def test_empty_input_is_rejected_without_calling_model(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch("analyzer._create_client") as create_client:
                for policy_text in ("", " \n "):
                    with self.subTest(policy_text=policy_text):
                        with self.assertRaises(PolicyInputError):
                            analyze_policy(policy_text)

        create_client.assert_not_called()

    def test_oversized_input_is_rejected_without_calling_model(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch("analyzer._create_client") as create_client:
                with self.assertRaises(PolicyInputError):
                    analyze_policy("x" * (MAX_POLICY_LENGTH + 1))

        create_client.assert_not_called()

    def test_missing_api_key_is_reported(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("analyzer._create_client") as create_client:
                with self.assertRaises(MissingAPIKeyError):
                    analyze_policy(POLICY_TEXT)

        create_client.assert_not_called()

    def test_plain_text_model_output_matches_reported_json_parse_failure(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            client = make_model_client(
                "I cannot provide a JSON response for this request."
            )
            with patch("analyzer._create_client", return_value=client):
                with self.assertRaisesRegex(
                    ModelResponseError,
                    "The analysis service returned malformed JSON.",
                ):
                    analyze_policy(POLICY_TEXT)

    def test_json_surrounded_by_whitespace_is_accepted(self) -> None:
        response = f"\n  {valid_model_response()} \t"
        result = analyzer._parse_response(response, POLICY_TEXT)

        self.assertEqual(
            result["data_collected"]["evidence"],
            "We collect your email address",
        )

    def test_markdown_json_code_fence_is_accepted(self) -> None:
        response = f"```json\n{valid_model_response()}\n```"
        result = analyzer._parse_response(response, POLICY_TEXT)

        self.assertEqual(
            result["data_collected"]["evidence"],
            "We collect your email address",
        )

    def test_prose_around_json_code_fence_is_rejected(self) -> None:
        response = f"Here is the result:\n```json\n{valid_model_response()}\n```"

        with self.assertRaisesRegex(ModelResponseError, "malformed JSON"):
            analyzer._parse_response(response, POLICY_TEXT)

    def test_invalid_status_is_rejected(self) -> None:
        response = json.loads(valid_model_response())
        response["data_collected"]["status"] = "Probably"

        with self.assertRaisesRegex(ModelResponseError, "invalid finding"):
            analyzer._parse_response(json.dumps(response), POLICY_TEXT)

    def test_missing_finding_field_is_rejected(self) -> None:
        response = json.loads(valid_model_response())
        del response["data_collected"]["evidence"]

        with self.assertRaisesRegex(ModelResponseError, "invalid finding"):
            analyzer._parse_response(json.dumps(response), POLICY_TEXT)

    def test_extra_top_level_field_is_rejected(self) -> None:
        response = json.loads(valid_model_response())
        response["overall_score"] = 90

        with self.assertRaisesRegex(ModelResponseError, "incomplete response"):
            analyzer._parse_response(json.dumps(response), POLICY_TEXT)

    def test_verbatim_evidence_is_accepted(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            client = make_model_client(valid_model_response())
            with patch("analyzer._create_client", return_value=client):
                result = analyze_policy(POLICY_TEXT)

        self.assertEqual(
            result["data_collected"]["evidence"],
            "We collect your email address",
        )
        self.assertIn("does not prove", result["missing_information_note"])

    def test_unsupported_evidence_excerpt_is_rejected(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            client = make_model_client(
                valid_model_response("We collect your phone number")
            )
            with patch("analyzer._create_client", return_value=client):
                with self.assertRaisesRegex(ModelResponseError, "could not be verified"):
                    analyze_policy(POLICY_TEXT)

        self.assertEqual(client.models.generate_content.call_count, 2)

    def test_whitespace_variant_returns_exact_source_excerpt(self) -> None:
        policy_text = "We collect your email\u00a0address for your account."
        finding = {
            "explanation": "The service collects an email address.",
            "evidence": "We collect your email address",
            "status": "Explicitly stated",
        }

        result = analyzer._validate_finding(finding, policy_text)

        self.assertEqual(result["evidence"], "We collect your email\u00a0address")

    def test_canonical_unicode_variant_returns_exact_source_excerpt(self) -> None:
        policy_text = "We collect your cafe\u0301 preference."
        finding = {
            "explanation": "The service collects a cafe preference.",
            "evidence": "We collect your café preference.",
            "status": "Explicitly stated",
        }

        result = analyzer._validate_finding(finding, policy_text)

        self.assertEqual(result["evidence"], "We collect your cafe\u0301 preference.")

    def test_invalid_evidence_retries_once_with_corrective_prompt(self) -> None:
        client = make_model_client("")
        client.models.generate_content.side_effect = [
            SimpleNamespace(text=valid_model_response("Invented data collection")),
            SimpleNamespace(text=valid_model_response()),
        ]
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch("analyzer._create_client", return_value=client):
                result = analyze_policy(POLICY_TEXT)

        self.assertEqual(
            result["data_collected"]["evidence"],
            "We collect your email address",
        )
        self.assertEqual(client.models.generate_content.call_count, 2)
        retry_prompt = client.models.generate_content.call_args.kwargs["contents"]
        self.assertIn("previous response included an excerpt", retry_prompt)

    def test_api_failure_is_safe_and_does_not_expose_error_details(self) -> None:
        secret = "private-test-key"
        with patch.dict(os.environ, {"GEMINI_API_KEY": secret}):
            client = make_model_client("")
            client.models.generate_content.side_effect = RuntimeError(
                f"request failed with {secret}"
            )
            with patch("analyzer._create_client", return_value=client):
                with self.assertRaises(AnalysisServiceError) as error:
                    analyze_policy(POLICY_TEXT)

        self.assertNotIn(secret, str(error.exception))

    def test_model_and_prompt_are_passed_to_mock_client(self) -> None:
        response = valid_model_response()
        client = make_model_client(response)
        with patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "test-key",
                "CLEARTERMS_MODEL": "gemma-test-model",
            },
        ):
            with patch("analyzer._create_client", return_value=client) as factory:
                analyze_policy(POLICY_TEXT)

        factory.assert_called_once_with("test-key")
        model, request = client.models.generate_content.call_args
        self.assertEqual(request["model"], "gemma-test-model")
        self.assertIn(POLICY_TEXT, request["contents"])
        self.assertEqual(
            request["config"].response_mime_type,
            "application/json",
        )
        self.assertEqual(
            request["config"].response_schema["required"],
            list(analyzer.RESULT_FIELDS),
        )
        self.assertEqual(model, ())

    def test_default_model_is_used_when_not_configured(self) -> None:
        client = make_model_client(valid_model_response())
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch("analyzer._create_client", return_value=client):
                analyze_policy(POLICY_TEXT)

        self.assertEqual(
            client.models.generate_content.call_args.kwargs["model"],
            "gemma-4-26b-a4b-it",
        )
        self.assertEqual(DEFAULT_MODEL, "gemma-4-26b-a4b-it")

    def test_non_gemma_model_configuration_is_rejected(self) -> None:
        with patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "test-key",
                "CLEARTERMS_MODEL": "other-model",
            },
        ):
            with patch("analyzer._create_client") as create_client:
                with self.assertRaises(ModelConfigurationError):
                    analyze_policy(POLICY_TEXT)

        create_client.assert_not_called()

    def test_dotenv_loads_from_project_root_without_overriding_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(
                "GEMINI_API_KEY=file-key\nCLEARTERMS_MODEL=file-model\n",
                encoding="utf-8",
            )

            with patch.object(analyzer, "ENV_FILE", env_file):
                with patch.dict(
                    os.environ,
                    {
                        "GEMINI_API_KEY": "existing-key",
                        "CLEARTERMS_MODEL": "existing-model",
                    },
                ):
                    self.environment_loader.stop()
                    try:
                        analyzer._load_environment()
                        self.assertEqual(
                            os.environ["GEMINI_API_KEY"],
                            "existing-key",
                        )
                        self.assertEqual(
                            os.environ["CLEARTERMS_MODEL"],
                            "existing-model",
                        )
                    finally:
                        self.environment_loader.start()


if __name__ == "__main__":
    unittest.main()
