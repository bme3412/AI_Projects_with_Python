"""# Data Requirements and Organization

## Required Data Fields

1. Player Information:
   - player_id (unique identifier for each player)
   - player_name
   - birth_year
   - draft_round
   - draft_pick

2. Season Information:
   - season (year)
   - team
   - offensive_coordinator

3. Game Statistics (per season):
   - games_played
   - games_started
   - passing_yards
   - pass_attempts
   - passing_touchdowns
   - interceptions
   - times_sacked
   - rushing_yards
   - rushing_touchdowns

4. College Statistics:
   - college_games_played
   - college_pass_attempts
   - college_pass_yards
   - college_pass_touchdowns
   - college_interceptions

## Data Organization

Organize your data into a CSV file with each row representing a player's season. The columns should include all the fields mentioned above. Here's a sample structure:

```
player_id,player_name,birth_year,season,team,offensive_coordinator,games_played,games_started,passing_yards,pass_attempts,passing_touchdowns,interceptions,times_sacked,rushing_yards,rushing_touchdowns,draft_round,draft_pick,college_games_played,college_pass_attempts,college_pass_yards,college_pass_touchdowns,college_interceptions
1,John Doe,1995,2018,Team A,Coach X,16,14,3500,500,25,10,30,200,2,1,15,40,1000,8000,70,20
1,John Doe,1995,2019,Team A,Coach X,15,15,3800,520,28,8,25,180,3,1,15,40,1000,8000,70,20
...
```

## Additional Considerations

1. Ensure you have data for each player across multiple seasons (2018-2023) to calculate year-over-year improvements.
2. Include data for all quarterbacks, even if they didn't play in a particular season, to account for career progression.
3. Make sure to have accurate and consistent offensive coordinator information for each season to calculate the 'years_with_current_oc' feature.
4. If possible, include data for rookies entering the league each year, with their college statistics, to enable draft recommendations.

## Data Preprocessing Steps

1. Combine your weekly game logs into season totals for each player.
2. Ensure all required fields are present and have consistent formatting.
3. Handle any missing data appropriately (e.g., fill with zeros or average values where applicable).
4. Verify that player_id is consistent across seasons for the same player.

By organizing your data in this manner, you'll be able to directly feed it into the `load_and_preprocess_data` function in the provided code, which will then perform the necessary transformations and feature engineering."""