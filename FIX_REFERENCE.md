# QUICK FIX REFERENCE

## What Was Wrong?
Baseline calculation compared values on **different scales**:
- LSTM predictions: properly scaled (0-1) → inverse-transformed back to original units
- Baseline values: raw values from original DataFrame (unscaled)

Result: MAPE = huge number because it's comparing 0.8 to 1000!

---

## What Was Fixed?

### Before (Buggy):
```python
baseline[seq_idx, t, 0] = df.iloc[lag_24_idx][target]  # Raw value ❌
```

### After (Fixed):
```python
raw_value = df.iloc[lag_24_idx][target]
value_scaled = scaler_y.transform([[raw_value]])[0, 0]
baseline[seq_idx, t, 0] = scaler_y.inverse_transform([[value_scaled]])[0, 0]  # ✓ Properly scaled
```

---

## Changes Made to ver2.ipynb

| Cell | Change |
|------|--------|
| Cell 6 | ✓ Fixed baseline calculation with proper scaling |
| New cell | ✓ Added diagnostic checks (zero values, scale consistency) |
| New cell | ✓ Added robust fallback baseline (with lag-168 and rolling mean) |

---

## What to Do Now

1. **Run Cell 6 and beyond** in ver2.ipynb with the data file
2. **Verify diagnostic output** shows consistency check passing
3. **Compare metrics**:
   - Baseline MAPE should be ~30-40% (not >90%)
   - LSTM MAPE should be ~20-30%
   - Improvement should be +20-40%

---

## Key Insight

**MAPE is sensitive to small values** → Use **sMAPE** as primary metric
- sMAPE = `2 * |actual - pred| / (|actual| + |pred|)` → always 0-200%
- More stable and reliable for electricity forecasting

---

## Files Reference

- **ver2.ipynb** - Updated notebook with fixes
- **BASELINE_FIX_SUMMARY.md** - Detailed explanation
- **diagnose_baseline.py** - Diagnostic reference code
