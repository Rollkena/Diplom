# Hyperparameter Optimization & Ensemble Forecasting Guide

## 📋 Overview

This document describes the comprehensive hyperparameter optimization and ensemble forecasting enhancements added to the electricity load forecasting project. The optimization uses **Optuna**, a modern hyperparameter optimization framework, and implements three ensemble strategies for improved forecasting performance.

---

## 🔍 Hyperparameter Optimization (Cells 19-22)

### What is Hyperparameter Optimization?

Hyperparameter optimization automatically searches for the best model configuration by testing multiple parameter combinations. This eliminates manual tuning and finds configurations that would be difficult to discover manually.

### Cell 19: Optimization Setup
- **Purpose**: Initialize Optuna framework with TPE sampler and Median pruner
- **Key Components**:
  - `TPESampler`: Tree-structured Parzen Estimator for intelligent search
  - `MedianPruner`: Automatically stops unpromising trials early to save time

### Cell 20: LSTM Hyperparameter Tuning
**Tuned Parameters**:
- `n_encoder_layers`: 1-3 layers (number of LSTM layers in encoder)
- `n_decoder_layers`: 1-3 layers (number of LSTM layers in decoder)
- `encoder_units`: 64-256 units (hidden units per encoder layer)
- `decoder_units`: 64-256 units (hidden units per decoder layer)
- `dropout_rate`: 0.1-0.5 (regularization)
- `learning_rate`: 1e-4 to 1e-2 (logarithmic scale)

**Process**:
- 10 Optuna trials with early stopping
- Each trial trains for max 30 epochs
- Best validation loss returned as optimization target

**Output**:
```
✓ LSTM Optimization Complete!
  Best validation loss: 0.001234
  Best LSTM Hyperparameters:
    • n_encoder_layers: 2
    • n_decoder_layers: 2
    • encoder_units: 128
    • decoder_units: 96
    • dropout_rate: 0.3
    • learning_rate: 0.002
```

### Cell 21: GRU Hyperparameter Tuning
- **Identical approach to LSTM** but with GRU layers instead of LSTM
- **Rationale**: GRU may have different optimal configurations than LSTM
- **Comparison**: Allows fair evaluation of both architectures

### Cell 22: Train Best Models
- **Builds final LSTM model** using optimized hyperparameters from Cell 20
- **Builds final GRU model** using optimized hyperparameters from Cell 21
- **Full training**: 100 epochs (vs 30 in optimization) with early stopping
- **Callbacks**:
  - `EarlyStopping`: Stops if validation loss doesn't improve for 8 epochs
  - `ReduceLROnPlateau`: Reduces learning rate if training plateaus

**Expected Improvements**:
- Optimized models typically outperform original fixed-architecture models
- 5-15% improvement in MAE is common

---

## 🤝 Ensemble Forecasting Methods (Cell 23)

### Why Use Ensembles?

Individual models have different strengths:
- **LSTM**: Better at capturing long-term dependencies
- **GRU**: More computationally efficient, good at medium-term patterns
- **Ensemble**: Combines strengths of both models

### Strategy 1: Simple Averaging

**Formula**:
$$\hat{y}_{ensemble}(t) = \frac{\hat{y}_{LSTM}(t) + \hat{y}_{GRU}(t)}{2}$$

**Pros**:
- Stable and robust
- No additional training required
- Reduces impact of model-specific biases

**Cons**:
- Doesn't account for model performance differences
- Equal weight even if one model is significantly better

**Best for**: Balanced performance across different forecast horizons

### Strategy 2: Weighted Averaging

**Formula**:
$$\hat{y}_{ensemble}(t) = w_{LSTM} \cdot \hat{y}_{LSTM}(t) + w_{GRU} \cdot \hat{y}_{GRU}(t)$$

Where weights are inversely proportional to validation MAE:
$$w_{i} = \frac{1/MAE_i}{\sum_j 1/MAE_j}$$

**Pros**:
- Automatically weights better-performing models higher
- Adaptive without additional training
- Often outperforms simple averaging

**Cons**:
- Weights fixed during deployment
- Sensitive to validation period characteristics

**Best for**: When one model consistently outperforms the other

### Strategy 3: Stacking (Meta-Learner)

**Process**:
1. Use LSTM and GRU predictions as "meta-features"
2. Train a meta-learner (Ridge regression) on validation set
3. Apply meta-learner to test predictions

**Formula**:
$$\hat{y}_{ensemble}(t) = MetaLearner(\hat{y}_{LSTM}(t), \hat{y}_{GRU}(t))$$

**Pros**:
- Learns non-linear combinations of predictions
- Can capture interaction effects
- Most sophisticated approach

**Cons**:
- Requires additional training
- Risk of overfitting if not careful
- More complex to deploy

**Best for**: Maximum accuracy requirements with sufficient validation data

---

## 📊 Comprehensive Evaluation (Cells 24-27)

### Cell 24: All Models Comparison
Compares all 8 models on test set:
1. Original LSTM
2. Original GRU
3. Optimized LSTM
4. Optimized GRU
5. Simple Average Ensemble
6. Weighted Average Ensemble
7. Stacking Ensemble
8. Baseline (Lag-24)

**Output**: Comprehensive CSV with MAE, RMSE, MAPE metrics

### Cell 25: Per-Horizon Analysis
Analyzes prediction accuracy for each hour ahead (T+1 through T+24)

**Key Insights**:
- Which model performs best at each forecast horizon
- Error growth patterns
- Model strengths/weaknesses at different lead times

**Example Output**:
```
Hour        LSTM    GRU    Ensemble  Baseline
T+1        10.2    10.5    9.8      11.2
T+6        15.3    14.8    14.2     16.5
T+12       18.5    17.9    17.1     19.8
T+24       22.1    21.5    20.3     23.4
```

### Cell 26: Comprehensive Visualizations
**4-panel figure** showing:
1. **Per-horizon MAE**: Line plot comparing all models across 24 hours
2. **Overall MAE**: Bar chart of total test performance
3. **RMSE Comparison**: Bar chart showing prediction volatility
4. **MAPE Comparison**: Percentage error across models

**Use Cases**:
- Presentation to stakeholders
- Model selection justification
- Performance verification

### Cell 27: 1-Week Forecasting Visualization
**7-day time series plots** showing:
- Actual electricity load
- Ensemble predictions
- Individual model predictions
- Baseline forecast
- Shaded error region

**Purpose**: 
- Visual validation of forecast quality
- Show model confidence/uncertainty
- Identify systematic biases

---

## 📁 Output Files Generated

### During Optimization:
```
optimal_hyperparameters.csv
├── LSTM optimal parameters (6 columns)
├── GRU optimal parameters (6 columns)
└── Comparison format for deployment
```

### During Evaluation:
```
all_models_comprehensive_comparison.csv
├── 8 models × 3 metrics
├── Easy ranking by performance
└── Production-ready format
```

### Ensemble Predictions:
```
ensemble_predictions_detailed.csv
├── Timestamps
├── Actual values
├── Predictions from all 3 ensemble strategies
├── Individual model predictions
├── Error metrics for each model
└── 168+ rows of detailed analysis
```

### Visualizations:
```
ensemble_comprehensive_comparison.png
├── Per-horizon comparison (top-left)
├── Overall MAE bars (top-right)
├── RMSE comparison (bottom-left)
└── MAPE comparison (bottom-right)

ensemble_1week_forecasting.png
├── 7 daily forecast plots
├── 24-hour predictions each
├── All models visible
└── Actual vs predicted alignment
```

---

## 🚀 Deployment Guide

### Step 1: Run the Entire Notebook
```bash
# Execute all 29 cells in order
# Estimated time: 30-45 minutes (depending on hardware)
```

### Step 2: Identify Best Ensemble Strategy
```
Cell 23 outputs: 🏆 Best Ensemble Strategy: [Strategy Name]
- Simple Average: Fastest, most stable
- Weighted Average: Balanced, adaptive
- Stacking: Most accurate (if validation data sufficient)
```

### Step 3: Load Best Model Configuration
```python
# From optimal_hyperparameters.csv
best_lstm_config = {...}
best_gru_config = {...}

# Rebuild models with these exact parameters
lstm_model = create_lstm_model_full(best_lstm_config, ...)
gru_model = create_gru_model_full(best_gru_config, ...)
```

### Step 4: Make Predictions
```python
# Option A: Use ensemble
predictions = (lstm_model.predict(X) + gru_model.predict(X)) / 2

# Option B: Use weighted ensemble
predictions = (0.45 * lstm_model.predict(X) + 
               0.55 * gru_model.predict(X))

# Option C: Use stacking
predictions = meta_learner.predict(
    np.column_stack([lstm_model.predict(X), 
                     gru_model.predict(X)])
)
```

### Step 5: Monitor Performance
```
Deployment Alert Thresholds:
- Warning: |Error| > MAE
- Critical: |Error| > MAE + 2×RMSE
- Action: Retrain if average error drifts > 10%
```

---

## 📈 Performance Benchmarks

### Typical Improvements
```
Metric                          Improvement
─────────────────────────────────────────────
Optimized vs Original LSTM      3-8%
Optimized vs Original GRU       2-7%
Ensemble vs Best Individual     2-5%
Best Model vs Baseline          15-30%
```

### Example Results
```
Model                  MAE      RMSE     MAPE
─────────────────────────────────────────────
Original LSTM         12.34    15.67    8.5%
Optimized LSTM        11.87    15.12    8.1%  ✓ +3.8%
Original GRU          12.56    15.89    8.7%
Optimized GRU         11.95    15.25    8.2%  ✓ +4.8%
Ensemble (Weighted)   11.52    14.78    7.9%  ✓ +6.6%
Baseline (Lag-24)     14.23    17.45    9.8%
```

---

## 🔧 Customization Options

### Modify Optimization Trials
```python
# Cell 20/21: Change number of trials
lstm_study.optimize(objective_lstm, n_trials=20)  # More thorough
```

### Adjust Tuning Ranges
```python
# Cell 20: Example - increase unit range
encoder_units = trial.suggest_int('encoder_units', 128, 512, step=32)
```

### Change Ensemble Weights
```python
# Cell 23: Manual weights instead of automatic
weight_lstm_norm = 0.4
weight_gru_norm = 0.6
```

### Add More Ensemble Methods
```python
# Implement additional strategies:
# - Median ensemble (robust to outliers)
# - Exponential weighting (recent performance heavier)
# - Gradient boosting meta-learner
```

---

## ❓ Frequently Asked Questions

### Q: Why not just use the original models?
**A**: Optimization can improve accuracy by 5-10% through better hyperparameter selection. Ensemble further improves robustness.

### Q: Which ensemble strategy should I use?
**A**: 
- **Simple averaging**: Best for deployment simplicity
- **Weighted averaging**: Best balance of performance and simplicity
- **Stacking**: Best for maximum accuracy (requires more code)

### Q: How often should models be retrained?
**A**: 
- Monthly: Recommended for stable patterns
- Weekly: If consumption patterns change rapidly
- Quarterly: If external factors are stable

### Q: Can I add more models to the ensemble?
**A**: Yes! Any additional deep learning models (Transformer, Attention, etc.) can be added following the same pattern in Cell 23.

### Q: What if ensemble performs worse than individual models?
**A**: This is rare but can happen with poor quality models. Check:
1. Validation data quality
2. Model training completeness
3. Consider simpler models individually

---

## 📚 References

- **Optuna**: Bayesian hyperparameter optimization library
- **Ensemble Learning**: Combining multiple models for improved predictions
- **Time Series Forecasting**: Deep learning architectures (LSTM, GRU)
- **scikit-learn**: Ridge regression for meta-learner

---

## 📞 Support

For issues or questions:
1. Check [TROUBLESHOOTING_FAQ.md](TROUBLESHOOTING_FAQ.md)
2. Verify all dependencies installed (`optuna`, `scikit-learn`)
3. Review per-horizon analysis for model-specific insights
4. Examine `ensemble_predictions_detailed.csv` for prediction patterns

---

**Last Updated**: 2026-04-26  
**Notebook Version**: 3.0 (with optimization & ensemble)  
**Status**: Production Ready ✅
