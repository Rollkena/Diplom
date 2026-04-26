# Technical Implementation Guide

## 1. Data Preparation Strategy

### 1.1 Feature Engineering

#### Time Features (Cyclic Encoding)
```python
# Hours (0-23) → sine/cosine encoding
hour_sin = sin(2π × hour / 24)
hour_cos = cos(2π × hour / 24)

# Day-of-week (0-6) → cyclic encoding  
dow_sin = sin(2π × dow / 7)
dow_cos = cos(2π × dow / 7)

# Month (1-12) → cyclic encoding
month_sin = sin(2π × month / 12)
month_cos = cos(2π × month / 12)
```

**Why**: Cyclic encoding preserves the circular nature of time (e.g., hour 23 is close to hour 0)

#### Lag Features (Historical Dependencies)
```python
lag_1    = actual(t-1)     # 1 hour ago
lag_24   = actual(t-24)    # 24 hours ago (daily seasonality)
lag_168  = actual(t-168)   # 168 hours ago (weekly seasonality)
```

#### Rolling Statistics
```python
roll_24  = mean(actual[t-25:t-1])     # 24-hour average (excludes current point)
roll_168 = mean(actual[t-169:t-1])    # 7-day average (excludes current point)
```

**Critical**: All shift/lag operations use `.shift(1).rolling()` to ensure no forward-looking data leakage.

### 1.2 Data Splitting (No Leakage)

```python
n_samples = 10000 (example)
train_end = 7000  (70%)
val_end = 8500    (85%)

train_df = df[0:7000]      # Earliest data
val_df = df[7000:8500]     # Middle period  
test_df = df[8500:]        # Most recent (unseen)
```

**Why Time-Based Split**:
- Reflects real deployment scenario
- Future test period is always after validation
- No data leakage from future to past

### 1.3 Scaling (MinMaxScaler)

```python
# FIT on training data only
scaler_X = MinMaxScaler()
X_train_scaled = scaler_X.fit_transform(train_df[features])

# APPLY to val/test using train statistics
X_val_scaled = scaler_X.transform(val_df[features])
X_test_scaled = scaler_X.transform(test_df[features])
```

**Why Separate Scalers for X and y**:
- Input features (X) scaling helps model convergence
- Target (y) scaling enables inverse transform for interpretable metrics
- All scaled to [0, 1] range

---

## 2. Sequence Generation

### 2.1 Sliding Window Approach

```
Input Window (Lookback = 168h)          Output (Horizon = 24h)
[t-168, t-167, ..., t-2, t-1]  →  [t, t+1, ..., t+22, t+23]

     ├─ 7 days of history              ├─ Next 24 hours to predict
     └─ All features included          └─ Only target variable
```

### 2.2 Sequence Creation Algorithm

```python
def create_sequences(X, y, lookback=168, horizon=24):
    Xs, ys = [], []
    for i in range(len(X) - lookback - horizon):
        Xs.append(X[i : i+lookback])           # shape: (168, n_features)
        ys.append(y[i+lookback : i+lookback+horizon])  # shape: (24, 1)
    return np.array(Xs), np.array(ys)

# Result shapes
X_train.shape = (n_train_sequences, 168, n_features)  # e.g., (5000, 168, 25)
y_train.shape = (n_train_sequences, 24, 1)            # e.g., (5000, 24, 1)
```

**Key Property**: Each sequence is independent and non-overlapping (maximizes training data utilization while preventing data leakage between train/val/test).

---

## 3. LSTM Encoder-Decoder Architecture

### 3.1 Model Structure

```
INPUT: (168, 25)  [168 hours, 25 features]
       ↓
ENCODER LSTM(128, return_sequences=False)
       ├─ Processes all 168 timesteps
       ├─ Outputs context vector: (128,)
       ├─ Dropout(0.2) for regularization
       ↓
REPEAT VECTOR (to match horizon)
       ├─ Expands context: (128,) → (24, 128)
       ↓
DECODER LSTM(128, return_sequences=True)
       ├─ Generates 24 timesteps from context
       ├─ Returns full sequence: (24, 128)
       ├─ Dropout(0.2)
       ↓
LSTM(64, return_sequences=True)
       ├─ Additional temporal refinement
       ├─ Output: (24, 64)
       ↓
TimeDistributed Dense(32, activation='relu')
       ├─ Applied to each of 24 timesteps
       ├─ Output: (24, 32)
       ↓
TimeDistributed Dense(1)
       ├─ Final prediction for each hour
       ├─ Output: (24, 1)
       ↓
OUTPUT: (24, 1)  [24 hourly predictions]
```

### 3.2 Why This Architecture?

1. **Encoder**: Compresses historical information into context vector
2. **RepeatVector**: Bridges encoder output to decoder input
3. **Decoder**: Generates forecast sequence using learned context
4. **Multi-layer Decoder**: Improves sequence coherence and captures hierarchical patterns
5. **TimeDistributed**: Ensures same transformation applied to each forecast hour
6. **Dropout**: Prevents overfitting by randomly deactivating neurons

---

## 4. Training Strategy

### 4.1 Loss Function & Optimization

```python
model.compile(
    optimizer=Adam(learning_rate=1e-3),
    loss='mse',                    # Penalizes larger errors more
    metrics=['mae']                # For interpretable monitoring
)
```

- **MSE Loss**: Differentiable, standard for regression, sensitive to outliers
- **Adam Optimizer**: Adaptive learning rates, works well with RNNs
- **Learning Rate 1e-3**: Good starting point for time series

### 4.2 Training Configuration

```python
model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=[early_stop, reduce_lr]
)
```

**Callbacks**:
1. **EarlyStopping**
   - Monitors: val_loss
   - Patience: 8 epochs
   - Stops if no improvement for 8 consecutive epochs
   - Restores best weights

2. **ReduceLROnPlateau**
   - Monitors: val_loss
   - Factor: 0.5 (reduce learning rate by half)
   - Patience: 4 epochs
   - Min learning rate: 1e-5

**Batch Size Selection**:
- Batch=32: Good balance between gradient stability and memory
- Updates weights 156 times per epoch (≈5000 samples / 32)

---

## 5. Evaluation Metrics

### 5.1 Global Metrics (Aggregate)

#### Mean Absolute Error (MAE)
```
MAE = (1/n) × Σ|y_true - y_pred|

Interpretation: Average absolute deviation in original units
Unit: Same as target variable (MW, kWh, etc.)
Use: Primary metric for interpretability
```

#### Root Mean Squared Error (RMSE)
```
RMSE = √[(1/n) × Σ(y_true - y_pred)²]

Interpretation: Penalizes large errors more than small ones
Unit: Same as target variable
Use: Identifies if model struggles with specific patterns
```

#### Mean Absolute Percentage Error (MAPE)
```
MAPE = (100/n) × Σ|y_true - y_pred| / |y_true|

Interpretation: Average percentage error
Unit: Percentage (%)
Use: Scale-independent comparison, handles different demand levels
Limitation: Undefined when y_true = 0, so add small epsilon
```

#### Symmetric MAPE (sMAPE)
```
sMAPE = (100/n) × Σ[2×|y_pred - y_true| / (|y_true| + |y_pred|)]

Interpretation: Symmetric percentage error, better behaved than MAPE
Unit: Percentage (%)
Use: Preferred over MAPE for symmetric treatment
```

### 5.2 Per-Horizon Metrics

Calculated separately for each forecast step T+1, T+2, ..., T+24:

```
For each hour h in [1..24]:
    yt_h = y_true[:, h, 0]          # All samples, hour h
    yp_h = y_pred[:, h, 0]          # All predictions, hour h
    
    MAE_h = mean(|yt_h - yp_h|)
    RMSE_h = sqrt(mean((yt_h - yp_h)²))
    MAPE_h = mean(|yt_h - yp_h| / |yt_h|) × 100
```

**Insight**: 
- Shows if model is better at short-term (T+1-6) vs long-term (T+19-24)
- Typical pattern: Error increases with horizon (harder to predict far future)
- Useful for choosing which hours to emphasize in deployment

---

## 6. Baseline: Seasonal Naive (Lag-24)

### 6.1 Algorithm

```python
# For each test sequence at time t:
# Predict using actual load from 24 hours ago

for each future hour h in [0..23]:
    y_baseline[t, h] = actual[t + LOOKBACK - 24 + h]

# Equivalent to:
y_baseline = y_true shifted by 24 hours back
```

### 6.2 Rationale

- **Electricity load is highly seasonal**: Same hour each day usually has similar demand
- **Simple and interpretable**: Easy for stakeholders to understand
- **Strong baseline**: Hard to beat with simple models
- **Fair comparison**: Validates that added complexity of LSTM is justified

### 6.3 Why Not Naive (Lag-1)?

- Electricity demand varies significantly hour-to-hour
- Daily seasonality (lag-24) is much stronger
- Lag-24 captures the dominant pattern

---

## 7. Model Comparison Strategy

### 7.1 Metric Hierarchy

1. **Primary**: MAE (interpretable, robust)
2. **Secondary**: RMSE (identifies worst cases)  
3. **Tertiary**: MAPE (scale-independent)

### 7.2 Improvement Calculation

```
Improvement% = (Baseline_Error - Model_Error) / Baseline_Error × 100

Positive: Model is better
Negative: Baseline is better (indicates model needs tuning)
```

### 7.3 Models Compared

| Model | Type | Complexity | Training Time |
|-------|------|-----------|---------------|
| Baseline (Lag-24) | Rule-based | O(1) | Instant |
| LSTM | RNN | High | ~5-10 min |
| GRU | RNN | Medium | ~3-5 min |

**GRU Advantage**: Fewer parameters than LSTM (GRU gate = gating mechanism simplification)
**LSTM Advantage**: More expressive gating (forget/input/output gates separate)

---

## 8. Data Leakage Prevention

### 8.1 Common Pitfalls

❌ **WRONG**: Use all data to fit scaler
```python
scaler.fit(df[features])  # Includes validation/test info!
X = scaler.transform(df[features])
```

❌ **WRONG**: Shuffle time series data
```python
train, test = train_test_split(df, shuffle=True)  # Destroys temporal order
```

❌ **WRONG**: Use future values in lag features
```python
lag_future = actual.shift(-24)  # Shift forward! Data leakage
```

### 8.2 Correct Implementation

✅ **RIGHT**: Fit scaler on training data only
```python
scaler.fit(train_df[features])
X_train = scaler.transform(train_df[features])
X_test = scaler.transform(test_df[features])  # Uses train statistics
```

✅ **RIGHT**: Time-based split, no shuffling
```python
train = df[:0.7 * n]
val = df[0.7*n : 0.85*n]
test = df[0.85*n :]
```

✅ **RIGHT**: Use only past values in lags
```python
lag_1 = actual.shift(1)      # t-1 (in the past)
lag_24 = actual.shift(24)    # t-24 (in the past)
```

---

## 9. Production Deployment Checklist

### Pre-Deployment
- [ ] Achieve >10% MAE improvement over baseline
- [ ] Validate on multiple seasons/years
- [ ] Test with missing data scenarios
- [ ] Profile memory/CPU requirements
- [ ] Document feature requirements

### Deployment
- [ ] Retrain model monthly with new data
- [ ] Monitor prediction errors in real-time
- [ ] Set up alerts for anomalously high errors
- [ ] Log all predictions for audit trail
- [ ] Implement fallback to baseline if model fails

### Post-Deployment
- [ ] Track prediction accuracy over time
- [ ] Identify seasonal patterns in errors
- [ ] Gather stakeholder feedback
- [ ] Plan model improvements
- [ ] A/B test against baseline periodically

---

## 10. Further Improvements

### 10.1 Architecture Enhancements

1. **Attention Mechanism**
   ```
   Allows model to focus on important historical timesteps
   Better for long sequences (168 hours)
   ```

2. **Temporal Fusion Transformer (TFT)**
   ```
   Combines LSTM with attention
   Handles multiple time-scales naturally
   State-of-art for energy forecasting
   ```

3. **Hybrid Models**
   ```
   ARIMA + LSTM: Combine statistical and deep learning
   Ensemble: Average multiple model predictions
   ```

### 10.2 Data Enhancements

1. **External Calendars**
   - Daylight Saving Time transitions
   - Regional holidays
   - School breaks, vacation periods

2. **Event Data**
   - Weather alerts
   - Grid maintenance
   - Exceptional demand events

3. **Real-Time Data**
   - Current system frequency
   - Reserve margins
   - Demand-side management events

---

**Document Version**: 1.0
**Last Updated**: 2026-04-22
