# Imports for the model
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Imports for the ONNX conversion
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import json

# 1. Load the data
data = pd.read_csv('../ml/dataset/dataset_training.csv')

# Select features
selected_features = [
    'length_url',          # Length of the URL
    'length_hostname',     # Length of the hostname
    'ip',                  # Contains IP address (0/1)
    'nb_dots',            # Number of dots
    'nb_hyphens',         # Number of hyphens
    'nb_qm',              # Number of question marks
    'nb_and',             # Number of & symbols
    'nb_eq',              # Number of = symbols
    'nb_underscore',      # Number of underscores
    'nb_percent',         # Number of % symbols
    'nb_slash',           # Number of slashes
    'nb_semicolumn',      # Number of semicolons
    'nb_www',             # Contains 'www' (0/1)
    'page_rank',          # PageRank score
    'google_index',       # Google index (0/1)
    'status'              # Target variable
]
filtered_data = data[selected_features]

# 2. Separate features and target
x = filtered_data.drop('status', axis=1)
y = filtered_data['status']

# Convert target to binary (0 for legitimate, 1 for phishing)
y = (y == 'phishing').astype(int)

# 3. Handle missing values
x = x.fillna(-1)

# 4. Split the data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# 5. Create and train Random Forest model
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=2,
    random_state=42
)

# 6. Train the model
rf_model.fit(x_train, y_train)

# 7. Make predictions
y_pred = rf_model.predict(x_test)

# 8. Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy:.2f}")

# Print detailed classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Print confusion matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 9. Feature importance analysis
feature_importance = pd.DataFrame({
    'feature': x.columns,
    'importance': rf_model.feature_importances_
})
print("\nFeature Importance:")
print(feature_importance.sort_values('importance', ascending=False))

# 10. Save the model
joblib.dump(rf_model, '../ml/model/random_forest_model.joblib')

# Convert to ONNX
feature_names = list(x.columns)
initial_type = [('float_input', FloatTensorType([None, len(feature_names)]))]
onnx_model = convert_sklearn(rf_model, initial_types=initial_type)

# Save ONNX model
with open("../ml/model/rf_model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

# Save feature metadata
model_metadata = {
    'feature_names': feature_names,
    'feature_importance': rf_model.feature_importances_.tolist(),
    'model_accuracy': accuracy
}

with open('../ml/model/model_metadata.json', 'w') as f:
    json.dump(model_metadata, f)