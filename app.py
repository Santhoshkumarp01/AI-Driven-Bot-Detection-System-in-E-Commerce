from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pickle
import numpy as np
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Dict, Any, Union
import uvicorn
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TouchGuard Bot Detection", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Database setup
DB_FILE = "touchguard.db"

def init_database():
    """Initialize SQLite database with proper schema"""
    # Delete existing database to start fresh
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        logger.info("🗑️ Existing database deleted")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_type TEXT,
            confidence REAL,
            status TEXT DEFAULT 'active',
            movement_count INTEGER DEFAULT 0,
            last_prediction TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized with clean schema")

# Load the trained model
try:
    with open('models/touchguard_improved_bot_detector.pkl', 'rb') as f:
        model = pickle.load(f)
    logger.info("✅ TouchGuard model loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading model: {e}")
    model = None

class MouseData(BaseModel):
    session_id: str
    movements: List[Dict[str, Any]]
    clicks: int
    timestamp: Union[str, float]

class DetectionEngine:
    def __init__(self):
        self.model = model
    
    def get_real_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for forwarded headers (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host
    
    def parse_mouse_behavior(self, movements):
        """Extract coordinates from movement data"""
        coords = []
        for move in movements:
            if isinstance(move, dict) and 'x' in move and 'y' in move:
                try:
                    coords.append((float(move['x']), float(move['y'])))
                except (ValueError, TypeError):
                    continue
        return coords
    
    def extract_features(self, movements, click_count):
        """Extract 18 behavioral features"""
        if len(movements) < 3:
            return None
        
        x_coords = [m[0] for m in movements]
        y_coords = [m[1] for m in movements]
        
        velocities = []
        accelerations = []
        direction_changes = []
        distances = []
        pauses = []
        
        for i in range(1, len(movements)):
            dx = x_coords[i] - x_coords[i-1]
            dy = y_coords[i] - y_coords[i-1]
            distance = np.sqrt(dx**2 + dy**2)
            distances.append(distance)
            velocity = max(distance, 0.1)
            velocities.append(velocity)
            
            if velocity < 2:
                pauses.append(1)
            
            if i > 1:
                prev_velocity = velocities[-2] if len(velocities) > 1 else velocity
                acceleration = velocity - prev_velocity
                accelerations.append(acceleration)
            
            if i > 1 and distance > 0:
                prev_dx = x_coords[i-1] - x_coords[i-2]
                prev_dy = y_coords[i-1] - y_coords[i-2]
                if prev_dx != 0 or prev_dy != 0:
                    angle_current = np.arctan2(dy, dx)
                    angle_prev = np.arctan2(prev_dy, prev_dx)
                    angle_diff = abs(angle_current - angle_prev)
                    if angle_diff > np.pi:
                        angle_diff = 2*np.pi - angle_diff
                    direction_changes.append(angle_diff)
        
        try:
            features = [
            # --- Velocity-based Features (from the list of speeds between points) ---
            np.mean(velocities) if velocities else 0,                      # 1. Average mouse speed
            np.std(velocities) if len(velocities) > 1 else 0,            # 2. Speed variation (standard deviation)
            np.max(velocities) if velocities else 0,                     # 3. Maximum speed
            np.min(velocities) if velocities else 0,                     # 4. Minimum speed
            np.median(velocities) if velocities else 0,                  # 5. Median speed
            np.var(velocities) if len(velocities) > 1 else 0,           # 17. Variance of speed (another measure of variation)

            # --- Acceleration-based Features (from the change in speed) ---
            np.mean(accelerations) if accelerations else 0,              # 6. Average acceleration
            np.std(accelerations) if len(accelerations) > 1 else 0,      # 7. Acceleration variation (standard deviation)

            # --- Direction-based Features (from the change in angle) ---
            np.mean(direction_changes) if direction_changes else 0,       # 8. Average change in direction (how curvy the path is)
            np.std(direction_changes) if len(direction_changes) > 1 else 0, # 9. Direction change variation (standard deviation)

            # --- Overall Movement Features ---
            len(movements),                                               # 10. Total number of recorded mouse coordinates
            sum(distances) if distances else 0,                           # 11. Total distance traveled by the cursor
            click_count,                                                  # 12. Total number of clicks
            len(pauses),                                                  # 13. Number of pauses (moments of very low speed)
            (max(x_coords) - min(x_coords)) if x_coords else 0,          # 14. The horizontal distance covered (width of movement)
            (max(y_coords) - min(y_coords)) if y_coords else 0,          # 15. The vertical distance covered (height of movement)
            len(movements) / (sum(distances) + 1) if distances else 0,   # 16. Movement efficiency (ratio of points to distance)
            (sum(distances) / len(movements)) if movements and distances else 0 # 18. Average step size between points
        ]
                    
            features = [float(f) if not np.isnan(f) and not np.isinf(f) else 0.0 for f in features]
            
            # Log feature extraction for debugging
            logger.info(f"🧠 Features extracted: velocity_mean={features[0]:.3f}, velocity_std={features[1]:.3f}, movement_count={features[9]}")
            
            return features if len(features) == 18 else None
            
        except Exception as e:
            logger.error(f"❌ Feature extraction error: {e}")
            return None
    
    def predict(self, session_id: str, movements: List[Dict], clicks: int, ip_address: str, user_agent: str):
        """Make bot/human prediction"""
        try:
            if not self.model:
                return {"error": "Model not loaded"}
            
            coords = self.parse_mouse_behavior(movements)
            if not coords or len(coords) < 3:
                return {"error": "Insufficient movement data"}
            
            features = self.extract_features(coords, clicks)
            if not features or len(features) != 18:
                return {"error": "Feature extraction failed"}
            
            prediction = self.model.predict([features])[0]
            probabilities = self.model.predict_proba([features])[0]
            confidence = max(probabilities) * 100
            
            result = {
                "session_id": session_id,
                "is_bot": bool(prediction),
                "confidence": round(confidence, 2),
                "classification": "Bot" if prediction else "Human",
                "timestamp": datetime.now().isoformat(),
                "movement_count": len(movements),
                "features": features
            }
            
            # Save to database
            self.save_prediction(session_id, result, ip_address, user_agent)
            
            # Console logging for verification
            logger.info(f"🔍 DETECTION RESULT: {result['classification']} ({result['confidence']}%)")
            logger.info(f"📍 IP: {ip_address} | Session: {session_id[:16]}... | Movements: {len(movements)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return {"error": f"Prediction failed: {str(e)}"}
    
    def save_prediction(self, session_id: str, result: Dict, ip_address: str, user_agent: str):
        """Save prediction to database"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, created_at, user_type, confidence, movement_count, last_prediction, ip_address, user_agent, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                datetime.now(),
                result['classification'],
                result['confidence'],
                result['movement_count'],
                datetime.now(),
                ip_address,
                user_agent,
                'active'
            ))
            
            conn.commit()
            logger.info(f"✅ Database: Session {session_id[:16]}... saved - {result['classification']} - IP: {ip_address}")
            
        except Exception as e:
            logger.error(f"❌ Database save error: {e}")
        finally:
            conn.close()

# Initialize components
detector = DetectionEngine()

@app.on_event("startup")
async def startup_event():
    init_database()
    logger.info("🚀 TouchGuard Bot Detection System started")

# Routes
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get recent sessions
    cursor.execute('SELECT * FROM sessions ORDER BY last_prediction DESC LIMIT 50')
    sessions = cursor.fetchall()
    
    # Update session status based on last activity
    enhanced_sessions = []
    for session in sessions:
        session_list = list(session)
        if session[6]:  # last_prediction exists
            try:
                last_time = datetime.fromisoformat(session[6].replace('Z', ''))
                time_diff = datetime.now() - last_time
                session_list[4] = "active" if time_diff < timedelta(minutes=2) else "inactive"
            except:
                session_list[4] = "inactive"
        enhanced_sessions.append(session_list)
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM sessions WHERE user_type = "Human"')
    human_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sessions WHERE user_type = "Bot"')
    bot_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sessions')
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    stats = {
        "total_sessions": total_count,
        "human_sessions": human_count,
        "bot_sessions": bot_count,
        "sessions": enhanced_sessions,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "startup_time": "System online",
        "uptime": "Running",
        "last_activity_time": datetime.now().isoformat()
    }
    
    logger.info(f"📊 Admin Dashboard loaded: {human_count} humans, {bot_count} bots, {total_count} total sessions")
    
    return templates.TemplateResponse("admin.html", {"request": request, "stats": stats})

@app.post("/api/detect")
async def detect_bot(data: MouseData, request: Request):
    try:
        # Get real IP address
        client_ip = detector.get_real_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Log the detection request
        logger.info(f"🖱️ MOUSE MOVEMENT DATA RECEIVED:")
        logger.info(f"   📍 IP Address: {client_ip}")
        logger.info(f"   🆔 Session: {data.session_id[:16]}...")
        logger.info(f"   📊 Movements: {len(data.movements)}")
        logger.info(f"   🖱️ Clicks: {data.clicks}")
        logger.info(f"   🖥️ User Agent: {user_agent[:50]}...")
        
        # Log some sample coordinates for verification
        if len(data.movements) >= 5:
            sample_movements = data.movements[-5:]  # Last 5 movements
            logger.info(f"   🎯 Last 5 coordinates: {[(m.get('x', 0), m.get('y', 0)) for m in sample_movements]}")
        
        result = detector.predict(
            data.session_id,
            data.movements,
            data.clicks,
            client_ip,
            user_agent
        )
        
        # Log the prediction result
        if not result.get("error"):
            logger.info(f"🎯 PREDICTION COMPLETE:")
            logger.info(f"   🤖 Classification: {result.get('classification', 'Unknown')}")
            logger.info(f"   📈 Confidence: {result.get('confidence', 0)}%")
            logger.info(f"   ⚡ Is Bot: {result.get('is_bot', False)}")
        else:
            logger.warning(f"⚠️ Prediction error: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Detection endpoint error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
    session = cursor.fetchone()
    
    conn.close()
    
    if session:
        logger.info(f"👀 Session details requested: {session_id[:16]}...")
        return {
            "session": session,
            "status": "success"
        }
    return {"error": "Session not found"}

@app.post("/api/admin/block/{session_id}")
async def block_session(session_id: str):
    """Block a specific session"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE sessions SET status = "blocked" WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()
    
    logger.info(f"🚫 Session blocked: {session_id[:16]}...")
    return {"message": f"Session {session_id[:16]}... blocked successfully"}

@app.delete("/api/admin/delete/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()
    
    logger.info(f"🗑️ Session deleted: {session_id[:16]}...")
    return {"message": f"Session {session_id[:16]}... deleted successfully"}

if __name__ == "__main__":
    print("=" * 60)
    print("🛡️  TOUCHGUARD BOT DETECTION SYSTEM")
    print("=" * 60)
    print("🚀 Starting server...")
    print("📍 Main site: http://localhost:8000")
    print("🔧 Admin dashboard: http://localhost:8000/admin") 
    print("📊 Real-time monitoring active")
    print("🖱️ Mouse movement tracking enabled")
    print("🤖 AI model ready for predictions")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
