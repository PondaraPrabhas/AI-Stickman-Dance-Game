import cv2
import sys
import time
import threading
import nlp_module
import gesture_module
import stickman_module
import mediapipe as mp

# Shared variables between threads
lock = threading.Lock()
latest_frame = None
finger_count = 0
hand_landmarks_data = None
running = True
dance_style = 'normal'
config_overrides = {}  # Dynamic overrides for stickman dimensions/thickness

def gesture_worker():
    """Background thread to process hand tracking using MediaPipe."""
    global latest_frame, finger_count, hand_landmarks_data, running
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    TIP_IDS = [4, 8, 12, 16, 20]
    
    while running:
        frame_to_process = None
        with lock:
            if latest_frame is not None:
                frame_to_process = latest_frame.copy()
                
        if frame_to_process is not None:
            frame_rgb = cv2.cvtColor(frame_to_process, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            
            local_finger_count = 0
            local_landmarks = None
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    local_landmarks = hand_landmarks
                    
                    fingers = []
                    # Thumb (relative check working for flipped selfie view)
                    if hand_landmarks.landmark[TIP_IDS[0]].x < hand_landmarks.landmark[TIP_IDS[0] - 1].x:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                        
                    # 4 Fingers (checking y relative to joint below)
                    for i in range(1, 5):
                        if hand_landmarks.landmark[TIP_IDS[i]].y < hand_landmarks.landmark[TIP_IDS[i] - 2].y:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                            
                    local_finger_count = fingers.count(1)
            
            with lock:
                finger_count = local_finger_count
                hand_landmarks_data = local_landmarks
                
        time.sleep(0.01)

def stdin_worker():
    """Thread to read dynamic mood updates and parameter overrides from stdin."""
    global dance_style, running, config_overrides
    while running:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            text = line.strip()
            if text:
                if text.startswith("CFG:"):
                    parts = text.split(":")
                    if len(parts) == 3:
                        param_name = parts[1]
                        try:
                            param_val = float(parts[2])
                            with lock:
                                config_overrides[param_name] = param_val
                                print(f"SYS_CONFIG:{param_name.upper()}={param_val}", flush=True)
                        except ValueError:
                            pass
                else:
                    new_style = nlp_module.get_dance_style(text)
                    with lock:
                        dance_style = new_style
                        print(f"MOOD_UPDATE:{dance_style.upper()}", flush=True)
        except Exception:
            break

def draw_hud(frame, fps, finger_count, dance_style):
    """Draw a futuristic high-tech telemetry HUD overlay."""
    h, w, _ = frame.shape
    
    # 1. Semi-transparent black banner
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 105), (20, 20, 30), -1)
    alpha = 0.75
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # 2. Determine state color
    hud_color = (220, 220, 0)      # Cyan for idle/normal
    if dance_style == 'happy':
        hud_color = (50, 220, 50)   # Neon Green
    elif dance_style == 'sad':
        hud_color = (255, 100, 50)  # Neon Blue
    
    if finger_count == 2:
        hud_color = (180, 50, 255)  # Neon Violet (moving)
        
    cv2.line(frame, (0, 105), (w, 105), hud_color, 2, cv2.LINE_AA)
    
    # 3. Left Panel - Console Brand & Status
    cv2.putText(frame, "AI STICKMAN DANCE CONSOLE", (20, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "SYS STATUS: ACTIVE / TRACKING", (20, 65), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 255, 80), 1, cv2.LINE_AA)
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 85), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
    
    # Separator 1
    cv2.line(frame, (w // 3 + 20, 15), (w // 3 + 20, 90), (80, 80, 80), 1, cv2.LINE_AA)
    
    # 4. Middle Panel - Gesture Information
    cv2.putText(frame, "GESTURE INPUT", (w // 3 + 40, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, f"Fingers Detected: {finger_count}", (w // 3 + 40, 55), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, hud_color, 2, cv2.LINE_AA)
    
    state_desc = "STANDBY"
    if finger_count == 1:
        state_desc = "IDLE ANIMATION"
    elif finger_count == 2:
        state_desc = "WALKING RIGHT"
    elif finger_count > 0:
        state_desc = "DANCING"
    cv2.putText(frame, f"Action: {state_desc}", (w // 3 + 40, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)
                
    # Separator 2
    cv2.line(frame, (2 * w // 3 + 20, 15), (2 * w // 3 + 20, 90), (80, 80, 80), 1, cv2.LINE_AA)
    
    # 5. Right Panel - NLP Sentiment Analysis
    cv2.putText(frame, "NLP SENTIMENT ANALYZER", (2 * w // 3 + 40, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)
    
    mood_str = "NORMAL (NEUTRAL)"
    if dance_style == 'happy':
        mood_str = "HAPPY (POSITIVE)"
    elif dance_style == 'sad':
        mood_str = "SAD (NEGATIVE)"
        
    cv2.putText(frame, mood_str, (2 * w // 3 + 40, 55), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, hud_color, 2, cv2.LINE_AA)
    cv2.putText(frame, "Source: Dynamic Stdin", (2 * w // 3 + 40, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)

def main():
    global latest_frame, finger_count, hand_landmarks_data, running, dance_style, config_overrides
    
    print("SYS_START: Stickman background process ready.", flush=True)
    
    # Wait for the initial mood text from stdin
    try:
        initial_text = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        return
        
    if not initial_text:
        initial_text = "happy"
        
    dance_style = nlp_module.get_dance_style(initial_text)
    print(f"MOOD_INITIAL:{dance_style.upper()}", flush=True)
    
    # Start background threads
    threading.Thread(target=stdin_worker, daemon=True).start()
    threading.Thread(target=gesture_worker, daemon=True).start()
    
    # Initialize stickman at center-bottom
    stickman = stickman_module.Stickman((320, 240))
    
    cap = cv2.VideoCapture(0)
    
    prev_time = time.time()
    fps = 0
    frame_count = 0
    
    # Setup windows and graphics
    cv2.namedWindow('AI Stickman Dance Console', cv2.WINDOW_AUTOSIZE)
    
    while cap.isOpened() and running:
        success, frame = cap.read()
        if not success:
            time.sleep(0.01)
            continue
            
        # Flip frame horizontally for selfie view
        frame = cv2.flip(frame, 1)
        
        # Share frame with background gesture thread and load configurations
        with lock:
            latest_frame = frame.copy()
            local_finger_count = finger_count
            local_landmarks = hand_landmarks_data
            local_dance_style = dance_style
            
            # Apply dynamic config overrides
            if 'thickness' in config_overrides:
                stickman.thickness = int(config_overrides['thickness'])
            if 'head_radius' in config_overrides:
                stickman.head_radius = int(config_overrides['head_radius'])
            if 'body_length' in config_overrides:
                stickman.body_length = int(config_overrides['body_length'])
            if 'arm_length' in config_overrides:
                stickman.arm_length = int(config_overrides['arm_length'])
            if 'leg_length' in config_overrides:
                stickman.leg_length = int(config_overrides['leg_length'])
            
        # Update stickman movement/animation state
        if local_finger_count == 1:
            stickman.idle()
        elif local_finger_count == 2:
            stickman.walk()
            # Walk right, loop around borders
            stickman.x += 7
            if stickman.x > frame.shape[1] + 50:
                stickman.x = -50
        else:
            if local_dance_style == 'happy':
                stickman.happy_dance()
            elif local_dance_style == 'sad':
                stickman.sad_dance()
            else:
                stickman.idle()
                
        # Draw MediaPipe hands landmarks if available
        if local_landmarks is not None:
            mp_hands = mp.solutions.hands
            mp_draw = mp.solutions.drawing_utils
            mp_draw.draw_landmarks(
                frame, 
                local_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1)
            )
            
        # Render stickman with glows & facial expressions
        stickman.draw(frame)
        
        # FPS Counter logic
        frame_count += 1
        curr_time = time.time()
        elapsed = curr_time - prev_time
        if elapsed >= 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            prev_time = curr_time
            
        # Draw HUD overlays
        draw_hud(frame, fps, local_finger_count, local_dance_style)
        
        # Display the visual window
        cv2.imshow('AI Stickman Dance Console', frame)
        
        # Read exit command from window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("SYS_QUIT: User closed console.", flush=True)
            break
            
    running = False
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
