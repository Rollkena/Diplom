# =========================
# DIAGNOSTIC: BASELINE MAPE ISSUE
# =========================

"""
The problem in ver2.ipynb Cell 6:

The baseline calculation is using:
  baseline[seq_idx, t, 0] = df.iloc[lag_24_idx][target]

But this retrieves values from the ORIGINAL df, which are:
1. Not inverse-scaled (they're raw values from the Excel file)
2. Not aligned with the sequence indices correctly
3. The indexing calculation is problematic

This causes:
- MAPE to be extremely high (often >90%) because:
  - y_test_inv are inverse-transformed predictions (scaled 0-1, then back)
  - y_baseline are raw values from df (unscaled)
  - Comparing values on different scales → huge errors
  
Solution: Baseline should use inverse-transformed values from the same time period.
"""

print(__doc__)

print("\n" + "="*80)
print("KEY ISSUES IN BASELINE CALCULATION:")
print("="*80)

print("""
BUG #1: Data Scale Mismatch
  ❌ y_test_inv = scaler_y.inverse_transform(y_test)  # Properly scaled
  ❌ y_baseline = df.iloc[...][target]                # Raw unscaled values
  
  This compares apples to oranges!
  
  SOLUTION: Use scaled values for baseline too:
  y_baseline_raw = df_test.loc[lag_24_indices, target].values
  y_baseline = scaler_y.transform(y_baseline_raw)
  y_baseline_inv = scaler_y.inverse_transform(y_baseline)

BUG #2: Incorrect Indexing
  The indexing formula: actual_test_idx = val_end + (lookback - HORIZON) + seq_idx * HORIZON + t
  
  Assumptions being made:
  - Each sequence is separated by HORIZON (24) steps
  - But overlapping sequences might be used!
  - The formula doesn't account for how sequences were created
  
  Better approach: Track the actual timestamps for each sequence

BUG #3: Undefined Baseline Values
  If lag_24_idx < 0 or >= len(df), the baseline remains 0 (from initialization)
  This creates MASSIVE errors: |actual - 0| / |actual + 1e-8| = potentially infinite
  
  Check: How many baseline values are actually 0?
""")

print("\n" + "="*80)
print("RECOMMENDED FIX:")
print("="*80)

print("""
Replace the entire baseline calculation with:

# CORRECT BASELINE CALCULATION
def get_seasonal_naive_baseline_FIXED(X_test, scaler_y, lookback=168, horizon=24):
    '''
    Creates baseline using lag-24 from the actual lookback window.
    Uses inverse-transformed values for proper comparison.
    '''
    y_baseline = np.zeros((len(X_test), horizon, 1))
    
    # Last feature should be scaled actual values from lookback
    for seq_idx in range(len(X_test)):
        for t in range(horizon):
            # Get the scaled value from lookback window at position (168 - 24 + t)
            # This is "24 hours before the prediction starts" + offset t
            lookback_idx = lookback - 24 + t
            
            if lookback_idx < lookback and lookback_idx >= 0:
                # X_test[seq_idx, lookback_idx, -1] should be the scaled actual value
                # But we need the RAW actual value, not the scaled feature
                # 
                # Alternative: Use the known lag-24 values properly
                scaled_value = X_test[seq_idx, lookback_idx, -1]  # Last feature is scaled actual
                y_baseline[seq_idx, t, 0] = scaled_value
    
    # Inverse transform to get actual scale
    y_baseline_inv = scaler_y.inverse_transform(
        y_baseline.reshape(-1, 1)
    ).reshape(y_baseline.shape)
    
    return y_baseline_inv

# Or even simpler: use test_df directly with proper time alignment
y_baseline_fixed = np.zeros_like(y_pred_inv)
for seq_idx in range(len(X_test)):
    for t in range(horizon):
        # Get the index of the actual observation we're predicting
        obs_idx = test_start_idx + seq_idx * horizon + t
        # Get lag-24 value from 24 hours earlier
        lag_24_idx = obs_idx - 24
        
        if lag_24_idx >= 0 and lag_24_idx < len(df):
            # Use the value scaled and inverse-scaled the same way as y_test_inv
            value = df.iloc[lag_24_idx][target]
            value_array = np.array([[value]])
            value_scaled = scaler_y.transform(value_array)[0, 0]
            y_baseline_fixed[seq_idx, t, 0] = scaler_y.inverse_transform([[value_scaled]])[0, 0]
""")

print("\n" + "="*80)
print("EXPECTED RESULTS WITH FIX:")
print("="*80)
print("""
✓ Baseline MAPE should be in reasonable range (20-50% for electricity data)
✓ LSTM should clearly outperform baseline (improvement > 10%)
✓ sMAPE should be comparable to MAPE (not wildly different)
✓ Per-horizon errors should increase gradually (T+24 worse than T+1)
""")
