import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Finger tip landmark IDs
TIP_IDS = [4, 8, 12, 16, 20]

def detect_fingers(frame):
    """
    Detects a hand in the frame and counts the number of raised fingers.
    Returns the annotated frame and the finger count.
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    finger_count = 0
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            fingers = []
            
            # Thumb (checking x-coordinate relative to the lower joint)
            # Note: This is a simplified check that works best for the right hand
            if hand_landmarks.landmark[TIP_IDS[0]].x < hand_landmarks.landmark[TIP_IDS[0] - 1].x:
                fingers.append(1)
            else:
                fingers.append(0)
                
            # Other 4 fingers (checking y-coordinate relative to corresponding lower joints)
            for i in range(1, 5):
                if hand_landmarks.landmark[TIP_IDS[i]].y < hand_landmarks.landmark[TIP_IDS[i] - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            finger_count = fingers.count(1)
            
    return frame, finger_count

def main():
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
            
        # Detect fingers
        frame, count = detect_fingers(frame)
        
        # Display the finger count on the screen
        cv2.putText(frame, f'Fingers: {count}', (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        cv2.imshow("Hand Gesture Tracker", frame)
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
