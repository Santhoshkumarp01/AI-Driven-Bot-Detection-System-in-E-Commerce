Main Site: http://localhost:8000

Admin Dashboard: http://localhost:8000/admin

fastapi dev app.py







Improved TouchGuard Bot Detection Training
============================================================
Loading ALL Phase 1 mouse movement files...
Loading from: humans_and_moderate_bots
Found 100 session folders in humans_and_moderate_bots
Loaded 50 sessions from humans_and_moderate_bots...
Loaded 100 sessions from humans_and_moderate_bots...
Successfully loaded 100 sessions from humans_and_moderate_bots
Loading from: humans_and_advanced_bots
Found 100 session folders in humans_and_advanced_bots
Loaded 50 sessions from humans_and_advanced_bots...
Loaded 100 sessions from humans_and_advanced_bots...
Successfully loaded 100 sessions from humans_and_advanced_bots

Final Dataset Summary:
Total samples: 200
Humans: 133
Bots: 67
Features per sample: 18

Data Split:
Training: 150 samples (Humans: 100, Bots: 50)
Testing: 50 samples (Humans: 33, Bots: 17)

Training improved Random Forest with regularization...
Performing cross-validation...
Cross-validation scores: [0.93333333 0.9        0.93333333 0.86666667 0.96666667]
Mean CV accuracy: 0.920 (+/- 0.068)
Out-of-bag score: 0.927

============================================================
IMPROVED TOUCHGUARD RESULTS
============================================================
Training Accuracy: 95.33%
Test Accuracy: 92.00%
Accuracy Gap: 3.33% (should be < 10%)
✅ Good generalization - No overfitting detected!

Detailed Test Results:
Training samples: 150
Testing samples: 50

Confusion Matrix:
[[30  3]
 [ 1 16]]
[[True Humans, False Bots],
 [False Humans, True Bots]]

Classification Report:
              precision    recall  f1-score   support

       Human       0.97      0.91      0.94        33
         Bot       0.84      0.94      0.89        17

    accuracy                           0.92        50
   macro avg       0.90      0.93      0.91        50
weighted avg       0.93      0.92      0.92        50


Top 10 Most Important Features:
 1. velocity_std        : 0.2362
 2. velocity_variance   : 0.1653
 3. x_range             : 0.1308
 4. total_distance      : 0.0815
 5. avg_step_size       : 0.0601
 6. velocity_min        : 0.0504
 7. acceleration_std    : 0.0457
 8. movement_efficiency : 0.0438
 9. velocity_max        : 0.0436
10. direction_mean      : 0.0362

Improved model saved: touchguard_improved_bot_detector.pkl

🎉 SUCCESS! Improved TouchGuard model: 92.0% accuracy
🚀 Overfitting issues resolved - Ready for deployment!



TEST


PS C:\Users\Santhosh kumar P\OneDrive\Desktop\Advanced Bot Detection\touchgaurd> python test_touchguard.py
TouchGuard Model Testing Suite - IMPROVED VERSION
============================================================
✅ Improved model loaded successfully

1. Individual Session Testing
----------------------------------------
✅ Successfully tested 18 sessions
✅ g2gh9qmk9krl... -> Predicted: Human, Actual: Human, Confidence: 100.0%
✅ kaodsjbnqm7u... -> Predicted: Human, Actual: Human, Confidence: 100.0%
✅ 1aqgqrcuurlm... -> Predicted: Human, Actual: Human, Confidence: 100.0%
✅ igbeqcjnbst8... -> Predicted: Human, Actual: Human, Confidence:  99.1%
✅ vopb1c4o3o2d... -> Predicted: Human, Actual: Human, Confidence:  99.8%
❌ jfmilo33fin8... -> Predicted: Human, Actual: Bot  , Confidence:  57.0%
✅ 6gftqgk6qqki... -> Predicted: Bot  , Actual: Bot  , Confidence: 100.0%
✅ 84q2klr0foif... -> Predicted: Bot  , Actual: Bot  , Confidence: 100.0%

2. Performance Testing
----------------------------------------
Test Accuracy: 88.89%
Humans in test: 10
Bots in test: 8

Confusion Matrix:
[[10  0]
 [ 2  6]]
[[True Humans, False Bots],
 [False Humans, True Bots]]

Classification Report:
              precision    recall  f1-score   support

       Human       0.83      1.00      0.91        10
         Bot       1.00      0.75      0.86         8

    accuracy                           0.89        18
   macro avg       0.92      0.88      0.88        18
weighted avg       0.91      0.89      0.89        18


3. Cross-Validation Testing
----------------------------------------
✅ Cross-validation on 60 samples
CV scores: [0.83333333 0.91666667 1.         0.91666667 0.91666667]
Mean CV accuracy: 0.917 (+/- 0.105)

4. Feature Importance Analysis
----------------------------------------
Top 8 Most Important Features:
 1. velocity_std        : 0.2362
 2. velocity_variance   : 0.1653
 3. x_range             : 0.1308
 4. total_distance      : 0.0815
 5. avg_step_size       : 0.0601
 6. velocity_min        : 0.0504
 7. acceleration_std    : 0.0457
 8. movement_efficiency : 0.0438

5. Speed Testing
----------------------------------------
✅ Average prediction time: 2.16 ms
✅ Predictions per second: 462

6. Robustness Testing
----------------------------------------
✅ Model stability: 60% consistent predictions with noise
⚠️  Good robustness - Monitor in production

============================================================
🎯 TouchGuard Enhanced Testing Complete!
🚀 Model performance is EXCELLENT - Ready for deployment!
============================================================
