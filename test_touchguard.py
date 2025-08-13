import pickle
import numpy as np
import json
import re
import os
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
import time

def test_improved_touchguard_model():
    """Complete testing suite for the improved TouchGuard model"""
    
    print("TouchGuard Model Testing Suite - IMPROVED VERSION")
    print("="*60)
    
    # Load your improved model
    model_path = "touchguard_improved_bot_detector.pkl"
    base_path = r"C:\Users\Santhosh kumar P\OneDrive\Desktop\Advanced Bot Detection\web_bot_detection_dataset"
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print("✅ Improved model loaded successfully")
    except:
        print("❌ Improved model not found. Using old model as fallback...")
        try:
            with open("touchguard_bot_detector.pkl", 'rb') as f:
                model = pickle.load(f)
        except:
            print("❌ No model found!")
            return
    
    # Known annotations for testing
    test_annotations = {
        "g2gh9qmk9krld14h5uojlg7g10": "human",
        "kaodsjbnqm7umgfvao63d3rihb": "human", 
        "1aqgqrcuurlmvvbbpirvsh7e53": "human",
        "igbeqcjnbst8afmoi4sg6tn669": "human",
        "vopb1c4o3o2dpsov8jinbbou5h": "human",
        "vtcjrbtjq57mnai4banl61pd25": "advanced_bot",
        "071tbv7fsev5d64kb0f9jieor6": "advanced_bot",
        "6ntd0tthl2oaq1l21tho6bflst": "advanced_bot",
        "imgld2d8lq8ugjvfur481ofr2n": "advanced_bot",
        "htodnmm7tjpihgeuqk64c0gjes": "advanced_bot",
        "jfmilo33fin84baeh3k6bcnh3v": "moderate_bot",
        "6gftqgk6qqkipsecbrvk0mtr5h": "moderate_bot",
        "84q2klr0foifmc69684fjvafqa": "moderate_bot"
    }
    
    def parse_mouse_behavior(behavior_string):
        move_pattern = r'\[m\((\d+),(\d+)\)\]'
        moves = re.findall(move_pattern, behavior_string)
        click_pattern = r'\[c\([lr]\)\]'
        clicks = re.findall(click_pattern, behavior_string)
        movements = [(int(x), int(y)) for x, y in moves]
        click_count = len(clicks)
        return movements, click_count
    
    def extract_features_from_movements(movements, click_count):
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
            velocity = distance
            velocities.append(velocity)
            
            if velocity < 2:
                pauses.append(1)
            
            if i > 1:
                acceleration = velocities[-1] - velocities[-2]
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
        
        # Match the 18 features from improved model
        features = [
            np.mean(velocities) if velocities else 0,                    # velocity_mean
            np.std(velocities) if len(velocities) > 1 else 0,           # velocity_std
            np.max(velocities) if velocities else 0,                    # velocity_max
            np.min(velocities) if velocities else 0,                    # velocity_min
            np.median(velocities) if velocities else 0,                 # velocity_median
            np.mean(accelerations) if accelerations else 0,             # acceleration_mean
            np.std(accelerations) if len(accelerations) > 1 else 0,     # acceleration_std
            np.mean(direction_changes) if direction_changes else 0,      # direction_mean
            np.std(direction_changes) if len(direction_changes) > 1 else 0, # direction_std
            len(movements),                                              # total_points
            sum(distances),                                              # total_distance
            click_count,                                                 # click_count
            len(pauses),                                                 # pause_count
            np.max(x_coords) - np.min(x_coords) if x_coords else 0,     # x_range
            np.max(y_coords) - np.min(y_coords) if y_coords else 0,     # y_range
            len(movements) / (sum(distances) + 1),                      # movement_efficiency
            np.var(velocities) if len(velocities) > 1 else 0,          # velocity_variance
            sum(distances) / len(movements) if movements else 0         # avg_step_size
        ]
        
        return features
    
    # Load test data from known annotations
    def load_test_data():
        search_folders = [
            os.path.join(base_path, "phase1", "data", "mouse_movements", "humans_and_moderate_bots"),
            os.path.join(base_path, "phase1", "data", "mouse_movements", "humans_and_advanced_bots")
        ]
        
        features_list = []
        labels_list = []
        session_ids = []
        
        for search_folder in search_folders:
            if not os.path.exists(search_folder):
                continue
                
            for session_id, label in test_annotations.items():
                json_file = os.path.join(search_folder, session_id, "mouse_movements.json")
                
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        behavior = data.get('total_behaviour', '')
                        if behavior:
                            movements, click_count = parse_mouse_behavior(behavior)
                            
                            if movements and len(movements) >= 3:
                                features = extract_features_from_movements(movements, click_count)
                                
                                if features and len(features) == 18:
                                    features_list.append(features)
                                    # Convert to binary labels
                                    labels_list.append(0 if label == "human" else 1)
                                    session_ids.append(session_id)
                    except:
                        continue
        
        return np.array(features_list), np.array(labels_list), session_ids
    
    # Test 1: Individual Session Testing
    print("\n1. Individual Session Testing")
    print("-" * 40)
    
    X_test, y_test, session_ids = load_test_data()
    
    if len(X_test) > 0:
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
        
        print(f"✅ Successfully tested {len(X_test)} sessions")
        
        # Show individual predictions
        for i in range(min(8, len(X_test))):
            pred_label = "Human" if predictions[i] == 0 else "Bot"
            actual_label = "Human" if y_test[i] == 0 else "Bot"
            confidence = max(probabilities[i]) * 100
            status = "✅" if predictions[i] == y_test[i] else "❌"
            
            print(f"{status} {session_ids[i][:12]}... -> Predicted: {pred_label:5s}, "
                  f"Actual: {actual_label:5s}, Confidence: {confidence:5.1f}%")
    else:
        print("❌ No test data loaded")
    
    # Test 2: Performance Metrics
    if len(X_test) > 0:
        print("\n2. Performance Testing")
        print("-" * 40)
        
        test_accuracy = accuracy_score(y_test, predictions)
        print(f"Test Accuracy: {test_accuracy:.2%}")
        print(f"Humans in test: {sum(y_test == 0)}")
        print(f"Bots in test: {sum(y_test == 1)}")
        
        print(f"\nConfusion Matrix:")
        cm = confusion_matrix(y_test, predictions)
        print(cm)
        print("[[True Humans, False Bots],")
        print(" [False Humans, True Bots]]")
        
        print(f"\nClassification Report:")
        print(classification_report(y_test, predictions, target_names=['Human', 'Bot']))
    
    # Test 3: Cross-Validation (load more data if needed)
    print("\n3. Cross-Validation Testing")
    print("-" * 40)
    
    # Load more data for cross-validation
    search_folders = [
        os.path.join(base_path, "phase1", "data", "mouse_movements", "humans_and_moderate_bots"),
        os.path.join(base_path, "phase1", "data", "mouse_movements", "humans_and_advanced_bots")
    ]
    
    all_features = []
    all_labels = []
    
    for search_folder in search_folders:
        if not os.path.exists(search_folder):
            continue
            
        session_folders = [f for f in os.listdir(search_folder) 
                          if os.path.isdir(os.path.join(search_folder, f))][:30]  # Limit for testing
        
        for session_id in session_folders:
            json_file = os.path.join(search_folder, session_id, "mouse_movements.json")
            
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    behavior = data.get('total_behaviour', '')
                    if behavior:
                        movements, click_count = parse_mouse_behavior(behavior)
                        
                        if movements and len(movements) >= 3:
                            features = extract_features_from_movements(movements, click_count)
                            
                            if features and len(features) == 18:
                                all_features.append(features)
                                # Use simple heuristic for labeling
                                if session_id in test_annotations:
                                    all_labels.append(0 if test_annotations[session_id] == "human" else 1)
                                else:
                                    # Simple heuristic based on behavioral patterns
                                    velocity_std = features[1]
                                    pause_count = features[12]
                                    all_labels.append(0 if velocity_std > 10 and pause_count > 2 else 1)
                except:
                    continue
    
    if len(all_features) > 10:
        X_cv = np.array(all_features)
        y_cv = np.array(all_labels)
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_cv, y_cv, cv=cv, scoring='accuracy')
        
        print(f"✅ Cross-validation on {len(X_cv)} samples")
        print(f"CV scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    else:
        print("❌ Not enough data for cross-validation")
    
    # Test 4: Feature Importance Analysis
    print("\n4. Feature Importance Analysis")
    print("-" * 40)
    
    feature_names = [
        'velocity_mean', 'velocity_std', 'velocity_max', 'velocity_min', 'velocity_median',
        'acceleration_mean', 'acceleration_std', 'direction_mean', 'direction_std',
        'total_points', 'total_distance', 'click_count', 'pause_count',
        'x_range', 'y_range', 'movement_efficiency', 'velocity_variance', 'avg_step_size'
    ]
    
    if hasattr(model, 'feature_importances_'):
        importance_pairs = list(zip(feature_names, model.feature_importances_))
        importance_pairs.sort(key=lambda x: x[1], reverse=True)
        
        print("Top 8 Most Important Features:")
        for i, (name, importance) in enumerate(importance_pairs[:8]):
            print(f"{i+1:2d}. {name:20s}: {importance:.4f}")
    
    # Test 5: Speed Testing
    print("\n5. Speed Testing")
    print("-" * 40)
    
    if len(X_test) > 0:
        start_time = time.time()
        for _ in range(100):
            _ = model.predict([X_test[0]])
        end_time = time.time()
        
        avg_prediction_time = (end_time - start_time) / 100 * 1000
        print(f"✅ Average prediction time: {avg_prediction_time:.2f} ms")
        print(f"✅ Predictions per second: {1000/avg_prediction_time:.0f}")
    
    # Test 6: Robustness Testing
    print("\n6. Robustness Testing")
    print("-" * 40)
    
    if len(X_test) > 0:
        # Test with noise injection
        original_pred = model.predict([X_test[0]])[0]
        
        stable_predictions = 0
        for _ in range(10):
            noise_level = 0.05  # 5% noise
            noisy_features = X_test[0] + np.random.normal(0, noise_level * np.std(X_test[0]), len(X_test[0]))
            noisy_pred = model.predict([noisy_features])[0]
            if noisy_pred == original_pred:
                stable_predictions += 1
        
        stability_percent = stable_predictions / 10 * 100
        print(f"✅ Model stability: {stability_percent:.0f}% consistent predictions with noise")
        
        if stability_percent >= 80:
            print("✅ Excellent robustness - Ready for production")
        elif stability_percent >= 60:
            print("⚠️  Good robustness - Monitor in production")
        else:
            print("❌ Poor robustness - Consider model improvement")
    
    print("\n" + "="*60)
    print("🎯 TouchGuard Enhanced Testing Complete!")
    
    if len(X_test) > 0 and test_accuracy > 0.85:
        print("🚀 Model performance is EXCELLENT - Ready for deployment!")
    elif len(X_test) > 0 and test_accuracy > 0.75:
        print("✅ Model performance is GOOD - Consider minor improvements")
    else:
        print("⚠️  Model needs improvement before production deployment")
    
    print("="*60)

if __name__ == "__main__":
    test_improved_touchguard_model()
