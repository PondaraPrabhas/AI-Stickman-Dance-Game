import cv2
import math
import time

class Stickman:
    def __init__(self, position):
        """
        Initialize the stickman.
        position: tuple (x, y) representing the top center of the body (shoulders).
        """
        self.x, self.y = position
        self.state = 'idle'
        self.start_time = time.time()
        
        # Stickman proportions
        self.thickness = 4
        self.head_radius = 35
        self.body_length = 90
        self.arm_length = 65
        self.leg_length = 75
        
        # Neon Color Palette (BGR)
        # Cyan-Teal for idle, Emerald Green for happy, Deep Ocean Blue for sad, Violet for moving
        self.colors = {
            'idle': (220, 220, 0),      # Neon Cyan
            'happy': (50, 220, 50),     # Neon Green
            'sad': (255, 100, 50),      # Neon Deep Blue
            'moving': (180, 50, 255)    # Neon Violet/Pink
        }
        
    def idle(self):
        """Set stickman to idle state."""
        if self.state != 'idle':
            self.state = 'idle'
            self.start_time = time.time()
            
    def happy_dance(self):
        """Set stickman to happy dance state."""
        if self.state != 'happy':
            self.state = 'happy'
            self.start_time = time.time()
            
    def sad_dance(self):
        """Set stickman to sad dance state."""
        if self.state != 'sad':
            self.state = 'sad'
            self.start_time = time.time()
            
    def walk(self):
        """Set stickman to moving/walking state."""
        if self.state != 'moving':
            self.state = 'moving'
            self.start_time = time.time()

    def draw_glow_line(self, frame, pt1, pt2, color, thickness):
        """Draw a line with a neon glow effect."""
        # Outer glow (thick, semi-transparent overlay blend simulated by thick lines)
        cv2.line(frame, pt1, pt2, color, thickness * 4, cv2.LINE_AA)
        cv2.line(frame, pt1, pt2, color, thickness * 2, cv2.LINE_AA)
        # Bright inner core
        cv2.line(frame, pt1, pt2, (255, 255, 255), max(1, thickness // 2), cv2.LINE_AA)

    def draw_glow_circle(self, frame, center, radius, color, thickness):
        """Draw a circle with a neon glow effect."""
        cv2.circle(frame, center, radius, color, thickness * 4, cv2.LINE_AA)
        cv2.circle(frame, center, radius, color, thickness * 2, cv2.LINE_AA)
        cv2.circle(frame, center, radius, (255, 255, 255), max(1, thickness // 2), cv2.LINE_AA)

    def draw_glow_arc(self, frame, center, axes, angle, startAngle, endAngle, color, thickness):
        """Draw an arc with a neon glow effect."""
        cv2.ellipse(frame, center, axes, angle, startAngle, endAngle, color, thickness * 2, cv2.LINE_AA)
        cv2.ellipse(frame, center, axes, angle, startAngle, endAngle, (255, 255, 255), max(1, thickness // 2), cv2.LINE_AA)

    def draw(self, frame):
        """Draw the animated stickman on the given OpenCV frame."""
        t = time.time() - self.start_time
        color = self.colors.get(self.state, (255, 255, 255))
        
        # Base body anchors
        head_center = (self.x, self.y - self.head_radius)
        shoulder = (self.x, self.y)
        pelvis = (self.x, self.y + self.body_length)
        
        # Default angles (radians)
        left_arm_angle = math.pi * 0.75   # Down-Left
        right_arm_angle = math.pi * 0.25  # Down-Right
        left_leg_angle = math.pi * 0.70   # Down-Left
        right_leg_angle = math.pi * 0.30  # Down-Right
        
        # Animation & Joint positioning based on state
        if self.state == 'happy':
            # Wave arms up and down fast
            left_arm_angle = math.pi * 1.3 + math.sin(t * 18) * 0.4
            right_arm_angle = math.pi * 1.7 - math.sin(t * 18) * 0.4
            
            # Jump up and down dynamically
            jump_offset = int(abs(math.sin(t * 12)) * 30)
            head_center = (self.x, self.y - self.head_radius - jump_offset)
            shoulder = (self.x, self.y - jump_offset)
            pelvis = (self.x, self.y + self.body_length - jump_offset)
            
            # Legs move out and in as jumping
            left_leg_angle = math.pi * 0.75 + math.sin(t * 12) * 0.25
            right_leg_angle = math.pi * 0.25 - math.sin(t * 12) * 0.25
            
        elif self.state == 'sad':
            # Droop head lower
            head_center = (self.x, self.y - self.head_radius + 15)
            # Body slumps forward slightly
            shoulder = (self.x - 5, self.y + 5)
            
            # Arms hang down limp, swaying slowly
            left_arm_angle = math.pi * 0.55 + math.sin(t * 2.5) * 0.08
            right_arm_angle = math.pi * 0.45 - math.sin(t * 2.5) * 0.08
            
            # Legs static, slightly bent inwards
            left_leg_angle = math.pi * 0.65
            right_leg_angle = math.pi * 0.35
            
        elif self.state == 'moving':
            # Walk cycle animation
            walk_speed = 10
            # Legs swing back and forth
            left_leg_angle = math.pi * 0.5 + math.sin(t * walk_speed) * 0.35
            right_leg_angle = math.pi * 0.5 - math.sin(t * walk_speed) * 0.35
            
            # Arms swing in opposite phase
            left_arm_angle = math.pi * 0.5 - math.sin(t * walk_speed) * 0.25
            right_arm_angle = math.pi * 0.5 + math.sin(t * walk_speed) * 0.25
            
            # Body bobs up and down
            bob_offset = int(abs(math.sin(t * walk_speed * 2)) * 8)
            head_center = (self.x, self.y - self.head_radius - bob_offset)
            shoulder = (self.x, self.y - bob_offset)
            pelvis = (self.x, self.y + self.body_length - bob_offset)
            
        else: # idle
            # Gentle breathing sway
            breath = math.sin(t * 3.5)
            left_arm_angle = math.pi * 0.75 + breath * 0.06
            right_arm_angle = math.pi * 0.25 - breath * 0.06
            
            shoulder = (self.x, self.y + int(breath * 3))
            head_center = (self.x, self.y - self.head_radius + int(breath * 1.5))
            
            left_leg_angle = math.pi * 0.70
            right_leg_angle = math.pi * 0.30

        # Calculate joint endpoints using trigonometry
        left_hand = (
            int(shoulder[0] + self.arm_length * math.cos(left_arm_angle)),
            int(shoulder[1] + self.arm_length * math.sin(left_arm_angle))
        )
        right_hand = (
            int(shoulder[0] + self.arm_length * math.cos(right_arm_angle)),
            int(shoulder[1] + self.arm_length * math.sin(right_arm_angle))
        )
        
        left_foot = (
            int(pelvis[0] + self.leg_length * math.cos(left_leg_angle)),
            int(pelvis[1] + self.leg_length * math.sin(left_leg_angle))
        )
        right_foot = (
            int(pelvis[0] + self.leg_length * math.cos(right_leg_angle)),
            int(pelvis[1] + self.leg_length * math.sin(right_leg_angle))
        )
        
        # --- Drawing the Stickman ---
        # Body Link
        self.draw_glow_line(frame, shoulder, pelvis, color, self.thickness)
        # Arms
        self.draw_glow_line(frame, shoulder, left_hand, color, self.thickness)
        self.draw_glow_line(frame, shoulder, right_hand, color, self.thickness)
        # Legs
        self.draw_glow_line(frame, pelvis, left_foot, color, self.thickness)
        self.draw_glow_line(frame, pelvis, right_foot, color, self.thickness)
        # Head Outer Outline
        self.draw_glow_circle(frame, head_center, self.head_radius, color, self.thickness)
        
        # --- Drawing Facial Expressions ---
        hc_x, hc_y = head_center
        face_thick = max(1, self.thickness // 2)
        
        if self.state == 'happy':
            # Smiling eyes (arcs curving up)
            self.draw_glow_arc(frame, (hc_x - 11, hc_y - 6), (5, 4), 0, 180, 360, color, face_thick)
            self.draw_glow_arc(frame, (hc_x + 11, hc_y - 6), (5, 4), 0, 180, 360, color, face_thick)
            # Big open smile (U-shape)
            self.draw_glow_arc(frame, (hc_x, hc_y + 8), (14, 9), 0, 0, 180, color, face_thick)
            
        elif self.state == 'sad':
            # Downward slanted eyes
            # Left: \ , Right: /
            self.draw_glow_line(frame, (hc_x - 15, hc_y - 10), (hc_x - 7, hc_y - 5), color, face_thick)
            self.draw_glow_line(frame, (hc_x + 15, hc_y - 10), (hc_x + 7, hc_y - 5), color, face_thick)
            # Frown (Inverted U-shape)
            self.draw_glow_arc(frame, (hc_x, hc_y + 14), (10, 6), 0, 180, 360, color, face_thick)
            # Teardrop on the left side
            tear_y = hc_y + int(t * 15) % 15
            if tear_y < hc_y + 16:
                cv2.circle(frame, (hc_x - 9, tear_y), 2, (255, 200, 50), -1, cv2.LINE_AA) # Blue-ish tear BGR
            
        elif self.state == 'moving':
            # Focused eyes looking right
            cv2.circle(frame, (hc_x - 7, hc_y - 6), 3, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (hc_x + 11, hc_y - 6), 3, (255, 255, 255), -1, cv2.LINE_AA)
            # Small cute whistling/determined mouth (circle)
            cv2.circle(frame, (hc_x + 4, hc_y + 8), 4, color, face_thick, cv2.LINE_AA)
            
        else: # idle
            # Simple relaxed eyes
            self.draw_glow_line(frame, (hc_x - 13, hc_y - 6), (hc_x - 7, hc_y - 6), color, face_thick)
            self.draw_glow_line(frame, (hc_x + 7, hc_y - 6), (hc_x + 13, hc_y - 6), color, face_thick)
            # Gentle smile
            self.draw_glow_arc(frame, (hc_x, hc_y + 6), (8, 4), 0, 0, 180, color, face_thick)
