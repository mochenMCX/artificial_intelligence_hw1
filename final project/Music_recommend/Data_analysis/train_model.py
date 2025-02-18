import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
from sklearn.model_selection import GridSearchCV

file_path = 'spotify_dataset/songs_preprocessed.csv'
df = pd.read_csv(file_path)

# add feature: Like
df['Like'] = None

# can customize features that affect 'Like'
for index, row in df.iterrows():
    if row['valence'] >= 0.3 and row['loudness'] <= 0.9 and row['popularity'] >= 0.3:
        df.at[index, 'Like'] = 1
    else:
        df.at[index, 'Like'] = 0

# Shuffle the data to remove any biases
data_shuffled = df.sample(frac=1, random_state=42)

# equally distribute data with respect to column: 'year'
equal_distribute_col = 'year'
train_data, test_data = train_test_split(df, test_size=0.1, stratify=df[equal_distribute_col], random_state=42)

# drop unused columns
train_data = train_data.drop(['artist', 'song', 'valence', 'popularity', 'duration_ms'], axis=1)


# ----------------------------------------
# divide dataset into training and testing
x = train_data.drop("Like", axis=1)
y = train_data["Like"].astype(int)

# Perform stratified train-test split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)

# Initialize the Random Forest classifier
random_forest = RandomForestClassifier(n_estimators=10, random_state=42, max_features=6, min_samples_split=30, min_samples_leaf=4, max_depth = 3)

# Train the model
random_forest.fit(x_train, y_train)

# Make predictions
predictions = random_forest.predict(x_test)

# Evaluate the model
accuracy = accuracy_score(y_test, predictions)
print("Accuracy:", accuracy)

# Print classification report for detailed evaluation
print("Classification Report:")
print(classification_report(y_test, predictions))

# ----------------------------------------
# Define the parameter grid to search over
param_grid = {
    'n_estimators': [100, 150, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 4, 6],
    'min_samples_leaf': [1, 2, 4]
}

# Create a RandomForestClassifier instance
rf = RandomForestClassifier(random_state=42)

# Setup the RandomizedSearchCV instance
random_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, verbose=0, n_jobs=-1)

# Fit the RandomizedSearchCV instance to the data
random_search.fit(x, y)

# Print the best parameters and the corresponding score
print(f"Best parameters: {random_search.best_params_}")
print(f"Best score: {random_search.best_score_}")

# Retrieve the best estimator
best_rf = random_search.best_estimator_

# Initialize the Random Forest classifier
best_rf = RandomForestClassifier(n_estimators=100, random_state=42, min_samples_split=2, min_samples_leaf=1, max_depth=10)

# Train the model
best_rf.fit(x_train, y_train)

# Make predictions
predictions = best_rf.predict(x_test)

# Evaluate the model
accuracy = accuracy_score(y_test, predictions)
print("Accuracy:", accuracy)

# You can also print classification report for detailed evaluation
print("Classification Report:")
print(classification_report(y_test, predictions))

# -----------------------------------------------
# Identidy the important features affecting 'Like'
feature_importances = pd.DataFrame({
    'Feature': x.columns,
    'Importance': best_rf.feature_importances_
}).sort_values(by='Importance', ascending=False)

print(feature_importances)

# Select top 5 important features
top_features = feature_importances.head(5)['Feature'].values
print("\nTop 5 Features:", top_features)

# Determine optimal thresholds and direction for each top feature
thresholds = {}
directions = {}
for feature in top_features:
    fpr, tpr, thresholds_roc = roc_curve(y_test, x_test[feature])
    youdens_j = tpr - fpr
    optimal_idx = np.argmax(youdens_j)
    optimal_threshold = thresholds_roc[optimal_idx]
    thresholds[feature] = optimal_threshold
    
    # Determine direction: evaluate performance metrics above and below the threshold
    above_threshold = x_test[feature] > optimal_threshold
    below_threshold = x_test[feature] <= optimal_threshold
    
    true_positive_rate_above = np.sum(y_test[above_threshold] == 1) / np.sum(above_threshold)
    true_positive_rate_below = np.sum(y_test[below_threshold] == 1) / np.sum(below_threshold)
    
    if true_positive_rate_above > true_positive_rate_below:
        directions[feature] = 'greater'
    else:
        directions[feature] = 'less'

print("Optimal Thresholds:", thresholds)
print("Threshold Directions:", directions)
