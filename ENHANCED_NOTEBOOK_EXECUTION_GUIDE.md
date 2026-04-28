# Enhanced Notebook: Quick Execution Guide

## 🚀 Running the Optimized Forecasting Pipeline

This guide shows how to execute the enhanced `ver3.ipynb` notebook with hyperparameter optimization and ensemble forecasting.

---

## 📋 Pre-Requisites

### Required Python Packages
```bash
pip install optuna
pip install scikit-learn
pip install tensorflow
pip install pandas numpy matplotlib seaborn
```

### Verify Installation
```python
import optuna
import sklearn.linear_model
import tensorflow
print("✓ All packages installed successfully")
```

---

## 🏃 Execution Workflow

### Phase 1: Data Preparation (Cells 1-6)
**Time**: ~2-3 minutes

```
Cell 1: Mount Google Drive
Cell 2: Import dependencies
Cell 3: Load data & preprocessing
Cell 4: Feature engineering
Cell 5: Train/val/test split
Cell 6: Create sequences
```

**Verify**: Check X_train, y_train shapes are correct

### Phase 2: Baseline Models (Cells 7-17)
**Time**: ~10-15 minutes

```
Cell 7-11: Original LSTM model
Cell 12-14: Original GRU model
Cell 15-16: Baseline (Lag-24) comparison
Cell 17: Optimization setup
```

**Verify**: Compare original LSTM vs GRU metrics

### Phase 3: Hyperparameter Optimization (Cells 18-22)
**Time**: ~15-20 minutes (longest phase)

```
Cell 18: Helper functions
Cell 19: LSTM optimization (10 trials)
Cell 20: GRU optimization (10 trials)
Cell 21: Train best LSTM
Cell 22: Train best GRU
```

**Monitor**: Watch for trial completions and "✓ Optimization Complete!" messages

**Expected Output**:
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

### Phase 4: Ensemble Implementation (Cells 23-28)
**Time**: ~5-8 minutes

```
Cell 23: Implement 3 ensemble strategies
Cell 24: Comprehensive comparison
Cell 25: Per-horizon analysis
Cell 26: Generate comparison visualizations
Cell 27: Generate 1-week forecasting plots
Cell 28: Export predictions to CSV
```

**Output Files**:
- `ensemble_comprehensive_comparison.png` ✓
- `ensemble_1week_forecasting.png` ✓
- `all_models_comprehensive_comparison.csv` ✓
- `ensemble_predictions_detailed.csv` ✓
- `optimal_hyperparameters.csv` ✓

### Phase 5: Final Report (Cell 29)
**Time**: ~1 minute

```
Cell 29: Generate final summary & deployment recommendations
```

---

## ⏱️ Total Execution Time
- **Full notebook**: 30-45 minutes
- **Parallel vs Sequential**: Sequential (dependencies between cells)

---

## 💻 Hardware Recommendations

| Resource | Minimum | Recommended | Ideal |
|----------|---------|-------------|-------|
| CPU | 4 cores | 8 cores | 16+ cores |
| RAM | 4GB | 8GB | 16GB+ |
| GPU | CPU-only | NVIDIA 4GB | NVIDIA 8GB+ |
| Disk | 500MB | 1GB | 2GB+ |

**Note**: GPU acceleration significantly reduces optimization time (2-3× speedup)

---

## 🔄 Execution Checkpoints

### After Cell 3 (Data Loading)
```python
print(f"Data shape: {df.shape}")
# Expected: (8000+, 16) - Depends on data file
```

### After Cell 6 (Sequences)
```python
print(f"X_train: {X_train.shape}, y_train: {y_train.shape}")
# Expected: (3000+, 168, 25) and (3000+, 24, 1)
```

### After Cell 17 (Original Models)
```python
print(f"Original LSTM MAE: {mae:.4f}")
print(f"Original GRU MAE: {mae_gru:.4f}")
# Expected: MAE values around 10-15
```

### After Cell 21 (Optimization Complete)
```python
print(f"Improvement: {improvement_vs_baseline:.2f}%")
# Expected: Positive percentage vs baseline
```

### After Cell 23 (Ensemble Complete)
```
🏆 Best Ensemble Strategy: [Strategy Name]
   MAE: X.XXXX
```

### After Cell 28 (Exports Complete)
```
✓ Exported ensemble predictions to: ensemble_predictions_detailed.csv
  Total predictions: 5000+
```

### After Cell 29 (Final Summary)
```
🏆 BEST OVERALL MODEL: [Model Name]
   MAE: X.XXXX
   
Improvements:
  vs Baseline: +XX.XX%
  vs Original LSTM: ±X.XX%
  vs Original GRU: ±X.XX%
```

---

## 🐛 Troubleshooting During Execution

### Issue: Optuna trials fail with memory error
**Solution**: Reduce trial epochs in Cells 19-20
```python
# Change from:
history = model.fit(..., epochs=30, ...)
# To:
history = model.fit(..., epochs=15, ...)
```

### Issue: "CUDA out of memory" error
**Solution**: 
```python
# Add before Cell 1:
import tensorflow as tf
# Use CPU only
tf.config.set_visible_devices([], 'GPU')
# Or limit GPU memory
gpus = tf.config.list_physical_devices('GPU')
tf.config.set_logical_device_configuration(gpus[0], [
    tf.config.LogicalDeviceConfiguration(memory_limit=2048)])
```

### Issue: Optimization takes too long
**Solution**: Reduce number of trials in Cells 19-20
```python
# Change from:
lstm_study.optimize(objective_lstm, n_trials=10)
# To:
lstm_study.optimize(objective_lstm, n_trials=5)
```

### Issue: "Module not found" error
**Solution**: Install missing package
```bash
pip install optuna  # if Optuna missing
pip install scikit-learn  # if sklearn missing
```

---

## 📊 Interpreting Results

### Metrics Explained

**MAE** (Mean Absolute Error)
- Average absolute deviation from actual
- Lower is better
- **Typical range**: 10-20 MW

**RMSE** (Root Mean Squared Error)
- Penalizes larger errors more
- Sensitive to outliers
- **Typical range**: 15-25 MW

**MAPE** (Mean Absolute Percentage Error)
- Percentage error relative to actual
- Good for comparing across different scales
- **Typical range**: 5-15%

### Comparing Models

**Example Scenario**:
```
Model                MAE     RMSE    MAPE     Status
─────────────────────────────────────────────────────
Original LSTM       12.34   15.67   8.5%     Baseline
Optimized LSTM      11.87   15.12   8.1%     ✓ +3.8% better
Ensemble (Weighted) 11.52   14.78   7.9%     ✓✓ +6.6% better
Baseline            14.23   17.45   9.8%     Reference
```

**Decision**: Use **Ensemble (Weighted)**

---

## 🎯 Next Steps After Execution

1. **Review visualizations**
   - `ensemble_comprehensive_comparison.png`
   - `ensemble_1week_forecasting.png`

2. **Check detailed predictions**
   - Open `ensemble_predictions_detailed.csv` in Excel
   - Verify predictions align with actual values

3. **Extract hyperparameters**
   - Use `optimal_hyperparameters.csv` for deployment
   - Build models with these exact parameters

4. **Deploy best model**
   - Use the ensemble strategy identified in Cell 23
   - Follow [HYPERPARAMETER_OPTIMIZATION_GUIDE.md](HYPERPARAMETER_OPTIMIZATION_GUIDE.md) for deployment

---

## 📝 Saving Your Work

### Export Models (Optional)
```python
# After training, save models
best_lstm_model.save('best_lstm_model.h5')
best_gru_model.save('best_gru_model.h5')
```

### Export Scalers (Important for deployment)
```python
import pickle
with open('scalers.pkl', 'wb') as f:
    pickle.dump({'X_scaler': scaler_X, 'y_scaler': scaler_y}, f)
```

### Backup Notebook
- Download `ver3.ipynb` after execution
- Save all generated PNG and CSV files
- Archive for reproducibility

---

## 🔍 Quality Assurance Checklist

- [ ] All 29 cells executed without errors
- [ ] Cell 29 displays "END OF ANALYSIS - PROJECT COMPLETE"
- [ ] All expected CSV files generated
- [ ] All PNG visualizations created
- [ ] Ensemble MAE < Baseline MAE
- [ ] Optimized models better than original models
- [ ] Per-horizon analysis shows consistent patterns
- [ ] 1-week visualization looks reasonable

---

## 📞 Support Resources

| Issue | Resource |
|-------|----------|
| Hyperparameter tuning questions | [HYPERPARAMETER_OPTIMIZATION_GUIDE.md](HYPERPARAMETER_OPTIMIZATION_GUIDE.md) |
| General troubleshooting | [TROUBLESHOOTING_FAQ.md](TROUBLESHOOTING_FAQ.md) |
| Technical details | [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) |
| Quick overview | [QUICK_START.md](QUICK_START.md) |

---

**Status**: ✅ Ready to Execute  
**Last Updated**: 2026-04-26  
**Estimated Runtime**: 30-45 minutes
