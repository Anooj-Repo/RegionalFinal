"""
Unit Test Suite Execution Runner & Result Logger (tests/unit/run_unit_tests.py)
Runs all unit tests, prints detailed outputs, and saves execution report to unit_test_results.json.
"""

import unittest
import sys
import os
import json
from datetime import datetime

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

unit_dir = os.path.dirname(os.path.abspath(__file__))
if unit_dir not in sys.path:
    sys.path.insert(0, unit_dir)

from test_unit_guardrails import TestSecurityGuardrails
from test_unit_apis import TestBackendAPIs

def execute_unit_test_suite():
    print("==========================================================================")
    print("RUNNING STANDALONE UNIT TEST SUITE")
    print("==========================================================================")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityGuardrails))
    suite.addTests(loader.loadTestsFromTestCase(TestBackendAPIs))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    test_report = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests_run": result.testsRun,
        "successful_tests": result.testsRun - len(result.failures) - len(result.errors),
        "failures_count": len(result.failures),
        "errors_count": len(result.errors),
        "passed": result.wasSuccessful()
    }

    report_path = os.path.join(unit_dir, "unit_test_results.json")
    with open(report_path, "w") as f:
        json.dump(test_report, f, indent=2)

    print(f"\n[Unit Test Runner] Saved test execution report to: {report_path}")
    print(f"Overall Result: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
    return result.wasSuccessful()

if __name__ == '__main__':
    success = execute_unit_test_suite()
    sys.exit(0 if success else 1)
