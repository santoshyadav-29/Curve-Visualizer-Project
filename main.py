import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60

# App Pages
PAGES = ["START", "INFO", "MAIN_APP"]
current_page = 0

# Curve Data
# For curves that use "a" and "b" (Ellipse, Parabola, Hyperbola),
# these parameters will be reinterpreted accordingly.
current_curve = "Circle"
curve_params = {"radius": 0.5, "a": 1, "b": 0.5}  # Use a and b for Ellipse, Parabola, Hyperbola
curve_facts = {
    "Circle": "A circle is all points equidistant from its center (radius = {radius:.2f}).",
    "Parabola": "A parabola: y = {a:.2f}x² + {b:.2f}",
    "Ellipse": "An ellipse: (x/{a:.2f})² + (y/{b:.2f})² = 1",
    "Hyperbola": "A hyperbola: (x/{a:.2f})² - (y/{b:.2f})² = 1"
}

# Refined Color Palette (RGBA)
COLOR_BG         = (0.12, 0.12, 0.16, 1)
COLOR_PANEL      = (0.18, 0.18, 0.22, 1)
COLOR_ACCENT     = (0.26, 0.59, 0.98, 1)
COLOR_TEXT       = (0.9, 0.9, 0.9, 1)
COLOR_HIGHLIGHT  = (0.32, 0.64, 1.0, 1)
COLOR_BUTTON     = (0.2, 0.2, 0.3, 1)
COLOR_BUTTON_HOV = (0.3, 0.3, 0.4, 1)

# UI State
active_slider = None
font = None

def init():
    global font
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Math Curves Visualizer")
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    # Use a system font (change "Arial" to your preferred font)
    font = pygame.font.SysFont("Arial", 24, bold=True)

def draw_text_vp(text, x, y, font_size=24, color=COLOR_TEXT):
    """
    Draws text using glRasterPos2f in the current projection.
    This function assumes that the current projection has been set up
    to match the viewport (for example, with gluOrtho2D) and that the
    coordinate system uses the top-left as (0,0).
    """
    text_surface = font.render(text, True, (int(color[0]*255),
                                              int(color[1]*255),
                                              int(color[2]*255)))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()
    glRasterPos2f(x, y + text_height)  # Note: Adjust y so text appears correctly
    glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_button(x, y, w, h, text, base_color, hover=False):
    # Button background
    color = base_color if not hover else COLOR_BUTTON_HOV
    glColor4f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
    
    # Button border
    glColor4f(*COLOR_ACCENT)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
    
    # Center the text within the button.
    text_surface = font.render(text, True, (int(COLOR_TEXT[0]*255),
                                              int(COLOR_TEXT[1]*255),
                                              int(COLOR_TEXT[2]*255)))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()
    text_x = x + (w - text_width) / 2
    text_y = y + (h - text_height) / 2
    glRasterPos2f(text_x, text_y + text_height)
    glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_slider(x, y, w, h, value, min_val, max_val, label):
    global active_slider
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # Constrain value within [min_val, max_val]
    value = max(min_val, min(max_val, value))
    
    # Draw slider track (as a panel)
    glColor4f(*COLOR_PANEL)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
    
    # Compute thumb position (relative to slider width)
    thumb_pos = (value - min_val) / (max_val - min_val)
    thumb_x = x + thumb_pos * w
    thumb_width = 12
    thumb_x = max(x, min(x + w - thumb_width, thumb_x))
    
    # Draw slider thumb
    glColor4f(*COLOR_ACCENT)
    glBegin(GL_QUADS)
    glVertex2f(thumb_x, y - 4)
    glVertex2f(thumb_x + thumb_width, y - 4)
    glVertex2f(thumb_x + thumb_width, y + h + 4)
    glVertex2f(thumb_x, y + h + 4)
    glEnd()
    
    # Draw label and current value using draw_text_vp.
    label_text = f"{label}: {value:.2f}"
    draw_text_vp(label_text, x, y - 30, 20, COLOR_TEXT)
    
    # Handle dragging if mouse is pressed
    if pygame.mouse.get_pressed()[0]:
        # In a viewport setup, the mouse coordinates might need conversion.
        if x <= mouse_x <= x + w and y - 10 <= mouse_y <= y + h + 10:
            active_slider = label
            new_val = (mouse_x - x) / w * (max_val - min_val) + min_val
            # Use the first word of the label (e.g., "Radius", "A", "B") as the key.
            curve_params[label.split()[0].lower()] = max(min_val, min(max_val, new_val))

def handle_ui():
    global current_page, active_slider, current_curve
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pressed = pygame.mouse.get_pressed()[0]
    
    if current_page == 0:
        # START page: click on the "Start" button (centered)
        btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
        if btn_rect.collidepoint(mouse_x, mouse_y) and pressed:
            current_page = 1
    elif current_page == 1:
        # INFO page: Back and Continue buttons
        back_rect = pygame.Rect(300, 600, 150, 50)
        cont_rect = pygame.Rect(750, 600, 150, 50)
        if back_rect.collidepoint(mouse_x, mouse_y) and pressed:
            current_page = 0
        elif cont_rect.collidepoint(mouse_x, mouse_y) and pressed:
            current_page = 2
    elif current_page == 2:
        # MAIN_APP page: Left panel interactions
        if mouse_x < WIDTH * 0.3:
            # Curve selection buttons
            for i, curve in enumerate(["Circle", "Parabola", "Ellipse", "Hyperbola"]):
                btn_rect = pygame.Rect(20, 100 + i * 80, 240, 40)
                if btn_rect.collidepoint(mouse_x, mouse_y) and pressed:
                    current_curve = curve
            # Sliders for curve parameters:
            if current_curve == "Circle":
                slider_rect = pygame.Rect(30, HEIGHT - 210, 240, 20)
                if slider_rect.collidepoint(mouse_x, mouse_y) and pressed:
                    active_slider = "Radius"
                    min_val, max_val = 0.1, 1.5
                    ratio = (mouse_x - 30) / 240
                    curve_params["radius"] = min_val + ratio * (max_val - min_val)
            elif current_curve in ("Ellipse", "Hyperbola"):
                slider_rect_a = pygame.Rect(30, HEIGHT - 210, 240, 20)
                slider_rect_b = pygame.Rect(30, HEIGHT - 280, 240, 20)
                if slider_rect_a.collidepoint(mouse_x, mouse_y) and pressed:
                    active_slider = "A (x-axis)"
                    min_val, max_val = 0.1, 2.0
                    ratio = (mouse_x - 30) / 240
                    curve_params["a"] = min_val + ratio * (max_val - min_val)
                elif slider_rect_b.collidepoint(mouse_x, mouse_y) and pressed:
                    active_slider = "B (y-axis)"
                    min_val, max_val = 0.1, 2.0
                    ratio = (mouse_x - 30) / 240
                    curve_params["b"] = min_val + ratio * (max_val - min_val)
            elif current_curve == "Parabola":
                slider_rect_a = pygame.Rect(30, HEIGHT - 210, 240, 20)
                slider_rect_b = pygame.Rect(30, HEIGHT - 280, 240, 20)
                if slider_rect_a.collidepoint(mouse_x, mouse_y) and pressed:
                    active_slider = "A (x² coeff)"
                    min_val, max_val = -2.0, 2.0
                    ratio = (mouse_x - 30) / 240
                    curve_params["a"] = min_val + ratio * (max_val - min_val)
                elif slider_rect_b.collidepoint(mouse_x, mouse_y) and pressed:
                    active_slider = "B (constant)"
                    min_val, max_val = -2.0, 2.0
                    ratio = (mouse_x - 30) / 240
                    curve_params["b"] = min_val + ratio * (max_val - min_val)
    
    if not pressed:
        active_slider = None

def draw_grid():
    glColor4f(0.4, 0.4, 0.4, 0.3)
    glLineWidth(1)
    glBegin(GL_LINES)
    for x in range(-10, 11):
        glVertex2f(x / 5.0, -2)
        glVertex2f(x / 5.0, 2)
    for y in range(-10, 11):
        glVertex2f(-2, y / 5.0)
        glVertex2f(2, y / 5.0)
    glEnd()

def draw_curve():
    glColor4f(*COLOR_ACCENT)
    glLineWidth(3)
    
    if current_curve == "Circle":
        glBegin(GL_LINE_LOOP)
        for i in range(360):
            angle = math.radians(i)
            x = curve_params["radius"] * math.cos(angle)
            y = curve_params["radius"] * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
    elif current_curve == "Parabola":
        glBegin(GL_LINE_STRIP)
        for i in range(-200, 201):
            x = i / 100.0
            y = curve_params["a"] * x**2 + curve_params["b"]
            glVertex2f(x, y)
        glEnd()
        
    elif current_curve == "Ellipse":
        glBegin(GL_LINE_LOOP)
        for i in range(360):
            angle = math.radians(i)
            x = curve_params["a"] * math.cos(angle)
            y = curve_params["b"] * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
    elif current_curve == "Hyperbola":
        # Draw the hyperbola defined by (x/a)^2 - (y/b)^2 = 1.
        # We use the parametric equations:
        #   x = ±a * cosh(t),   y = ±b * sinh(t)
        # t varies from 0 to t_max (adjust t_max as needed)
        a = curve_params["a"]
        b = curve_params["b"]
        t_min = 0.0
        t_max = 1.5  # Increase this if you want a larger visible section
        num_points = 100
        dt = (t_max - t_min) / (num_points - 1)
        
        # Right branch, upper half:
        glBegin(GL_LINE_STRIP)
        for i in range(num_points):
            t = t_min + i * dt
            x = a * math.cosh(t)
            y = b * math.sinh(t)
            glVertex2f(x, y)
        glEnd()
        
        # Right branch, lower half:
        glBegin(GL_LINE_STRIP)
        for i in range(num_points):
            t = t_min + i * dt
            x = a * math.cosh(t)
            y = -b * math.sinh(t)
            glVertex2f(x, y)
        glEnd()
        
        # Left branch, upper half:
        glBegin(GL_LINE_STRIP)
        for i in range(num_points):
            t = t_min + i * dt
            x = -a * math.cosh(t)
            y = b * math.sinh(t)
            glVertex2f(x, y)
        glEnd()
        
        # Left branch, lower half:
        glBegin(GL_LINE_STRIP)
        for i in range(num_points):
            t = t_min + i * dt
            x = -a * math.cosh(t)
            y = -b * math.sinh(t)
            glVertex2f(x, y)
        glEnd()

def render_main_app():
    # ---------------- Left Panel: UI Controls ----------------
    left_width = int(WIDTH * 0.3)
    glViewport(0, 0, left_width, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Coordinate system: origin at top-left
    gluOrtho2D(0, left_width, HEIGHT, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Left panel background
    glColor4f(*COLOR_PANEL)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(left_width, 0)
    glVertex2f(left_width, HEIGHT)
    glVertex2f(0, HEIGHT)
    glEnd()
    
    # Header for curve selection
    draw_text_vp("Select Curve:", 30, 50, 28, COLOR_TEXT)
    for i, curve in enumerate(["Circle", "Parabola", "Ellipse", "Hyperbola"]):
        btn_x = 20
        btn_y = 100 + i * 80
        btn_w = 240
        btn_h = 40
        rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        hover = rect.collidepoint(pygame.mouse.get_pos())
        btn_color = COLOR_ACCENT if current_curve == curve else COLOR_BUTTON
        draw_button(btn_x, btn_y, btn_w, btn_h, curve, btn_color, hover)
    
    # Parameter sliders header
    draw_text_vp("Parameters:", 30, HEIGHT - 260, 28, COLOR_TEXT)
    if current_curve == "Circle":
        draw_slider(30, HEIGHT - 210, 240, 20, curve_params["radius"], 0.1, 1.5, "Radius")
    elif current_curve in ("Ellipse", "Hyperbola"):
        draw_slider(30, HEIGHT - 210, 240, 20, curve_params["a"], 0.1, 2.0, "A (x-axis)")
        draw_slider(30, HEIGHT - 280, 240, 20, curve_params["b"], 0.1, 2.0, "B (y-axis)")
    elif current_curve == "Parabola":
        draw_slider(30, HEIGHT - 210, 240, 20, curve_params["a"], -2.0, 2.0, "A (x² coeff)")
        draw_slider(30, HEIGHT - 280, 240, 20, curve_params["b"], -2.0, 2.0, "B (constant)")
    
    # ---------------- Right Panel: Curve Visualization ----------------
    right_width = int(WIDTH * 0.7)
    glViewport(left_width, 0, right_width, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = right_width / HEIGHT
    # Coordinate system: origin at center
    gluOrtho2D(-2 * aspect, 2 * aspect, -2, 2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    draw_grid()
    draw_curve()
    
    # ---------------- Info Panel (Bottom of Right Panel) ----------------
    info_height = int(HEIGHT * 0.2)
    glViewport(left_width, HEIGHT - info_height, right_width, info_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Coordinate system: origin at top-left for the info panel.
    gluOrtho2D(0, right_width, info_height, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glColor4f(*COLOR_PANEL)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(right_width, 0)
    glVertex2f(right_width, info_height)
    glVertex2f(0, info_height)
    glEnd()
    
    fact = curve_facts[current_curve].format(**curve_params)
    draw_text_vp(fact, 20, 20, 22, COLOR_TEXT)

def main():
    init()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
        
        handle_ui()
        
        glClearColor(*COLOR_BG)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if PAGES[current_page] == "START":
            glViewport(0, 0, WIDTH, HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            # Use a top-left origin for full-window pages.
            gluOrtho2D(0, WIDTH, HEIGHT, 0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            draw_text_vp("Math Curves Visualizer", WIDTH // 2 - 300, HEIGHT // 2 - 100, 48, COLOR_ACCENT)
            btn_x = WIDTH // 2 - 100
            btn_y = HEIGHT // 2 + 50
            rect = pygame.Rect(btn_x, btn_y, 200, 50)
            hover = rect.collidepoint(pygame.mouse.get_pos())
            draw_button(btn_x, btn_y, 200, 50, "Start", COLOR_BUTTON, hover)
        elif PAGES[current_page] == "INFO":
            glViewport(0, 0, WIDTH, HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, WIDTH, HEIGHT, 0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            draw_text_vp("Learn Mathematical Curves", 100, 100, 36, COLOR_ACCENT)
            draw_text_vp("- Interactive visualizations with real-time controls", 100, 170, 24, COLOR_TEXT)
            draw_text_vp("- Adjust parameters using sliders", 100, 220, 24, COLOR_TEXT)
            draw_text_vp("- Educational facts and equations", 100, 270, 24, COLOR_TEXT)
            draw_button(300, 600, 150, 50, "Back", COLOR_BUTTON,
                        pygame.Rect(300, 600, 150, 50).collidepoint(pygame.mouse.get_pos()))
            draw_button(750, 600, 150, 50, "Continue", COLOR_BUTTON,
                        pygame.Rect(750, 600, 150, 50).collidepoint(pygame.mouse.get_pos()))
        else:
            render_main_app()
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
