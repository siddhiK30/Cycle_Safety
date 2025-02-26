import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Generate Dummy Data
np.random.seed(42)
data = {
    "speed": np.random.randint(10, 50, 500),  # Speed in km/h
    "num_rides": np.random.randint(1, 30, 500),  # Number of rides per week
    "road_condition": np.random.choice([1, 2, 3], 500),  # 1=Smooth, 2=Moderate, 3=Rough
    "brake_behavior": np.random.uniform(0, 1, 500),  # 0=Smooth braking, 1=Sudden braking
    "safety_score": np.random.randint(30, 100, 500)  # Safety score (target)
}

df = pd.DataFrame(data)

# Print Safety Score
print(df["safety_score"].head())

# Split dataset
X = df.drop(columns=["safety_score"])
y = df["safety_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Model
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
model.fit(X_train_scaled, y_train)

# Predictions
y_pred = model.predict(X_test_scaled)

# Evaluate Model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse:.2f}")
print(f"R-Squared Score: {r2:.2f}")

# Plot Predictions vs Actual
test_indices = range(len(y_test))
plt.scatter(test_indices, y_test, label="Actual", alpha=0.6)
plt.scatter(test_indices, y_pred, label="Predicted", alpha=0.6)
plt.legend()
plt.xlabel("Test Sample Index")
plt.ylabel("Safety Score")
plt.title("Actual vs Predicted Safety Score")
plt.show()
