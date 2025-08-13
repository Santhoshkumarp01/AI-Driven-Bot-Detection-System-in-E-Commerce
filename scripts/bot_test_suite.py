import time
import statistics
from basic_bot_simulator import BasicBotSimulator
from advanced_bot_simulator import AdvancedBotSimulator
import concurrent.futures
import threading

class BotTestSuite:
    def __init__(self, target_url="http://localhost:8000"):
        self.target_url = target_url
        self.results = []
        self.lock = threading.Lock()
    
    def run_basic_bot_tests(self, count=5):
        """Run multiple basic bot tests"""
        print(f"🤖 Running {count} basic bot tests...")
        
        for i in range(count):
            print(f"\n--- Basic Bot Test {i+1}/{count} ---")
            bot = BasicBotSimulator(self.target_url)
            result = bot.simulate_bot_shopping()
            
            if result:
                with self.lock:
                    self.results.append(('basic', result))
            
            time.sleep(3)  # Delay between tests
    
    def run_advanced_bot_tests(self, count=3):
        """Run multiple advanced bot tests"""
        print(f"\n🧠 Running {count} advanced bot tests...")
        
        for i in range(count):
            print(f"\n--- Advanced Bot Test {i+1}/{count} ---")
            bot = AdvancedBotSimulator(self.target_url)
            result = bot.simulate_human_shopping_pattern()
            
            if result:
                with self.lock:
                    self.results.append(('advanced', result))
            
            time.sleep(4)  # Longer delay for advanced tests
    
    def run_concurrent_tests(self, basic_count=3, advanced_count=2):
        """Run tests concurrently to simulate real attack patterns"""
        print(f"\n⚡ Running concurrent bot tests...")
        
        def run_basic():
            self.run_basic_bot_tests(basic_count)
        
        def run_advanced():
            self.run_advanced_bot_tests(advanced_count)
        
        # Run both types concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_basic = executor.submit(run_basic)
            future_advanced = executor.submit(run_advanced)
            
            # Wait for both to complete
            concurrent.futures.wait([future_basic, future_advanced])
    
    def analyze_results(self):
        """Analyze TouchGuard detection performance"""
        if not self.results:
            print("❌ No test results to analyze")
            return
        
        print("\n" + "="*60)
        print("🎯 TOUCHGUARD BOT DETECTION ANALYSIS")
        print("="*60)
        
        basic_results = [r[1] for r in self.results if r[0] == 'basic']
        advanced_results = [r[1] for r in self.results if r[0] == 'advanced']
        
        # Basic bot analysis
        if basic_results:
            basic_detected = sum(1 for r in basic_results if r.get('is_bot', False))
            basic_accuracy = (basic_detected / len(basic_results)) * 100
            basic_confidences = [r.get('confidence', 0) for r in basic_results if r.get('is_bot')]
            
            print(f"\n📊 BASIC BOT RESULTS:")
            print(f"   Total Tests: {len(basic_results)}")
            print(f"   Detected as Bot: {basic_detected}")
            print(f"   Detection Rate: {basic_accuracy:.1f}%")
            if basic_confidences:
                print(f"   Avg Confidence: {statistics.mean(basic_confidences):.1f}%")
                print(f"   Max Confidence: {max(basic_confidences):.1f}%")
                print(f"   Min Confidence: {min(basic_confidences):.1f}%")
        
        # Advanced bot analysis
        if advanced_results:
            advanced_detected = sum(1 for r in advanced_results if r.get('is_bot', False))
            advanced_accuracy = (advanced_detected / len(advanced_results)) * 100
            advanced_confidences = [r.get('confidence', 0) for r in advanced_results if r.get('is_bot')]
            
            print(f"\n🧠 ADVANCED BOT RESULTS:")
            print(f"   Total Tests: {len(advanced_results)}")
            print(f"   Detected as Bot: {advanced_detected}")
            print(f"   Detection Rate: {advanced_accuracy:.1f}%")
            if advanced_confidences:
                print(f"   Avg Confidence: {statistics.mean(advanced_confidences):.1f}%")
                print(f"   Max Confidence: {max(advanced_confidences):.1f}%")
                print(f"   Min Confidence: {min(advanced_confidences):.1f}%")
        
        # Overall performance
        total_tests = len(self.results)
        total_detected = sum(1 for r in self.results if r[1].get('is_bot', False))
        overall_accuracy = (total_detected / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL TOUCHGUARD PERFORMANCE:")
        print(f"   Total Bot Tests: {total_tests}")
        print(f"   Total Detected: {total_detected}")
        print(f"   Overall Accuracy: {overall_accuracy:.1f}%")
        
        # Detailed session info
        print(f"\n📋 SESSION DETAILS:")
        for i, (bot_type, result) in enumerate(self.results):
            session_id = result.get('session_id', 'Unknown')[:20]
            classification = result.get('classification', 'Unknown')
            confidence = result.get('confidence', 0)
            movement_count = result.get('movement_count', 0)
            
            print(f"   {i+1:2d}. {bot_type:8s} | {session_id:20s} | {classification:6s} | {confidence:5.1f}% | {movement_count:3d} moves")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if basic_accuracy >= 90:
            print("   ✅ Excellent basic bot detection - Linear movements caught effectively")
        elif basic_accuracy >= 75:
            print("   ⚠️  Good basic bot detection - Consider tuning velocity features")
        else:
            print("   ❌ Poor basic bot detection - Check feature extraction")
            
        if advanced_accuracy >= 70:
            print("   ✅ Excellent advanced bot detection - Handles sophisticated patterns")
        elif advanced_accuracy >= 50:
            print("   ⚠️  Moderate advanced bot detection - Some sophisticated bots bypass")
        else:
            print("   ❌ Advanced bots easily bypass - Need more training data")
        
        print(f"\n🚀 TOUCHGUARD STATUS:")
        if overall_accuracy >= 85:
            print("   ✅ PRODUCTION READY - Excellent bot detection performance")
        elif overall_accuracy >= 70:
            print("   ⚠️  NEEDS IMPROVEMENT - Acceptable but monitor closely")
        else:
            print("   ❌ NOT READY - Requires significant improvement")

if __name__ == "__main__":
    print("🚀 TouchGuard Bot Testing Suite")
    print("="*50)
    
    suite = BotTestSuite()
    
    # Choose test mode
    test_mode = input("Select test mode:\n1. Sequential tests\n2. Concurrent tests\n3. Basic only\n4. Advanced only\nEnter choice (1-4): ")
    
    if test_mode == "1":
        suite.run_basic_bot_tests(count=3)
        suite.run_advanced_bot_tests(count=2)
    elif test_mode == "2":
        suite.run_concurrent_tests(basic_count=3, advanced_count=2)
    elif test_mode == "3":
        suite.run_basic_bot_tests(count=5)
    elif test_mode == "4":
        suite.run_advanced_bot_tests(count=3)
    else:
        print("Invalid choice, running sequential tests...")
        suite.run_basic_bot_tests(count=3)
        suite.run_advanced_bot_tests(count=2)
    
    # Analyze results
    suite.analyze_results()
    
    print(f"\n🏁 Testing Complete! Check your admin dashboard at http://localhost:8000/admin")
