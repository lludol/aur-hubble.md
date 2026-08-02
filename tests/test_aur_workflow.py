"""Regression checks for transient AUR outages in the update workflow."""

from pathlib import Path
import re
import unittest


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "aur.yml"


def step_body(workflow: str, name: str) -> str:
    match = re.search(
        rf"^\s*- name: {re.escape(name)}\n(?P<body>.*?)(?=^\s*- name:|\Z)",
        workflow,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"Workflow step not found: {name}")
    return match.group(0)


class AURAvailabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text()

    def test_aur_maintenance_is_reported_without_failing_the_update(self) -> None:
        """A temporary AUR outage must be retried later, not fail the daily update."""
        for package in ("hubble.md", "hubble.md-bin"):
            with self.subTest(package=package):
                step = step_body(self.workflow, f"Push to AUR ({package})")
                clone = re.escape(
                    f"if ! git clone --depth 1 ssh://aur@aur.archlinux.org/{package}.git"
                )
                self.assertRegex(
                    step,
                    rf"{clone}.*?then\s+echo \"::warning::AUR is unavailable; will retry on the next run\.\"\s+exit 0\s+fi",
                )


if __name__ == "__main__":
    unittest.main()
