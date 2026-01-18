# 🛡️ TouchGuard - AI-Driven Malicious Bot Detection System



TouchGuard is an AI-powered system designed to detect **malicious and automated bots** in web applications by analyzing **mouse movement behavior**. It distinguishes human users from bots using machine learning and fine-grained behavioral analytics.

## 🚀 Features

- ✅ Behavioral bot detection using mouse movement data
- 🤖 Detects moderate and advanced bots
- ⚡ FastAPI backend with admin dashboard
- 🎯 High accuracy with strong generalization (no overfitting)
- 🚄 Real-time predictions with very low latency (~2.16 ms)

## 📋 Table of Contents

- [System Overview](#-system-overview)
- [Methodology](#-methodology)
- [Dataset Summary](#-dataset-summary)
- [Model Performance](#-model-performance)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Future Enhancements](#-future-enhancements)

## 🧠 System Overview

The system analyzes cursor movement sessions and extracts behavioral patterns such as:
- Speed and acceleration
- Movement efficiency
- Direction changes
- Cursor range and distance

These patterns are used to train a machine learning model that classifies traffic as **Human** or **Bot** with a confidence score.

## 🧪 Methodology

### 1. Data Collection

Mouse movement sessions collected from:
- Human users
- Moderate bots
- Advanced bots

Each session represents a complete interaction flow.

### 2. Feature Engineering

Each session is converted into **18 numerical features**, including:

| Feature Category | Examples |
|-----------------|----------|
| Velocity Statistics | `velocity_mean`, `velocity_std`, `velocity_variance` |
| Acceleration Statistics | `acceleration_mean`, `acceleration_std` |
| Movement Patterns | `x_range`, `total_distance`, `avg_step_size` |
| Efficiency Metrics | `movement_efficiency`, `direction_consistency` |

### 3. Model Training

- **Algorithm:** Random Forest (Regularized)
- **Cross-validation:** K-Fold to avoid overfitting
- **Dataset:** Balanced split between humans and bots

### 4. Prediction Flow

```
Session Data → Feature Extraction → Model Prediction → Classification (Human/Bot) + Confidence Score
```

## 📊 Dataset Summary

| Metric | Value |
|--------|-------|
| **Total Samples** | 200 |
| **Human Samples** | 133 |
| **Bot Samples** | 67 |
| **Features per Sample** | 18 |

### Data Split

**Training Set (150 samples)**
- Humans: 100
- Bots: 50

**Testing Set (50 samples)**
- Humans: 33
- Bots: 17

## 📈 Model Performance

### Accuracy Metrics

| Metric | Score |
|--------|-------|
| **Training Accuracy** | 95.33% |
| **Test Accuracy** | 92.00% |
| **Accuracy Gap** | 3.33% ✅ |
| **Mean CV Accuracy** | 92.0% ± 6.8% |
| **Out-of-Bag Score** | 0.927 |

✅ **Good generalization - no overfitting detected**

### Test Results

#### Confusion Matrix

```
              Predicted
              Human  Bot
Actual Human    30    3
       Bot       1   16
```

- **True Humans:** 30
- **False Bots (FP):** 3
- **False Humans (FN):** 1
- **True Bots:** 16

#### Classification Report

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| **Human** | 0.97 | 0.91 | 0.94 | 33 |
| **Bot** | 0.84 | 0.94 | 0.89 | 17 |
| **Accuracy** | | | **0.92** | 50 |

### Feature Importance (Top 10)

1. `velocity_std` - Standard deviation of velocity
2. `velocity_variance` - Variance in cursor speed
3. `x_range` - Horizontal movement range
4. `total_distance` - Total path traveled
5. `avg_step_size` - Average distance per movement
6. `velocity_min` - Minimum velocity
7. `acceleration_std` - Acceleration variation
8. `movement_efficiency` - Path efficiency ratio
9. `velocity_max` - Maximum velocity
10. `direction_mean` - Average movement direction

## ⚡ Performance & Speed

| Metric | Value |
|--------|-------|
| **Average Prediction Time** | ~2.16 ms |
| **Predictions per Second** | ~462 |
| **Robustness (with noise)** | 60% consistency |

✅ **Suitable for real-time deployment**

## 🔧 Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/touchguard.git
cd touchguard

# Install dependencies
pip install -r requirements.txt
```

### Requirements

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
pydantic>=2.0.0
```

## 🚀 Usage

### Start the Application

```bash
# Development mode
fastapi dev app.py

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Access Points

- **Main Site:** http://localhost:8000
- **Admin Dashboard:** http://localhost:8000/admin


### Quick Test

```python
import requests

# Sample mouse movement data
session_data = {
    "movements": [
        {"x": 100, "y": 150, "timestamp": 1000},
        {"x": 120, "y": 160, "timestamp": 1050},
        # ... more movements
    ]
}

# Make prediction
response = requests.post(
    "http://localhost:8000/api/predict",
    json=session_data
)

print(response.json())
# Output: {"prediction": "Human", "confidence": 0.94}
```

## 📚 API Documentation

### Prediction Endpoint

**POST** `/api/predict`

**Request Body:**
```json
{
  "movements": [
    {"x": 100, "y": 150, "timestamp": 1000},
    {"x": 120, "y": 160, "timestamp": 1050}
  ]
}
```

**Response:**
```json
{
  "prediction": "Human",
  "confidence": 0.94,
  "session_id": "abc123",
  "timestamp": "2024-01-18T10:30:00Z"
}
```

For full API documentation, visit `/docs` after starting the server.

## 💾 Model Artifact

The trained model is saved as:
```
models/touchguard_improved_bot_detector.pkl
```

## 🔮 Future Enhancements

- [ ] Expand dataset with real-world traffic
- [ ] Implement sequence-based deep learning models (LSTM/Transformer)
- [ ] Browser fingerprint integration
- [ ] Cloud deployment with auto-scaling
- [ ] Real-time dashboard with analytics
- [ ] Multi-session user profiling
- [ ] A/B testing framework

## 📊 Project Structure

```
touchguard/
├── app.py                 # FastAPI application
├── models/                # Trained model artifacts
├── src/
│   ├── feature_engineering/
│   ├── model/
│   └── utils/
├── static/                # Frontend assets
├── templates/             # HTML templates
├── tests/                 # Unit tests
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🏁 Conclusion

TouchGuard demonstrates that mouse movement behavior can effectively distinguish humans from bots with:
- **92% accuracy**
- **2.16 ms prediction time**
- **Strong generalization**

Making it suitable for production-grade web security systems.

## 📧 Contact

For questions or support, please open an issue or contact [santhoshpalanisamy292@gmail.com](mailto:santhoshpalanisamy292@gmail.com)

---

**Built with ❤️ using FastAPI and scikit-learn**
