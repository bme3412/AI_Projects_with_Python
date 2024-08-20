import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    # Calculate years with current offensive coordinator
    df['years_with_current_oc'] = df.groupby(['player_id', 'offensive_coordinator'])['season'].transform('count')
    
    # Create stability flag
    df['stability_flag'] = (df['years_with_current_oc'] >= 3)
    
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
    
    # Target variable: Fantasy points per game
    df['fantasy_points_per_game'] = (
        df['passing_yards'] * 0.04 +
        df['passing_touchdowns'] * 4 +
        df['interceptions'] * -2 +
        df['rushing_yards'] * 0.1 +
        df['rushing_touchdowns'] * 6
    ) / df['games_played']
    
    return df

def engineer_features(df):
    features = [
        'age', 'games_started_ratio', 'yards_per_attempt', 'touchdown_ratio',
        'interception_ratio', 'sack_ratio', 'yoy_completion_pct', 'yoy_yards_per_game',
        'yoy_td_ratio', 'years_with_current_oc', 'stability_flag', 'draft_round', 
        'draft_pick', 'college_games_played', 'college_pass_attempts', 
        'college_pass_yards', 'college_pass_touchdowns', 'college_interceptions'
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

def analyze_stability_impact(df, model, scaler):
    X, y = engineer_features(df)
    X_scaled = scaler.transform(X)
    
    df['predicted_fantasy_points'] = model.predict(X_scaled)
    
    stability_analysis = df.groupby('stability_flag').agg({
        'fantasy_points_per_game': 'mean',
        'predicted_fantasy_points': 'mean'
    })
    stability_analysis['actual_vs_predicted'] = stability_analysis['fantasy_points_per_game'] - stability_analysis['predicted_fantasy_points']
    
    print("Stability Impact Analysis:")
    print(stability_analysis)
    
    # Analyze performance by years with current OC
    years_analysis = df.groupby('years_with_current_oc').agg({
        'fantasy_points_per_game': 'mean',
        'predicted_fantasy_points': 'mean'
    })
    years_analysis['actual_vs_predicted'] = years_analysis['fantasy_points_per_game'] - years_analysis['predicted_fantasy_points']
    
    print("\nPerformance by Years with Current OC:")
    print(years_analysis)
    
    return df

def get_draft_recommendations(df, model, scaler, top_n=10):
    current_season = df['season'].max() + 1
    potential_targets = df[df['season'] == current_season - 1]
    
    X_potential = engineer_features(potential_targets)[0]
    X_potential_scaled = scaler.transform(X_potential)
    
    predictions = model.predict(X_potential_scaled)
    potential_targets['predicted_fantasy_points'] = predictions
    
    top_recommendations = potential_targets.nlargest(top_n, 'predicted_fantasy_points')
    
    print(f"\nTop {top_n} QB Draft Recommendations:")
    print(top_recommendations[['player_name', 'team', 'years_with_current_oc', 'predicted_fantasy_points']])

    # Highlight stable QBs
    stable_qbs = top_recommendations[top_recommendations['stability_flag']]
    print(f"\nStable QBs (3+ years with current OC) among top recommendations:")
    print(stable_qbs[['player_name', 'team', 'years_with_current_oc', 'predicted_fantasy_points']])

# Main execution
if __name__ == "__main__":
    file_path = "path_to_your_data.csv"
    df = load_and_preprocess_data(file_path)
    X, y = engineer_features(df)
    model, scaler = train_model(X, y)
    df_with_predictions = analyze_stability_impact(df, model, scaler)
    get_draft_recommendations(df_with_predictions, model, scaler)