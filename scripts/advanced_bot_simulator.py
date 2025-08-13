import time
import requests
import json
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import random
import math

class AdvancedBotSimulator:
    def __init__(self, target_url="http://localhost:8000"):
        self.target_url = target_url
        self.driver = None
        self.session_id = f"advanced_bot_{int(time.time())}"
        
    def setup_browser(self):
        """Initialize browser with advanced anti-detection"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        
        # Advanced anti-detection scripts
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
    
    def generate_bezier_curve(self, start_x, start_y, end_x, end_y, steps=50):
        """Generate curved, human-like movements using Bézier curves"""
        movements = []
        current_time = int(time.time() * 1000)
        
        # Add control points for natural curve
        mid_x = (start_x + end_x) / 2 + random.randint(-100, 100)
        mid_y = (start_y + end_y) / 2 + random.randint(-50, 50)
        
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 1
            
            # Quadratic Bézier curve
            x = (1-t)**2 * start_x + 2*(1-t)*t * mid_x + t**2 * end_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * mid_y + t**2 * end_y
            
            # Add subtle random noise (human imperfection)
            x += random.uniform(-3, 3)
            y += random.uniform(-3, 3)
            
            # Variable timing (human-like acceleration/deceleration)
            base_delay = random.uniform(15, 35)  # Variable timing
            timestamp_offset = int(base_delay * i)
            
            movements.append({
                'x': int(max(0, min(x, 1920))),  # Keep within screen bounds
                'y': int(max(0, min(y, 1080))),
                'timestamp': current_time + timestamp_offset
            })
            
        return movements
    
    def add_human_like_pauses(self, movements):
        """Add realistic pauses and micro-movements"""
        enhanced_movements = []
        
        for i, move in enumerate(movements):
            enhanced_movements.append(move)
            
            # Random pauses (thinking time)
            if random.random() < 0.08:  # 8% chance of pause
                pause_duration = random.uniform(200, 800)  # 200-800ms pause
                pause_move = move.copy()
                pause_move['timestamp'] += int(pause_duration)
                enhanced_movements.append(pause_move)
            
            # Micro-movements (small adjustments)
            if random.random() < 0.03:  # 3% chance of micro-movement
                micro_x = move['x'] + random.randint(-5, 5)
                micro_y = move['y'] + random.randint(-5, 5)
                micro_move = {
                    'x': micro_x,
                    'y': micro_y,
                    'timestamp': move['timestamp'] + random.randint(20, 100)
                }
                enhanced_movements.append(micro_move)
                
        return enhanced_movements
    
    def simulate_human_shopping_pattern(self):
        """Simulate more human-like shopping behavior"""
        print(f"🧠 Starting advanced bot simulation: {self.session_id}")
        
        self.setup_browser()
        self.driver.get(self.target_url)
        time.sleep(random.uniform(2, 5))  # Variable loading time
        
        movements = []
        clicks = 0
        
        try:
            # 1. Explore the page (human browsing behavior)
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Initial exploration movements
            exploration_moves = self.generate_bezier_curve(
                random.randint(50, 200), random.randint(50, 200),
                random.randint(300, 600), random.randint(200, 400)
            )
            movements.extend(exploration_moves)
            
            # 2. Browse products with realistic patterns
            for product_num in range(random.randint(2, 4)):  # Look at 2-4 products
                # Move to product area
                product_x = random.randint(200, 800)
                product_y = random.randint(300, 600)
                
                if movements:
                    last_move = movements[-1]
                    product_moves = self.generate_bezier_curve(
                        last_move['x'], last_move['y'],
                        product_x, product_y
                    )
                else:
                    product_moves = self.generate_bezier_curve(
                        200, 200, product_x, product_y
                    )
                
                movements.extend(product_moves)
                
                # Simulate reading/thinking time
                time.sleep(random.uniform(1, 3))
                
                # Maybe click on a product (not always)
                if product_num >= 1:  # More likely to click later products
                    clicks += 1
                    # Add click timestamp
                    if movements:
                        click_move = movements[-1].copy()
                        click_move['timestamp'] += random.randint(100, 500)
                        click_move['type'] = 'click'
                        movements.append(click_move)
            
            # 3. Enhanced movements with human-like patterns
            movements = self.add_human_like_pauses(movements)
            
            # 4. Send detection request
            result = self.send_detection_request(movements, clicks)
            return result
            
        except Exception as e:
            print(f"Advanced bot error: {e}")
            # Generate fallback movements
            fallback_moves = self.generate_bezier_curve(100, 100, 600, 400, 60)
            return self.send_detection_request(fallback_moves, random.randint(1, 3))
        finally:
            self.driver.quit()
    
    def send_detection_request(self, movements, clicks):
        """Send advanced bot data to TouchGuard"""
        data = {
            "session_id": self.session_id,
            "movements": movements,
            "clicks": clicks,
            "timestamp": datetime.now().isoformat()
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
                print(f"🎯 Advanced Detection: {result['classification']} ({result['confidence']}%)")
                return result
            else:
                print(f"❌ Detection request failed: {response.status_code}")
                print(f"Error details: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

if __name__ == "__main__":
    advanced_bot = AdvancedBotSimulator()
    advanced_bot.simulate_human_shopping_pattern()
