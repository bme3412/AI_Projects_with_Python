import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import os
from tqdm import tqdm
import time
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_combine_wr_data(base_path):
    all_data = []
    years = range(2018, 2024)
    total_files = sum(len([f for f in os.listdir(f"{base_path}/{year}_football_data/wr_data") if f.endswith('.csv')]) for year in years)
    
    with tqdm(total=total_files, desc="Loading files") as pbar:
        for year in years:
            year_path = f"{base_path}/{year}_football_data/wr_data"
            for file in os.listdir(year_path):
                if file.endswith(".csv"):
                    df = pd.read_csv(os.path.join(year_path, file))
                    df['Year'] = year
                    df['Week'] = int(file.split('_')[1].split('.')[0])
                    all_data.append(df)
                    pbar.update(1)
    
    print("Concatenating all data...")
    return pd.concat(all_data, ignore_index=True)

def explore_data(df):
    print("Exploring data...")
    print(f"Dataset shape: {df.shape}")
    print("\nColumns:")
    for col in df.columns:
        print(col)
    print("\nSample data:")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nUnique values in categorical columns:")
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        print(f"{col}: {df[col].nunique()} unique values")

def preprocess_wr_data_for_forecasting(df):
    print("Preprocessing data for forecasting...")
    
    # Sort the dataframe by player and date
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Week'].astype(str) + '-1', format='%Y-%W-%w')
    df = df.sort_values(['Player', 'Date'])
    
    # Handle missing values
    df = df.fillna(0)
    
    # Convert percentage strings to floats
    if 'ROST' in df.columns:
        df['ROST'] = df['ROST'].str.rstrip('%').astype('float') / 100.0
    
    # Feature engineering
    print("Creating new features...")
    if 'G' in df.columns and 'TGT' in df.columns:
        df['Targets_per_Game'] = df['TGT'] / df['G'].replace(0, 1)
    if 'YDS' in df.columns and 'TGT' in df.columns:
        df['Yards_per_Target'] = df['YDS'] / df['TGT'].replace(0, 1)
    if 'TD' in df.columns and 'REC' in df.columns:
        df['TD_Rate'] = df['TD'] / df['REC'].replace(0, 1)
    if 'YDS' in df.columns and 'REC' in df.columns:
        df['Yards_per_Reception'] = df['YDS'] / df['REC'].replace(0, 1)
    
    # Create lagged features
    print("Creating lagged features...")
    lag_features = ['REC', 'TGT', 'YDS', 'TD', 'Targets_per_Game', 'Yards_per_Target', 'TD_Rate', 'Yards_per_Reception']
    lag_features = [f for f in lag_features if f in df.columns]
    lags = [1, 2, 3, 4]  # Previous 1, 2, 3, and 4 weeks
    for feature in tqdm(lag_features, desc="Lagged features"):
        for lag in lags:
            df[f'{feature}_lag_{lag}'] = df.groupby('Player')[feature].shift(lag)
    
    # Calculate rolling averages
    print("Calculating rolling averages...")
    windows = [3, 5, 10]  # 3-week, 5-week, and 10-week rolling averages
    for feature in tqdm(lag_features, desc="Rolling averages"):
        for window in windows:
            df[f'{feature}_rolling_{window}'] = df.groupby('Player')[feature].transform(lambda x: x.rolling(window=window, min_periods=1).mean())
    
    # Create seasonal features
    print("Creating seasonal features...")
    df['Season_Week'] = df['Week']
    df['Season_Progress'] = df['Week'] / df['Week'].max()
    
    # Create team performance features
    print("Creating team performance features...")
    if 'Team' in df.columns:
        team_features = ['TGT', 'YDS', 'TD', 'REC']
        team_features = [f for f in team_features if f in df.columns]
        for feature in team_features:
            df[f'Team_{feature}_Total'] = df.groupby(['Team', 'Year', 'Week'])[feature].transform('sum')
            df[f'Player_{feature}_Share'] = df[feature] / df[f'Team_{feature}_Total'].replace(0, 1)
    
    # Opponent features
    print("Creating opponent features...")
    if 'Opponent' in df.columns:
        opponent_allowed = ['TGT', 'YDS', 'TD', 'REC']
        opponent_allowed = [f for f in opponent_allowed if f in df.columns]
        for feature in opponent_allowed:
            df[f'Opp_{feature}_Allowed'] = df.groupby(['Opponent', 'Year', 'Week'])[feature].transform('sum')
    else:
        print("Warning: 'Opponent' column not found. Skipping opponent features.")
    
    # Encode categorical variables
    print("Encoding categorical variables...")
    categorical_cols = ['Team', 'Opponent']
    categorical_cols = [col for col in categorical_cols if col in df.columns]
    df = pd.get_dummies(df, columns=categorical_cols)
    
    # Normalize numerical features
    print("Normalizing numerical features...")
    scaler = StandardScaler()
    numerical_features = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
    numerical_features = [f for f in numerical_features if f not in ['Year', 'Week', 'FPTS', 'Rank']]
    df[numerical_features] = scaler.fit_transform(df[numerical_features])
    
    # Drop rows with NaN values created by lag and rolling features
    df = df.dropna()
    
    print(f"Preprocessing completed. Final dataset shape: {df.shape}")
    
    return df

def train_forecast_model(X_train, y_train, X_val, y_val):
    # Define the parameter grid for RandomizedSearchCV
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']  # Removed 'auto' to address the warning
    }
    
    # Create a base model
    rf = RandomForestRegressor(random_state=42)
    
    # Instantiate the random search model
    random_search = RandomizedSearchCV(estimator=rf, param_distributions=param_grid, 
                                       n_iter=100, cv=TimeSeriesSplit(n_splits=3), 
                                       verbose=2, random_state=42, n_jobs=-1)
    
    # Fit the random search model
    random_search.fit(X_train, y_train)
    
    # Get the best model
    best_model = random_search.best_estimator_
    
    # Evaluate on validation set
    y_pred = best_model.predict(X_val)
    mse = mean_squared_error(y_val, y_pred)
    mae = mean_absolute_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)
    
    print(f"Validation MSE: {mse:.2f}")
    print(f"Validation MAE: {mae:.2f}")
    print(f"Validation R2: {r2:.2f}")
    
    return best_model

def predict_wr_fpts(model, player_data):
    return model.predict(player_data)

def visualize_forecast_accuracy(y_true, y_pred, player_data, feature_importance):
    # 1. Actual vs Predicted Scatter Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel('Actual FPTS')
    plt.ylabel('Predicted FPTS')
    plt.title('Actual vs Predicted Fantasy Points')
    plt.tight_layout()
    plt.show()

    # 2. Residual Plot
    residuals = y_true - y_pred
    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predicted FPTS')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.tight_layout()
    plt.show()

    # 3. Distribution of Errors
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, kde=True)
    plt.xlabel('Prediction Error')
    plt.ylabel('Frequency')
    plt.title('Distribution of Prediction Errors')
    plt.tight_layout()
    plt.show()

    # 4. Time Series Plot of Actual vs Predicted for Top Players
    top_players = player_data.groupby('Player')['FPTS'].mean().nlargest(5).index
    plt.figure(figsize=(15, 10))
    for player in top_players:
        player_data_subset = player_data[player_data['Player'] == player].sort_values('Date')
        plt.plot(player_data_subset['Date'], player_data_subset['FPTS'], label=f'{player} (Actual)')
        plt.plot(player_data_subset['Date'], player_data_subset['Predicted_FPTS'], label=f'{player} (Predicted)', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Fantasy Points')
    plt.title('Actual vs Predicted Fantasy Points for Top 5 Players')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 5. Heatmap of Feature Importance
    plt.figure(figsize=(12, 8))
    sns.heatmap(feature_importance.head(20).set_index('feature'), annot=True, cmap='YlOrRd')
    plt.title('Top 20 Feature Importance Heatmap')
    plt.tight_layout()
    plt.show()

    # 6. Error Distribution by Player
    player_errors = player_data.groupby('Player').apply(lambda x: mean_absolute_error(x['FPTS'], x['Predicted_FPTS']))
    plt.figure(figsize=(12, 6))
    sns.boxplot(x=player_errors)
    plt.xlabel('Mean Absolute Error')
    plt.title('Distribution of Prediction Errors by Player')
    plt.tight_layout()
    plt.show()

# Main execution
if __name__ == "__main__":
    start_time = time.time()
    
    base_path = "."  # Adjust this to your actual base path
    print("Loading data...")
    data = load_and_combine_wr_data(base_path)
    
    print("\nExploring raw data:")
    explore_data(data)
    
    print("\nPreprocessing data...")
    processed_data = preprocess_wr_data_for_forecasting(data)
    
    print("\nExploring processed data:")
    explore_data(processed_data)
    
    # Sort data by date
    processed_data = processed_data.sort_values('Date')
    
    # Define train, validation, and test sets
    train_end_date = processed_data['Date'].max() - pd.Timedelta(weeks=8)
    val_end_date = processed_data['Date'].max() - pd.Timedelta(weeks=4)
    
    train_data = processed_data[processed_data['Date'] <= train_end_date]
    val_data = processed_data[(processed_data['Date'] > train_end_date) & (processed_data['Date'] <= val_end_date)]
    test_data = processed_data[processed_data['Date'] > val_end_date]
    
    # Define target and features
    target = 'FPTS'
    features = [col for col in processed_data.columns if col != target and col != 'Player' and col != 'Date' and 'FPTS' not in col and col != 'Rank']
    
    X_train = train_data[features]
    y_train = train_data[target]
    X_val = val_data[features]
    y_val = val_data[target]
    X_test = test_data[features]
    y_test = test_data[target]
    
    print("\nFeatures:")
    for feature in features:
        print(feature)
    print(f"\nTarget: {target}")
    print(f"Train data shape: {X_train.shape}")
    print(f"Validation data shape: {X_val.shape}")
    print(f"Test data shape: {X_test.shape}")
    
    print("\nTraining model...")
    model = train_forecast_model(X_train, y_train, X_val, y_val)
    
    print("\nEvaluating on test set...")
    y_test_pred = model.predict(X_test)
    test_mse = mean_squared_error(y_test, y_test_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    
    print(f"Test MSE: {test_mse:.2f}")
    print(f"Test MAE: {test_mae:.2f}")
    print(f"Test R2: {test_r2:.2f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 20 Most Important Features:")
    print(feature_importance.head(20))
    
    # Example prediction for the next week
    last_week_data = test_data.groupby('Player').last().reset_index()
    next_week_features = last_week_data[features]
    predicted_fpts = predict_wr_fpts(model, next_week_features)
    
    results = pd.DataFrame({
        'Player': last_week_data['Player'],
        'Predicted_FPTS': predicted_fpts
    }).sort_values('Predicted_FPTS', ascending=False)
    
    print("\nTop 10 Predicted FPTS for next week:")
    print(results.head(10))
    
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
    
    # Visualizations
    test_data['Predicted_FPTS'] = y_test_pred
    visualize_forecast_accuracy(y_test, y_test_pred, test_data, feature_importance)