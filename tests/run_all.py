import subprocess
import sys


TESTS = [
    "tests.test_battery_model",
    "tests.test_charging_battery",
    "tests.test_current_limits",
    "tests.test_idle_battery",
    "tests.test_integrated_battery",
    "tests.test_battery_aging_integration",
    "tests.test_resistance_model",
    "tests.test_thermal_model",
    "tests.test_protection_model",
]


print("=" * 60)
print("           BATTERYTWIN CORE TEST SUITE")
print("=" * 60)

passed = 0
failed = 0

for test in TESTS:

    print()
    print("-" * 60)
    print(f"RUNNING: {test}")
    print("-" * 60)

    result = subprocess.run(
        [sys.executable, "-m", test]
    )

    if result.returncode == 0:
        print(f"PASS: {test}")
        passed += 1
    else:
        print(f"FAIL: {test}")
        failed += 1


print()
print("=" * 60)
print("                 TEST SUMMARY")
print("=" * 60)

print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total : {len(TESTS)}")

print("=" * 60)

if failed == 0:
    print("ALL BATTERYTWIN CORE TESTS PASSED")
    print("=" * 60)
    sys.exit(0)

else:
    print("BATTERYTWIN CORE TEST SUITE FAILED")
    print("=" * 60)
    sys.exit(1)
