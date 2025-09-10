# test_api.py - ML Parser Testing Utilities
import requests
import json
import time
from typing import List, Dict


class MLParserTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    def test_connection(self) -> bool:
        """Test if API is reachable"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_test_commands(self) -> List[str]:
        """Get available test commands from API"""
        try:
            response = requests.get(f"{self.base_url}/test-commands")
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("commands", [])
        except Exception as e:
            print(f"❌ Failed to get test commands: {e}")
        return []

    def test_single_command(self, command: str, test_mode: bool = True) -> Dict:
        """Test a single command"""
        endpoint = "/test-parse" if test_mode else "/parse"

        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json={"text": command, "test_mode": test_mode},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def run_test_suite(self) -> Dict:
        """Run comprehensive test suite"""
        print("🧪 Running ML Parser Test Suite...")
        print("=" * 50)

        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "results": []
        }

        # Test connection
        if not self.test_connection():
            print("❌ Cannot connect to ML Parser API")
            return results

        print("✅ API connection successful")

        # Get test commands
        test_commands = self.get_test_commands()
        if not test_commands:
            print("⚠️ No test commands available")
            return results

        print(f"📝 Testing {len(test_commands)} commands...")

        # Test each command
        for i, command in enumerate(test_commands, 1):
            print(f"\n🔬 Test {i}/{len(test_commands)}: '{command}'")

            start_time = time.time()
            result = self.test_single_command(command)
            duration = time.time() - start_time

            results["total_tests"] += 1

            if result.get("success", False):
                results["passed"] += 1
                data = result.get("data", {})
                parsed_result = data.get("parsed_result", {})

                print(f"   ✅ Intent: {parsed_result.get('intent', 'unknown')}")
                print(f"   ✅ Action: {parsed_result.get('action', 'unknown')}")
                print(f"   ✅ Confidence: {parsed_result.get('confidence', 0):.2f}")
                print(f"   ⏱️ Duration: {duration:.3f}s")

            else:
                results["failed"] += 1
                error = result.get("error", "Unknown error")
                print(f"   ❌ Failed: {error}")
                results["errors"].append({
                    "command": command,
                    "error": error
                })

            results["results"].append({
                "command": command,
                "success": result.get("success", False),
                "duration": duration,
                "result": result
            })

        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Passed: {results['passed']} ({results['passed'] / results['total_tests'] * 100:.1f}%)")
        print(f"   Failed: {results['failed']} ({results['failed'] / results['total_tests'] * 100:.1f}%)")

        if results["errors"]:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"   - '{error['command']}': {error['error']}")

        return results

    def test_corrupted_commands(self) -> Dict:
        """Test with corrupted speech-to-text input"""
        print("🔀 Testing Corrupted Commands...")

        corrupted_tests = [
            ("set temperature to 24", "sit temprature too 24"),
            ("turn up the volume", "tern up thee valium"),
            ("turn on the lights", "tern on thee lights"),
            ("heat the seats", "heat thee sits"),
            ("play some music", "play sum musik"),
        ]

        results = []

        for original, corrupted in corrupted_tests:
            print(f"\n🔬 Original: '{original}'")
            print(f"🔀 Corrupted: '{corrupted}'")

            # Test both versions
            clean_result = self.test_single_command(original)
            corrupted_result = self.test_single_command(corrupted)

            results.append({
                "original": original,
                "corrupted": corrupted,
                "clean_result": clean_result,
                "corrupted_result": corrupted_result
            })

            # Compare results
            if (clean_result.get("success") and corrupted_result.get("success")):
                clean_action = clean_result.get("data", {}).get("parsed_result", {}).get("action")
                corrupted_action = corrupted_result.get("data", {}).get("parsed_result", {}).get("action")

                if clean_action == corrupted_action:
                    print("   ✅ Both versions produced same action")
                else:
                    print(f"   ⚠️ Different actions: {clean_action} vs {corrupted_action}")
            else:
                print("   ❌ One or both tests failed")

        return results


def main():
    """Run interactive testing"""
    tester = MLParserTester()

    print("🧠 ML Parser API Tester")
    print("=" * 30)

    while True:
        print("\nOptions:")
        print("1. Test connection")
        print("2. Run full test suite")
        print("3. Test single command")
        print("4. Test corrupted commands")
        print("5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            if tester.test_connection():
                print("✅ Connection successful")
            else:
                print("❌ Connection failed")

        elif choice == "2":
            tester.run_test_suite()

        elif choice == "3":
            command = input("Enter command to test: ").strip()
            if command:
                result = tester.test_single_command(command)
                print(json.dumps(result, indent=2))

        elif choice == "4":
            tester.test_corrupted_commands()

        elif choice == "5":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()