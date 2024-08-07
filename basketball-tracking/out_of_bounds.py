import sys
import subprocess

def install_required_libraries():
    required_libraries = ['opencv-python', 'numpy', 'scikit-learn', 'yt-dlp']
    for library in required_libraries:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])
            print(f"Successfully installed {library}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {library}. Please install it manually.")
            sys.exit(1)

try:
    import cv2
    import numpy as np
    from sklearn.cluster import KMeans
except ImportError:
    print("Some required libraries are missing. Attempting to install them...")
    install_required_libraries()
    try:
        import cv2
        import numpy as np
        from sklearn.cluster import KMeans
    except ImportError:
        print("Failed to import required libraries even after installation attempt. Please check your Python environment.")
        sys.exit(1)

from collections import defaultdict

def download_youtube_video(url):
    try:
        result = subprocess.run(['yt-dlp', '--verbose', '-f', 'best', '-g', url], capture_output=True, text=True, check=True)
        video_url = result.stdout.strip()
        return video_url
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to get the video URL: {e}")
        print(f"Error output: {e.stderr}")
        return None

def apply_yolo(frame, net, output_layers, classes):
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    return boxes, class_ids, confidences

def calculate_speed(prev_pos, curr_pos, fps, pixels_per_meter):
    if prev_pos is None:
        return 0
    distance = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
    distance_meters = distance / pixels_per_meter
    speed = distance_meters * fps  # meters per second
    return speed

def get_dominant_colors(frame, n_colors=2):
    pixels = frame.reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_colors, n_init=10)
    kmeans.fit(pixels)
    return kmeans.cluster_centers_

def assign_team(player_color, team_colors):
    distances = [np.linalg.norm(player_color - team_color) for team_color in team_colors]
    return np.argmin(distances)

def main():
    url = input("Please enter the YouTube video URL: ")
    video_url = download_youtube_video(url)
    
    if video_url is None:
        print("Failed to retrieve video URL. Exiting.")
        return

    try:
        net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        with open("coco.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except Exception as e:
        print(f"Error loading YOLO files: {str(e)}")
        print("Make sure you have yolov3.weights, yolov3.cfg, and coco.names in the same directory as this script.")
        return

    cap = cv2.VideoCapture(video_url)
    if not cap.isOpened():
        print("Error opening video stream")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    # Estimate pixels per meter (assuming court width is about 28 meters)
    pixels_per_meter = frame_width / 28

    player_positions = defaultdict(lambda: None)
    player_speeds = defaultdict(float)
    player_teams = {}
    last_ball_possession = None
    frame_count = 0

    # Get team colors from the first frame
    ret, first_frame = cap.read()
    if not ret:
        print("Failed to read the first frame")
        return
    team_colors = get_dominant_colors(first_frame)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        boxes, class_ids, confidences = apply_yolo(frame, net, output_layers, classes)
        
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        ball_position = None
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                if label == 'person':
                    player_id = i  # Simple player ID based on detection order
                    center = (x + w // 2, y + h // 2)
                    
                    # Calculate speed
                    speed = calculate_speed(player_positions[player_id], center, fps, pixels_per_meter)
                    player_speeds[player_id] = speed
                    player_positions[player_id] = center

                    # Assign team based on jersey color
                    if player_id not in player_teams:
                        player_color = frame[y:y+h, x:x+w].mean(axis=(0, 1))
                        player_teams[player_id] = assign_team(player_color, team_colors)

                    team = player_teams[player_id]
                    color = (0, 255, 0) if team == 0 else (255, 0, 0)

                    # Draw bounding box and label
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"Player {player_id} (Team {team}): {speed:.2f} m/s", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                elif label == 'sports ball':
                    # Highlight the ball
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, "Ball", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
                    ball_position = (x + w // 2, y + h // 2)
                    
        if ball_position:
            # Find closest player to the ball
            closest_player = min(player_positions.items(), 
                                 key=lambda x: np.sqrt((x[1][0] - ball_position[0])**2 + 
                                                       (x[1][1] - ball_position[1])**2) 
                                 if x[1] is not None else float('inf'))
            
            # Update last ball possession if the closest player is within a certain distance
            distance_to_ball = np.sqrt((closest_player[1][0] - ball_position[0])**2 + 
                                       (closest_player[1][1] - ball_position[1])**2)
            if distance_to_ball < 50:  # Adjust this threshold as needed
                last_ball_possession = closest_player[0]

            cv2.putText(frame, f"Closest: Player {closest_player[0]} (Team {player_teams[closest_player[0]]})", 
                        (ball_position[0], ball_position[1] + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            if last_ball_possession is not None:
                cv2.putText(frame, f"Last touched: Team {player_teams[last_ball_possession]}", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Basketball Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()