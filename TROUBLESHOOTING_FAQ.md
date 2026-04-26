# Troubleshooting & FAQ Guide

## 🔴 Common Issues & Solutions

### Issue 1: "Memory Error" or "Out of Memory"

**Problem**: 
```
ResourceExhaustedError: OOM when allocating tensor...
```

**Solutions** (in order):
1. **Reduce batch size**
   ```python
   batch_size=32 → batch_size=16  # Or even 8
   ```

2. **Reduce sequence length**
   ```python
   LOOKBACK = 168 → 84  # Reduce from 7 days to 3.5 days
   ```

3. **Reduce model size**
   ```python
   LSTM(128) → LSTM(64)  # Fewer units
   ```

4. **Reduce number of features**
   - Drop less important weather variables
   - Use feature selection before modeling

5. **Use GPU**
   ```python
   # Check GPU availability
   import tensorflow as tf
   print(tf.config.list_physical_devices('GPU'))
   ```

---

### Issue 2: "Model Not Improving" or "High Loss"

**Problem**: 
- Validation loss remains high or increases
- Model worse than baseline
- Training loss decreases but validation loss increases (overfitting)

**Solutions**:

**For High Loss**:
1. Check data preprocessing
   ```python
   print(X_train.shape, X_train.min(), X_train.max())  # Should be [0, 1]
   print(y_train.shape, y_train.min(), y_train.max())  # Should be [0, 1]
   ```

2. Verify scaler was fit on training data only
   ```python
   # Check scaler min/max
   print("X scaler data_min:", scaler_X.data_min_)
   print("X scaler data_max:", scaler_X.data_max_)
   ```

3. Check for NaN values
   ```python
   print("NaN in X_train:", np.isnan(X_train).sum())
   print("NaN in y_train:", np.isnan(y_train).sum())
   ```

**For Overfitting** (train loss ↓, val loss ↑):
1. Increase dropout
   ```python
   Dropout(0.2) → Dropout(0.3) or 0.4
   ```

2. Reduce model capacity
   ```python
   LSTM(128) → LSTM(64)
   ```

3. Add L2 regularization
   ```python
   layers.LSTM(128, kernel_regularizer=tf.keras.regularizers.l2(0.01))
   ```

4. Reduce epochs or increase early stopping patience
   ```python
   patience=8 → patience=5  # Stop earlier
   ```

---

### Issue 3: "Data Shape Error"

**Problem**:
```
ValueError: Shape mismatch: feeding a size n_batch=32 
tensor into a placeholder expecting shape (?, 168, 25)
```

**Diagnosis**:
```python
# Print actual shapes
print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)
print("Model input shape:", model.input_shape)
print("Model output shape:", model.output_shape)

# Check if shapes match
assert X_train.shape[1] == LOOKBACK  # 168
assert X_train.shape[2] == n_features  # 25
assert y_train.shape[1] == HORIZON   # 24
assert y_train.shape[2] == 1
```

**Solutions**:
1. Verify `create_sequences` function executed correctly
2. Check that `train_df`, `val_df`, `test_df` are not empty
3. Ensure features list is complete
   ```python
   print("Features:", len(features))
   print("Features list:", features)
   ```

---

### Issue 4: "Metric Says Model is Worse Than Baseline"

**Problem**:
```
LSTM MAE: 5.23
Baseline MAE: 4.85
Improvement: -8.23%  ← Negative!
```

**Analysis**:
This is normal if your baseline is very strong. Electricity load has strong daily seasonality, so lag-24 is a tough baseline.

**Solutions**:

1. **Verify baseline is computed correctly**
   ```python
   # Baseline should be y_test shifted by 24 hours
   # Check a few samples manually
   print("y_test[0, 0]:", y_test_inv[0, 0, 0])
   print("y_baseline[0, 0]:", y_baseline[0, 0, 0])
   ```

2. **Try different baseline**
   - Moving average of past 7 days at same hour
   - Exponential smoothing

3. **Improve model**
   - Add more features (weather, external events)
   - Use attention mechanism
   - Increase training time
   - Use ensemble of multiple models

4. **Accept if improvement is marginal**
   - Sometimes baseline is already optimal
   - LSTM still provides uncertainty estimates
   - Consider business factors beyond accuracy

---

### Issue 5: "CSV Export is Empty or Wrong"

**Problem**:
- `predictions_detailed.csv` has 0 rows
- Timestamps don't match actual times

**Solutions**:

1. **Check if sequences were created**
   ```python
   print("X_test length:", len(X_test))
   print("y_test length:", len(y_test))
   # Both should be > 0
   ```

2. **Verify test_start_idx calculation**
   ```python
   test_start_idx = val_end + LOOKBACK
   print("test_start_idx:", test_start_idx)
   print("len(df):", len(df))
   # Should have test_start_idx < len(df)
   ```

3. **Check datetime column exists**
   ```python
   print("Columns:", df.columns.tolist())
   # Should include 'datetime'
   print(df[['datetime']].head())
   ```

---

### Issue 6: "Plots/Visualizations Not Showing"

**Problem**:
- PNG files generated but no display in notebook
- Matplotlib not showing

**Solutions**:

1. **Enable matplotlib in notebook**
   ```python
   import matplotlib
   matplotlib.use('Agg')  # For non-interactive backend
   # OR
   %matplotlib inline  # In Jupyter notebook
   ```

2. **Check if files were saved**
   ```python
   import os
   print(os.path.exists('forecast_comparison.png'))  # Should be True
   print(os.path.getsize('forecast_comparison.png'))  # Should be > 0
   ```

3. **Regenerate plots with explicit save**
   ```python
   plt.savefig('my_plot.png', dpi=150, bbox_inches='tight')
   plt.close()  # Important: close after saving
   ```

---

### Issue 7: "Predictions Don't Match Inverse Transform"

**Problem**:
- y_pred_inv values outside reasonable range
- Contains NaN or Inf

**Solutions**:

1. **Check if model was trained**
   ```python
   # Model should complete fit() without errors
   print("Model trained:", model.history is not None)
   ```

2. **Verify predictions shape**
   ```python
   y_pred = model.predict(X_test)
   print("y_pred shape:", y_pred.shape)
   print("y_pred range:", y_pred.min(), y_pred.max())
   # Should be approximately [0, 1] if data was scaled
   ```

3. **Check scaler
_y was fit correctly**
   ```python
   print("Scaler data_min:", scaler_y.data_min_)
   print("Scaler data_max:", scaler_y.data_max_)
   # Should be sensible values from training data
   ```

4. **Look for NaN propagation**
   ```python
   if np.isnan(y_pred).any():
       print("NaN in predictions!")
       # Check training data for NaN
   ```

---

## ❓ Frequently Asked Questions

### Q1: How many samples do I need?

**A**: 
- **Minimum**: 1 year of hourly data (8,760 samples)
  - 70% training: 6,132 samples
  - With LOOKBACK=168, creates ~5,900 sequences
- **Recommended**: 2-3 years
  - Better seasonal coverage
  - More validation data
  - Handles special events better
- **Ideal**: 5+ years
  - Different climate/demand patterns
  - Business cycle variations

---

### Q2: Should I use different lookback for different data?

**A**:
- **168h (7 days)**: Good general choice, captures weekly pattern
- **336h (14 days)**: If you have multi-week patterns
- **24h (1 day)**: If data is limited or for quick experiments
- **Compromise**: Start with 168, tune based on error analysis

Rule: `LOOKBACK = 7 × 24` (1 week) is sweet spot

---

### Q3: Can I use this for other time series (not electricity)?

**A**: Yes! The approach works for any time series with:
- Daily seasonality
- Calendar effects
- Exogenous features available

**Examples**:
- Water consumption ✓
- Gas demand ✓
- Traffic flow ✓
- Website traffic ✓
- Hotel occupancy ✓

**What to adjust**:
- LOOKBACK: Depends on your seasonality (daily vs weekly vs monthly)
- Features: Replace weather with domain-specific variables
- Baseline: Use appropriate lag (e.g., lag_7 for weekly pattern)

---

### Q4: Why split 70/15/15 and not other ratios?

**A**: 
```
70/15/15 is standard because:
- 70% training: Sufficient for LSTM to learn patterns
- 15% validation: Large enough for reliable error estimation
- 15% test: Final unbiased evaluation
```

**For more data** (5+ years):
- 70/10/20: More test data for better final estimate
- 60/20/20: More validation for hyperparameter tuning

**For less data** (< 1 year):
- 80/10/10: Maximize training
- Consider cross-validation alternatives

---

### Q5: Can I retrain the model with new data?

**A**: Yes, but carefully:

```python
# Approach 1: Retrain from scratch (recommended monthly)
model = build_model()
model.fit(X_train_new, y_train_new, ...)

# Approach 2: Fine-tune existing model (quarterly)
model.fit(X_train_new, y_train_new, 
          epochs=10,  # Few epochs, using old weights as init
          initial_epoch=50)  # Continue from last epoch
```

**Important**:
- ALWAYS refit scaler on new training data
- Keep old model for A/B testing
- Document retraining date

---

### Q6: What should I do if MAPE is very high?

**A**:

**Diagnose**:
```python
# Check if high values are skewing the metric
print("Mean actual:", y_true_flat.mean())
print("Min actual:", y_true_flat.min())
print("Max actual:", y_true_flat.max())
```

**If very low actual values present**:
- MAPE becomes unreliable (division by small numbers)
- Use MAE or RMSE instead
- Add epsilon to denominator: `(y_true + epsilon)`

**If genuinely high errors**:
- Use more features
- Increase model complexity  
- Check for missing seasonal patterns

---

### Q7: How do I interpret per-horizon error?

**A**: 
```python
# Example output:
T+01h | MAE: 1.234 | RMSE: 1.456 | MAPE: 5.23%  ← Error grows
T+06h | MAE: 2.345 | RMSE: 2.567 | MAPE: 8.34%
T+12h | MAE: 3.456 | RMSE: 3.789 | MAPE: 11.45%
T+24h | MAE: 4.567 | RMSE: 4.890 | MAPE: 14.56%  ← Hardest to predict
```

**Interpretation**:
- Error typically increases with horizon (expected)
- If error is high at T+1-3: Model struggling with immediate future
- If error is low at T+12-24: Model captures average well but misses peaks
- Use this to set expectations with stakeholders

---

### Q8: Should I use LSTM or GRU?

**A**:

| Aspect | LSTM | GRU |
|--------|------|-----|
| **Accuracy** | Slightly better | Slightly worse |
| **Speed** | Slower | ~33% faster |
| **Memory** | More parameters | Fewer parameters |
| **Training** | Longer | Quicker |
| **Overfitting risk** | Higher | Lower |

**Choose LSTM if**:
- You have ample compute resources
- Dataset is large (> 10K sequences)
- You want maximum accuracy

**Choose GRU if**:
- You have limited compute (laptop, edge device)
- Dataset is smaller
- You want faster training

---

### Q9: Can I use this model for real-time forecasting?

**A**: Yes, with modifications:

```python
# At each hour t+1:
# 1. Collect new actual load value
# 2. Update rolling window (remove oldest, add newest)
# 3. Preprocess with same scaler
# 4. Generate predictions for next 24 hours

def forecast_next_day(last_168_hours, model, scaler):
    X_new = scaler.transform(last_168_hours).reshape(1, 168, n_features)
    y_pred = model.predict(X_new, verbose=0)
    y_pred_inv = scaler_y.inverse_transform(y_pred.reshape(-1, 1))
    return y_pred_inv.reshape(24)
```

**Considerations**:
- Input must always be exactly 168 hours
- Scaler must be same as training
- Need reliable real-time data pipeline
- Monitor for concept drift

---

### Q10: How do I explain model predictions to non-technical stakeholders?

**A**: 

**Simple Explanation**:
> "The model looks at the past week of electricity usage and uses deep learning to predict the next day's hourly demand. It learns patterns like: mornings use less power, evenings use more, and Sundays differ from weekdays."

**Key Metrics to Share**:
- **MAE = 2.3 MW**: On average, prediction is off by 2.3 MW
- **MAPE = 5%**: Predictions are within ~5% of actual on average
- **Beats baseline by 15%**: Better than simple "same as yesterday" approach

**Visualizations to Show**:
1. Line chart: Actual vs Predicted (looks impressive)
2. Scatter plot: Actual vs Predicted (shows correlation)
3. Improvement bar chart: Model vs Baseline (shows ROI)

**Don't Share**:
- Internal model weights
- Detailed architecture
- Mathematical formulas (use analogies instead)

---

## 🔧 Debugging Checklist

Use this when nothing works:

- [ ] Data loaded correctly (`df.shape`, `df.dtypes`)
- [ ] Features computed properly (`X_train.shape`, no NaN)
- [ ] Scaling applied (`X_train` in [0,1])
- [ ] Sequences generated (`len(X_train) > 0`)
- [ ] Train/val/test split is correct (no overlap)
- [ ] Model builds without errors (`model.summary()`)
- [ ] Training starts and runs (`history.history['loss']` populated)
- [ ] Predictions generated (`y_pred.shape == y_test.shape`)
- [ ] Metrics calculated (`mae`, `rmse` are numbers)
- [ ] Visualizations saved (`os.path.exists('file.png')`)

If still stuck:
1. Rerun from beginning, one cell at a time
2. Print intermediate shapes at each step
3. Verify against sample notebook runs
4. Check TensorFlow/Keras versions
5. Look for error messages in console output

---

**FAQ Version**: 1.0
**Last Updated**: 2026-04-22
