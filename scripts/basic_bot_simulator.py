import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import numpy as np

class BasicBotSimulator:
    def __init__(self, target_url="http://localhost:8000"):
        self.target_url = target_url
        self.driver = None
        self.session_id = f"bot_session_{int(time.time())}"
        
    def setup_browser(self):
        """Initialize browser with bot-like settings"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--headless")  # Run in background
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def generate_linear_movements(self, start_x, start_y, end_x, end_y, steps=20):
        """Generate straight-line bot movements"""
        movements = []
        current_time = int(time.time() * 1000)
        
        for i in range(steps):
            progress = i / (steps - 1) if steps > 1 else 1
            x = int(start_x + (end_x - start_x) * progress)
            y = int(start_y + (end_y - start_y) * progress)
            
            movements.append({
                'x': x,
                'y': y,
                'timestamp': current_time + i * 50  # Fixed 50ms intervals
            })
            
        return movements
    
    def simulate_bot_shopping(self):
        """Simulate bot shopping behavior"""
        print(f"🤖 Starting bot simulation with session: {self.session_id}")
        
        self.setup_browser()
        self.driver.get(self.target_url)
        time.sleep(2)
        
        movements = []
        clicks = 0
        
        try:
            # 1. Get viewport size
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # 2. Generate mechanical movements to product area
            product_moves = self.generate_linear_movements(100, 100, 400, 300)
            movements.extend(product_moves)
            
            # 3. Click first add-to-cart button
            try:
                add_btn = self.driver.find_element(By.CLASS_NAME, "add-to-cart-btn")
                add_btn.click()
                clicks += 1
                time.sleep(0.1)  # Minimal delay
            except:
                print("⚠️ Add to cart button not found, simulating click anyway")
                clicks += 1
            
            # 4. Direct movement to cart area
            cart_moves = self.generate_linear_movements(400, 300, 800, 100)
            movements.extend(cart_moves)
            
            # 5. Click cart
            try:
                cart_btn = self.driver.find_element(By.ID, "cart-toggle")
                cart_btn.click()
                clicks += 1
            except:
                print("⚠️ Cart button not found, simulating click anyway")
                clicks += 1
            
            # 6. Send data to TouchGuard for detection
            result = self.send_detection_request(movements, clicks)
            return result
            
        except Exception as e:
            print(f"Bot simulation error: {e}")
            # Still send some movements for testing
            dummy_moves = self.generate_linear_movements(100, 100, 500, 400, 30)
            return self.send_detection_request(dummy_moves, 2)
        finally:
            self.driver.quit()
    
    def send_detection_request(self, movements, clicks):
        """Send bot data to TouchGuard API with proper formatting"""
        data = {
            "session_id": self.session_id,
            "movements": movements,
            "clicks": clicks,
            "timestamp": datetime.now().isoformat()  # ✅ Fixed timestamp format
        }
        
        try:
            response = requests.post(
                f"{self.target_url}/api/detect", 
                json=data, 
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"🎯 Detection Result: {result['classification']} ({result['confidence']}%)")
                return result
            else:
                print(f"❌ Detection failed: {response.status_code}")
                print(f"Error details: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

if __name__ == "__main__":
    bot = BasicBotSimulator()
    bot.simulate_bot_shopping()
