"""Metadata mapping regressions; no network calls or database writes."""
import unittest
from unittest.mock import patch

from case_generator import build_stakeholder_map, sync_protagonist_metadata


class ProtagonistMappingTests(unittest.TestCase):
    def test_existing_draft_retains_reviewed_map(self):
        rows = [{"name": "Local council", "perspective": "Reviewed text"}]
        processed = {"stakeholders": {"stakeholders": rows}}
        self.assertTrue(sync_protagonist_metadata(
            processed, {"protagonist": " Asha Rao, District Collector "}
        ))
        self.assertEqual(
            processed["stakeholders"]["primary_protagonist"],
            "Asha Rao, District Collector",
        )
        self.assertIs(processed["stakeholders"]["stakeholders"], rows)
        self.assertFalse(sync_protagonist_metadata(
            processed, {"protagonist": "Asha Rao, District Collector"}
        ))

    def test_metadata_edit_and_clear_replace_cached_identity(self):
        processed = {}
        for value in ("First author-supplied identity", "Corrected identity", ""):
            sync_protagonist_metadata(processed, {"protagonist": value})
            self.assertEqual(
                processed["stakeholders"]["primary_protagonist"], value
            )

    @patch("case_generator._call_json", return_value={"stakeholders": []})
    def test_ai_omission_does_not_lose_author_identity(self, call):
        result = build_stakeholder_map(
            [{"name": "Report", "text": "No named people."}],
            {"protagonist": "Asha Rao, District Collector"},
        )
        self.assertEqual(result["primary_protagonist"], "Asha Rao, District Collector")
        self.assertIn("even when the sources", call.call_args.args[0])

    def test_processing_error_preserved(self):
        processed = {"stakeholders": {"error": "API unavailable"}}
        sync_protagonist_metadata(processed, {"protagonist": "Asha Rao"})
        self.assertEqual(processed["stakeholders"]["error"], "API unavailable")
        self.assertEqual(processed["stakeholders"]["primary_protagonist"], "Asha Rao")


if __name__ == "__main__":
    unittest.main()