# Basketball Tracking Project

This project uses computer vision techniques to track players and the ball in basketball game videos. It employs the YOLO (You Only Look Once) object detection system to identify players and the ball, and then tracks their movements and interactions throughout the game.

## Features

- Player detection and tracking
- Ball tracking
- Team assignment based on jersey colors
- Speed calculation for players
- Last ball possession tracking

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6+
- OpenCV
- NumPy
- scikit-learn
- yt-dlp
- YOLO v3 weights file (not included in this repository)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/bme3412/AI_Projects_with_Python/basketball-tracking.git
   cd basketball-tracking
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the YOLO v3 weights file and place it in the project directory. You can download it from the official YOLO website or use a pre-trained weights file compatible with the configuration in this project.

## Usage

1. Run the script:
   ```
   python basketball_tracking.py
   ```

2. When prompted, enter the URL of a YouTube video containing a basketball game.

3. The script will process the video and display the tracking results in real-time.

4. Press 'q' to quit the video playback.

## How it Works

1. The script downloads the specified YouTube video.
2. It uses YOLO to detect players and the ball in each frame.
3. Players are assigned to teams based on the dominant colors of their jerseys.
4. The script tracks the movement of players and calculates their speeds.
5. It determines which player is closest to the ball and tracks the last team to possess the ball.
6. All this information is overlaid on the video in real-time.

## Contributing

Contributions to this project are welcome. Please fork the repository and create a pull request with your changes.

## License

[Specify your license here, e.g., MIT, GPL, etc.]

## Contact

If you have any questions or feedback, please contact [Your Name] at [your email].

## Acknowledgements

- YOLO (You Only Look Once) for object detection
- OpenCV for image processing
- yt-dlp for YouTube video downloading