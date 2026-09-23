import json
import unittest
from pathlib import Path
from simulator import run_simulation


class TestMysteryDeliverySystem(unittest.TestCase):

    def test_base_case(self):
        with open("base_case.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        report = run_simulation(data)
        total_delivered = sum(
            v["packages_delivered"] for k, v in report.items() if k != "best_agent"
        )
        self.assertEqual(total_delivered, 5)

    def test_all_cases(self):
        for i in range(1, 11):
            filename = f"test_case_{i}.json"
            path = Path(filename)
            if not path.exists():
                continue
            with self.subTest(file=filename):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                report = run_simulation(data)
                total_delivered = sum(
                    v["packages_delivered"] for k, v in report.items() if k != "best_agent"
                )
                self.assertEqual(total_delivered, len(data["packages"]))
                self.assertIsNotNone(report["best_agent"])


if __name__ == "__main__":
    unittest.main()
