import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# 1. Data Collection and Preprocessing
def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    # Identify QBs in their second year as a starter
    df['is_second_year_starter'] = (df['years_as_starter'] == 2)
    
    # Create features
    df['age'] = df['season'] - df['birth_year']
    df['games_started_ratio'] = df['games_started'] / df['games_played']
    df['yards_per_attempt'] = df['passing_yards'] / df['pass_attempts']
    df['touchdown_ratio'] = df['passing_touchdowns'] / df['pass_attempts']
    df['interception_ratio'] = df['interceptions'] / df['pass_attempts']
    df['sack_ratio'] = df['times_sacked'] / (df['pass_attempts'] + df['times_sacked'])
    
    # Calculate year-over-year improvements
    df['yoy_completion_pct'] = df.groupby('player_id')['completion_percentage'].pct_change()
    df['yoy_yards_per_game'] = df.groupby('player_id')['passing_yards_per_game'].pct_change()
    df['yoy_td_ratio'] = df.groupby('player_id')['touchdown_ratio'].pct_change()
    
    # Team continuity features
    df['same_team'] = df.groupby('player_id')['team'].transform(lambda x: x == x.shift())
    df['same_coach'] = df.groupby('player_id')['head_coach'].transform(lambda x: x == x.shift())
    
    # Target variable: Fantasy points per game
    df['fantasy_points_per_game'] = (
        df['passing_yards'] * 0.04 +
        df['passing_touchdowns'] * 4 +
        df['interceptions'] * -2 +
        df['rushing_yards'] * 0.1 +
        df['rushing_touchdowns'] * 6
    ) / df['games_played']
    
    return df

# 2. Feature Engineering
def engineer_features(df):
    features = [
        'age', 'games_started_ratio', 'yards_per_attempt', 'touchdown_ratio',
        'interception_ratio', 'sack_ratio', 'yoy_completion_pct', 'yoy_yards_per_game',
        'yoy_td_ratio', 'same_team', 'same_coach', 'draft_round', 'draft_pick',
        'college_games_played', 'college_pass_attempts', 'college_pass_yards',
        'college_pass_touchdowns', 'college_interceptions'
    ]
    
    X = df[features]
    y = df['fantasy_points_per_game']
    
    return X, y

# 3. Model Training
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

# 4. Sophomore Surge Analysis
def analyze_sophomore_surge(df, model, scaler):
    second_year_qbs = df[df['is_second_year_starter']]
    X_second_year = engineer_features(second_year_qbs)[0]
    X_second_year_scaled = scaler.transform(X_second_year)
    
    predictions = model.predict(X_second_year_scaled)
    second_year_qbs['predicted_fantasy_points'] = predictions
    
    surge_analysis = second_year_qbs.groupby('season').agg({
        'fantasy_points_per_game': 'mean',
        'predicted_fantasy_points': 'mean'
    })
    surge_analysis['actual_vs_predicted'] = surge_analysis['fantasy_points_per_game'] - surge_analysis['predicted_fantasy_points']
    
    print("Sophomore Surge Analysis:")
    print(surge_analysis)
    
    return second_year_qbs

# 5. Draft Recommendations
def get_draft_recommendations(df, model, scaler, top_n=10):
    current_season = df['season'].max() + 1
    potential_second_year_starters = df[
        (df['season'] == current_season - 1) & 
        (df['years_as_starter'] == 1)
    ]
    
    X_potential = engineer_features(potential_second_year_starters)[0]
    X_potential_scaled = scaler.transform(X_potential)
    
    predictions = model.predict(X_potential_scaled)
    potential_second_year_starters['predicted_fantasy_points'] = predictions
    
    top_recommendations = potential_second_year_starters.nlargest(top_n, 'predicted_fantasy_points')
    
    print(f"\nTop {top_n} QB Draft Recommendations:")
    print(top_recommendations[['player_name', 'team', 'predicted_fantasy_points']])

# Main execution
if __name__ == "__main__":
    file_path = "path_to_your_data.csv"
    df = load_and_preprocess_data(file_path)
    X, y = engineer_features(df)
    model, scaler = train_model(X, y)
    second_year_qbs = analyze_sophomore_surge(df, model, scaler)
    get_draft_recommendations(df, model, scaler)