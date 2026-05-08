import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import PowerTransformer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 1. Load Data (assuming it's already sorted chronologically)
# df = pd.read_csv('your_dataset.csv')
# df['timestamp'] = pd.to_datetime(df['timestamp'])
# df = df.sort_values("timestamp").reset_index(drop=True)

# 2. Define columns to drop based on your notebook
cols_to_drop = [
    'timestamp', 'at_c', 'rh_pct', 'ws_ms', 'wd_deg', 'rf_mm', 'tot_rf_mm', 
    'station_id', 'station', 'state', 'city', 'era5_temp_k', 'era5_dewpoint_k', 
    'era5_pressure_pa', 'era5_u10_ms', 'era5_v10_ms', 'era5_precip_m', 
    'solar_altitude_deg', 'era5_sw_down_wm2', 'era5_temp_c'
]

# Create Features (X) and Target (y)
X = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
y = df["sr_wm2"]

# 3. Train/Test Split (Chronological for Time Series)
split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx].copy(), X.iloc[split_idx:].copy()
y_train, y_test = y.iloc[:split_idx].copy(), y.iloc[split_idx:].copy()

# 4. Apply Power Transform (Yeo-Johnson) as specified in the paper
# This fosters homogeneous feature scales and handles skewed distributions
print("Fitting PowerTransformer...")
scaler_X = PowerTransformer(method='yeo-johnson', standardize=True)
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

scaler_y = PowerTransformer(method='yeo-johnson', standardize=True)
y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1))
y_test_scaled = scaler_y.transform(y_test.values.reshape(-1, 1))

# 5. Define Time Series Parameters
LOOKBACK = 24       # Use the past 24 hours of data to make a prediction
HORIZON = 24        # Predict the solar generation 24 hours out
BATCH_SIZE = 256

def create_ts_dataset(X, y, lookback, horizon, batch_size):
    """
    Creates a memory-efficient sliding window dataset.
    Inputs: Sequence of length 'lookback'
    Targets: The 'y' value 'horizon' steps in the future
    """
    # The target needs to be shifted by the horizon
    start_index = lookback + horizon - 1
    
    # Generate the dataset
    dataset = tf.keras.utils.timeseries_dataset_from_array(
        data=X[:-horizon],
        targets=y[start_index:],
        sequence_length=lookback,
        batch_size=batch_size,
        shuffle=False # Keep chronological order intact
    )
    return dataset

print("Creating batched sequence datasets...")
train_dataset = create_ts_dataset(X_train_scaled, y_train_scaled, LOOKBACK, HORIZON, BATCH_SIZE)
test_dataset = create_ts_dataset(X_test_scaled, y_test_scaled, LOOKBACK, HORIZON, BATCH_SIZE)



# 6. Define the Deep Stacked LSTM Model
model = models.Sequential([
    # First LSTM layer: Wider capacity, returns the full sequence to the next layer
    layers.LSTM(128, activation='relu', return_sequences=True, 
                input_shape=(LOOKBACK, X_train_scaled.shape[1])),
    layers.Dropout(0.2), # Randomly drops 20% of connections to prevent overfitting
    
    # Second LSTM layer: Compresses the sequence into a final state vector
    layers.LSTM(64, activation='relu', return_sequences=False),
    layers.Dropout(0.2),

    # Fully connected Dense layers (mirroring the depth mentioned in the paper)
    layers.Dense(64, activation='relu'),
    layers.Dense(32, activation='relu'),
    
    # Final output layer
    layers.Dense(1)
])

# Compile the model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='mean_squared_error',
              metrics=['mae'])

model.summary()


# 8. Generate Predictions
print("Generating predictions on the test set...")
y_pred_scaled = model.predict(test_dataset)

# Note: timeseries_dataset_from_array drops the last (lookback + horizon - 1) 
# targets to form complete windows. We must align y_test to match.
target_start_idx = LOOKBACK + HORIZON - 1
y_test_aligned = y_test.values[target_start_idx: target_start_idx + len(y_pred_scaled)]

# 9. Inverse Transform Predictions to original scale
y_pred = scaler_y.inverse_transform(y_pred_scaled)

# 10. Calculate Final Evaluation Metrics
rmse = np.sqrt(mean_squared_error(y_test_aligned, y_pred))
mae = mean_absolute_error(y_test_aligned, y_pred)
r2 = r2_score(y_test_aligned, y_pred)

print("\n--- LSTM Model Results (24 Hours Out) ---")
print(f"RMSE: {rmse:.2f} W/m²")
print(f"MAE:  {mae:.2f} W/m²")
print(f"R² Score: {r2:.4f}")