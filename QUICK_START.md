# Quick Start & Reference

## 🚀 Quick Start (5 Minutes)

### Step 1: Prepare Your Data
- Excel file with columns: date, hour_range, actual, weather features...
- Hourly frequency, no duplicates
- At least 1 year of data (8,760+ samples)

### Step 2: Update Data Path
```python
# Cell 3, line ~45
df = pd.read_excel("YOUR_FILE_PATH_HERE", header=None)
```

### Step 3: Run All Cells
1. Cell 1: Install `holidays` package
2. Cell 2: Import libraries  
3. Cell 3: Load data & features (~2 min)
4. Cell 4: Train LSTM model (~5-10 min depending on CPU/GPU)
5. Cell 5-18: Evaluation, baseline, comparisons, visualization

### Step 4: Review Results
```
Console Output:
  ✓ Model metrics (MAE, RMSE, MAPE)
  ✓ Baseline comparison
  ✓ Per-horizon error analysis
  ✓ Improvement percentage

Generated Files:
  ✓ 4 PNG visualizations
  ✓ 3 CSV data exports
```

---

## 📋 Notebook Cell Reference

| Cell # | Purpose | Time | Skip? |
|--------|---------|------|-------|
| 1 | Install holidays | 30s | No |
| 2 | Imports | Instant | No |
| 3 | Data loading + features | 2-5 min | No |
| 4 | LSTM training | 5-15 min | No |
| 5 | Evaluation metrics | 1-2 min | No |
| 6-8 | Baseline + comparison | <1 min | Optional |
| 9-10 | Visualizations | 1-2 min | Optional |
| 11-12 | Results table + history | <1 min | Optional |
| 13 | Export predictions | <1 min | Optional |
| 14 | Recommendations | Instant | Optional |
| 15 | GRU model training | 5-15 min | Optional* |
| 16-18 | Model comparison | <1 min | Optional |

*Skip if you want fast results; include for full analysis

---

## 🎯 Key Parameters to Tune

### Most Important (adjust these first)
```python
# Cell 3
LOOKBACK = 168      # Window size (24-336 hours)
HORIZON = 24        # Forecast horizon (fixed at 24)
TRAIN_END = 0.70    # Training split
VAL_END = 0.85      # Validation split

# Cell 4
BATCH_SIZE = 32     # Reduce if OOM: 32→16→8
EPOCHS = 50         # Max epochs (early stop will reduce)
LSTM_UNITS = 128    # Model size: 64, 128, 256
DROPOUT = 0.2       # Regularization: 0.1, 0.2, 0.3
LR = 1e-3           # Learning rate: 1e-4, 1e-3, 1e-2
```

### Less Important (usually don't change)
```python
# Cell 3
TRAIN_END = int(n * 0.70)   # 70% training (standard)
VAL_END = int(n * 0.85)     # 15% validation (standard)
# Test = remaining 15%

# Cell 4
PATIENCE = 8        # Early stop patience (good for most cases)
REDUCE_LR_PATIENCE = 4  # Learning rate reduction
REDUCE_LR_FACTOR = 0.5   # Reduce by 50%
```

---

## 📊 Output Files Guide

### Visualizations
| File | Shows | Use Case |
|------|-------|----------|
| `forecast_comparison.png` | 5 samples: actual vs LSTM vs baseline | Show to stakeholders |
| `error_per_horizon_comparison.png` | Error by forecast hour | Identify weak hours |
| `training_history.png` | Loss/MAE curves | Check for overfitting |
| `models_comparison_bars.png` | Bar chart: LSTM vs GRU vs baseline | Model comparison |

### Data Exports
| File | Content | Rows | Use Case |
|------|---------|------|----------|
| `predictions_detailed.csv` | Timestamp, actual, pred, baseline, errors | ~1K-5K | Detailed analysis |
| `model_results_comparison.csv` | LSTM vs Baseline metrics | 4 | Summary report |
| `models_comprehensive_comparison.csv` | LSTM, GRU, Baseline | 4 | Full comparison |

---

## 🔍 Interpreting Results

### Good Performance
```
Model Metrics:
  MAE: 2.5 MW          ← Low error
  RMSE: 3.2 MW         ← Proportional to MAE
  MAPE: 4.5%           ← Low percentage error
  
Improvement vs Baseline: +12% MAE  ← Positive!
Best hour: T+1h
Worst hour: T+24h       ← Expected pattern
```

### Needs Improvement
```
Model Metrics:
  MAE: 8.5 MW          ← High error
  RMSE: 10.2 MW        ← Much higher than MAE (outliers)
  MAPE: 15.2%          ← High percentage error
  
Improvement vs Baseline: -5% MAE  ← Negative!
Best hour: T+12h        ← Inconsistent
Worst hour: T+6h        ← Check for specific issues
```

### Action Items
**If model underperforms**:
1. [ ] Add more features
2. [ ] Increase model size (LSTM units 128→256)
3. [ ] Collect more data
4. [ ] Check for data leakage
5. [ ] Try different architecture (GRU, Transformer)

---

## 🛠️ Common Adjustments

### If Running Out of Memory
```python
# Option 1: Reduce batch size
batch_size = 32 → 16

# Option 2: Reduce lookback
LOOKBACK = 168 → 84

# Option 3: Reduce model size
LSTM(128) → LSTM(64)

# Option 4: Use GPU
# Install tensorflow-gpu
```

### If Model Not Improving
```python
# Option 1: Add features
weather_features.append('new_feature')

# Option 2: Increase capacity
LSTM(128) → LSTM(256)
Add another LSTM layer

# Option 3: Tune learning
learning_rate = 1e-3 → 1e-2
or 1e-3 → 1e-4

# Option 4: More training
epochs = 50 → 100
patience = 8 → 15
```

### If Overfitting (train loss ↓, val loss ↑)
```python
# Option 1: More dropout
Dropout(0.2) → Dropout(0.4)

# Option 2: Smaller model
LSTM(128) → LSTM(64)

# Option 3: L2 regularization
kernel_regularizer=L2(0.01)

# Option 4: More data or less features
Drop weak features
```

---

## 📈 Performance Benchmarks

### Realistic MAPE by Forecast Horizon

For electricity load forecasting:
```
T+1h   → 2-4% MAPE     (Very accurate)
T+6h   → 4-6% MAPE     (Good)
T+12h  → 5-8% MAPE     (Decent)
T+18h  → 6-10% MAPE    (Acceptable)
T+24h  → 8-12% MAPE    (Challenging)
```

**What This Means**:
- Predictions for tomorrow morning are ~2-4% off
- Predictions for end of day are ~8-12% off
- This is normal and expected

**When to Worry**:
- MAPE > 15% for T+1-6h: Model needs improvement
- MAPE > 20% overall: Likely data issues

---

## 🔐 Data Quality Checklist

Before training, verify:

- [ ] **No missing dates**: Check datetime continuity
- [ ] **No duplicates**: Verify unique timestamps
- [ ] **Realistic values**: Check data ranges make sense
- [ ] **Consistent time zone**: All dates in same timezone
- [ ] **No sudden jumps**: Look for data collection errors
- [ ] **Sufficient history**: At least LOOKBACK + HORIZON rows
- [ ] **Weather data available**: For future periods (forecast)
- [ ] **No negative loads**: Physical impossibility
- [ ] **Reasonable peaks**: Match expected seasonal patterns

---

## 📞 When to Retrain Model

| Scenario | Frequency | Action |
|----------|-----------|--------|
| Regular updates | Monthly | Retrain on last 2 years + new month |
| Seasonal change | Quarterly | Include new season in training |
| Major error | ASAP | Check data quality first |
| Policy change | Immediately | New model accounting for change |
| New equipment | After 1 month | Retrain with new baseline |

---

## 🚨 Warning Signs

Stop and investigate if you see:

1. **Model converges too quickly** (< 5 epochs)
   - Possible data leakage
   - Check scaling and feature engineering

2. **Loss becomes NaN**
   - Learning rate too high: reduce 1e-3 → 1e-4
   - Bad data: check for inf/NaN in input

3. **Validation loss is exactly baseline**
   - Model learned to predict average
   - Not enough capacity or signal

4. **Error same for all forecast hours**
   - Model predicts average regardless of input
   - Data preprocessing issue

5. **Predictions stay constant**
   - Model collapsed to predicting mean
   - Check for NaN in gradients

---

## 📞 Support Workflow

**If something breaks**:

1. **Check error message**
   ```python
   # Look for specific error type and line number
   ```

2. **Search in TROUBLESHOOTING_FAQ.md**
   - Most common issues covered there
   - Includes solutions

3. **Verify data and preprocessing**
   ```python
   print("X_train shape:", X_train.shape)
   print("No NaN:", not np.isnan(X_train).any())
   ```

4. **Run diagnostic cell**
   ```python
   # Add at Cell 3 end
   print("="*50)
   print("DATA DIAGNOSTICS")
   print(f"Total rows: {len(df)}")
   print(f"Features: {len(features)}")
   print(f"Target range: [{y_train_raw.min():.3f}, {y_train_raw.max():.3f}]")
   print("="*50)
   ```

5. **Rerun from scratch**
   - Sometimes helps clear GPU/memory issues
   - Restart kernel first

---

## 🎓 Learning Resources

### In This Package
1. `PROJECT_SUMMARY.md` - Overall project structure
2. `TECHNICAL_GUIDE.md` - Deep dive into algorithms
3. `TROUBLESHOOTING_FAQ.md` - Problem solving
4. `ver1.ipynb` - Executable code with comments

### External Resources
- TensorFlow Time Series: https://tensorflow.org/tutorials/structured_data/time_series
- LSTM Tutorial: Understanding LSTMs (Colah's Blog)
- Electricity Load Forecasting: IEEE papers on energy forecasting

---

**Quick Reference Version**: 1.0
**Last Updated**: 2026-04-22
**Print-friendly**: Yes (optimized for 4-page print)
