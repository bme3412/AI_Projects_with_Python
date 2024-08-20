import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    # Calculate fantasy points
    df['fantasy_points'] = (
        df['passing_yards'] * 0.04 +
        df['passing_touchdowns'] * 4 +
        df['interceptions'] * -2 +
        df['rushing_yards'] * 0.1 +
        df['rushing_touchdowns'] * 6
    )
    df['fantasy_points_per_game'] = df['fantasy_points'] / df['games_played']
    
    # Calculate year-over-year fantasy point changes
    df['prev_year_fantasy_points'] = df.groupby('player_id')['fantasy_points'].shift(1)
    df['fantasy_points_change'] = df['fantasy_points'] - df['prev_year_fantasy_points']
    df['fantasy_points_change_pct'] = df['fantasy_points_change'] / df['prev_year_fantasy_points']
    
    # Identify "down years"
    df['down_year'] = (df['fantasy_points_change_pct'] < -0.1) & (df['games_played'] >= 8)
    
    # Create other relevant features
    df['age'] = df['season'] - df['birth_year']
    df['yards_per_attempt'] = df['passing_yards'] / df['pass_attempts']
    df['touchdown_ratio'] = df['passing_touchdowns'] / df['pass_attempts']
    df['interception_ratio'] = df['interceptions'] / df['pass_attempts']
    
    return df

def engineer_features(df):
    features = [
        'age', 'games_played', 'yards_per_attempt', 'touchdown_ratio', 'interception_ratio',
        'rushing_yards', 'rushing_touchdowns', 'times_sacked', 'down_year',
        'fantasy_points_change', 'fantasy_points_change_pct', 'prev_year_fantasy_points'
    ]
    
    X = df[features]
    y = df['fantasy_points_per_game']
    
    return X, y

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance - MSE: {mse:.2f}, R2: {r2:.2f}")
    
    return model, scaler

def analyze_comeback_potential(df, model, scaler):
    # Focus on QBs coming off a down year
    comeback_candidates = df[df['down_year'].shift(1) == True]
    
    X_comeback = engineer_features(comeback_candidates)[0]
    X_comeback_scaled = scaler.transform(X_comeback)
    
    comeback_candidates['predicted_fantasy_points'] = model.predict(X_comeback_scaled)
    comeback_candidates['predicted_improvement'] = comeback_candidates['predicted_fantasy_points'] - comeback_candidates['prev_year_fantasy_points']
    
    # Analyze actual vs predicted improvement
    comeback_analysis = comeback_candidates.groupby('season').agg({
        'fantasy_points_per_game': 'mean',
        'predicted_fantasy_points': 'mean',
        'fantasy_points_change': 'mean',
        'predicted_improvement': 'mean'
    })
    
    print("Comeback Potential Analysis:")
    print(comeback_analysis)
    
    return comeback_candidates

def get_draft_recommendations(df, model, scaler, top_n=10):
    current_season = df['season'].max() + 1
    potential_comebacks = df[(df['season'] == current_season - 1) & (df['down_year'] == True)]
    
    X_potential = engineer_features(potential_comebacks)[0]
    X_potential_scaled = scaler.transform(X_potential)
    
    potential_comebacks['predicted_fantasy_points'] = model.predict(X_potential_scaled)
    potential_comebacks['predicted_improvement'] = potential_comebacks['predicted_fantasy_points'] - potential_comebacks['fantasy_points_per_game']
    
    top_recommendations = potential_comebacks.nlargest(top_n, 'predicted_improvement')
    
    print(f"\nTop {top_n} Comeback QB Draft Recommendations:")
    print(top_recommendations[['player_name', 'team', 'fantasy_points_per_game', 'predicted_fantasy_points', 'predicted_improvement']])

def feature_importance(model, feature_names):
    importances = model.feature_importances_
    feature_importance = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    
    print("\nFeature Importance:")
    for feature, importance in feature_importance:
        print(f"{feature}: {importance:.4f}")

# Main execution
if __name__ == "__main__":
    file_path = "path_to_your_data.csv"
    df = load_and_preprocess_data(file_path)
    X, y = engineer_features(df)
    model, scaler = train_model(X, y)
    comeback_candidates = analyze_comeback_potential(df, model, scaler)
    get_draft_recommendations(df, model, scaler)
    feature_importance(model, X.columns)