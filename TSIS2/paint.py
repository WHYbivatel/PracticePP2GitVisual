import pygame
import math
from collections import deque
from datetime import datetime


def draw_ui(screen, font, tool, color, brush_size, text_mode):
    """
    Draw a simple toolbar/info bar at the top of the window.
    """
    pygame.draw.rect(screen, (235, 235, 235), (0, 0, screen.get_width(), 90))
    pygame.draw.line(screen, (180, 180, 180), (0, 90), (screen.get_width(), 90), 2)

    info_1 = f"Tool: {tool}   |   Color: {color}   |   Size: {brush_size}px"
    info_2 = (
        "Tools: P-pencil, L-line, O-rect, C-circle, E-eraser, S-square, "
        "R-right triangle, T-equilateral triangle, H-rhombus, F-fill, X-text"
    )
    info_3 = (
        "Sizes: 1-small(2px), 2-medium(5px), 3-large(10px)   |   "
        "Colors: B-blue, G-green, K-black, Y-yellow, M-magenta, N-cyan, U-red   |   "
        "Ctrl+S save   Space clear"
    )

    text1 = font.render(info_1, True, (0, 0, 0))
    text2 = font.render(info_2, True, (0, 0, 0))
    text3 = font.render(info_3, True, (0, 0, 0))

    screen.blit(text1, (10, 8))
    screen.blit(text2, (10, 32))
    screen.blit(text3, (10, 56))

    # Small preview box showing current color
    pygame.draw.rect(screen, color, (930, 10, 40, 25))
    pygame.draw.rect(screen, (0, 0, 0), (930, 10, 40, 25), 2)

    # Show text mode status if active
    if text_mode:
        status = font.render("TEXT MODE: type and press Enter to place text, Esc to cancel", True, (180, 0, 0))
        screen.blit(status, (10, 70))


def draw_freehand_line(surface, color, start, end, width):
    """
    Draw a continuous freehand stroke using pygame.draw.line.
    This is used for the pencil and eraser tools.
    """
    if start is None or end is None:
        return
    pygame.draw.line(surface, color, start, end, width)


def make_rect(start, end):
    """
    Create a rectangle regardless of drag direction.
    """
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    return pygame.Rect(left, top, width, height)


def make_square(start, end):
    """
    Create a square by forcing width and height to be equal.
    """
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 >= x1:
        left = x1
    else:
        left = x1 - side

    if y2 >= y1:
        top = y1
    else:
        top = y1 - side

    return pygame.Rect(left, top, side, side)


def make_circle_data(start, end):
    """
    Use the start point as the center of the circle.
    Radius is distance from start point to current point.
    """
    cx, cy = start
    ex, ey = end
    radius = int(math.sqrt((ex - cx) ** 2 + (ey - cy) ** 2))
    return (cx, cy), radius


def make_right_triangle(start, end):
    """
    Create a right triangle inside the rectangle formed by start and end.
    """
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]


def make_equilateral_triangle(start, end):
    """
    Create an equilateral triangle.
    The horizontal drag distance determines the side length.
    """
    x1, y1 = start
    x2, _ = end

    side = abs(x2 - x1)
    if side == 0:
        side = 1

    direction = 1 if x2 >= x1 else -1
    height = int((math.sqrt(3) / 2) * side)

    p1 = (x1, y1)
    p2 = (x1 - direction * side // 2, y1 + height)
    p3 = (x1 + direction * side // 2, y1 + height)

    return [p1, p2, p3]


def make_rhombus(start, end):
    """
    Create a rhombus using the middle points of a bounding rectangle.
    """
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)

    mid_x = (left + right) // 2
    mid_y = (top + bottom) // 2

    return [
        (mid_x, top),
        (right, mid_y),
        (mid_x, bottom),
        (left, mid_y)
    ]


def flood_fill(surface, start_pos, new_color, toolbar_height=90):
    """
    Fill a closed region using exact color matching.

    Uses pygame.Surface.get_at() and pygame.Surface.set_at() as required.
    """
    width, height = surface.get_size()
    x, y = start_pos

    if y < toolbar_height:
        return

    target_color = surface.get_at((x, y))
    new_color_with_alpha = pygame.Color(*new_color)

    # If clicked color is already the chosen color, do nothing
    if target_color == new_color_with_alpha:
        return

    queue = deque()
    queue.append((x, y))

    while queue:
        px, py = queue.pop()

        if px < 0 or px >= width or py < toolbar_height or py >= height:
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), new_color_with_alpha)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def save_canvas(surface, toolbar_height=90):
    """
    Save only the drawing canvas area (without the toolbar) as a PNG file.
    """
    width, height = surface.get_size()
    canvas_rect = pygame.Rect(0, toolbar_height, width, height - toolbar_height)
    canvas_surface = surface.subsurface(canvas_rect).copy()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paint_{timestamp}.png"
    pygame.image.save(canvas_surface, filename)
    return filename


def main():
    pygame.init()

    # Window settings
    WIDTH, HEIGHT = 1000, 700
    TOOLBAR_HEIGHT = 90

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS 2 Paint Application")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)
    text_font = pygame.font.SysFont("arial", 28)

    # Colors
    BG_COLOR = (255, 255, 255)
    current_color = (0, 0, 255)  # default blue

    # Fill the whole window once
    screen.fill(BG_COLOR)

    # Current tool
    tool = "pencil"

    # Required brush sizes
    brush_size = 2  # small by default

    # Drawing states
    drawing = False
    start_pos = None
    last_pos = None

    # Canvas copy used for live preview
    canvas = screen.copy()

    # Text tool state
    text_active = False
    text_pos = None
    text_input = ""

    running = True
    while running:
        pressed = pygame.key.get_pressed()
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]

        for event in pygame.event.get():
            # Close button
            if event.type == pygame.QUIT:
                running = False

            # -------------------------
            # KEYBOARD INPUT
            # -------------------------
            if event.type == pygame.KEYDOWN:
                # Exit hotkeys
                if event.key == pygame.K_ESCAPE and not text_active:
                    running = False
                elif event.key == pygame.K_w and ctrl_held:
                    running = False
                elif event.key == pygame.K_F4 and alt_held:
                    running = False

                # Save image with Ctrl+S
                elif event.key == pygame.K_s and ctrl_held:
                    filename = save_canvas(screen, TOOLBAR_HEIGHT)
                    print(f"Saved as {filename}")

                # If text mode is active, process typing first
                elif text_active:
                    if event.key == pygame.K_RETURN:
                        # Finalize text onto the canvas
                        screen.blit(canvas, (0, 0))
                        text_surface = text_font.render(text_input, True, current_color)
                        screen.blit(text_surface, text_pos)
                        canvas = screen.copy()

                        text_active = False
                        text_input = ""
                        text_pos = None

                    elif event.key == pygame.K_ESCAPE:
                        # Cancel text input
                        text_active = False
                        text_input = ""
                        text_pos = None
                        screen.blit(canvas, (0, 0))

                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]

                    else:
                        # Add typed character
                        if event.unicode.isprintable():
                            text_input += event.unicode

                else:
                    # -------------------------
                    # TOOL SELECTION
                    # -------------------------
                    if event.key == pygame.K_p:
                        tool = "pencil"
                    elif event.key == pygame.K_l:
                        tool = "line"
                    elif event.key == pygame.K_o:
                        tool = "rect"
                    elif event.key == pygame.K_c:
                        tool = "circle"
                    elif event.key == pygame.K_e:
                        tool = "eraser"
                    elif event.key == pygame.K_s:
                        tool = "square"
                    elif event.key == pygame.K_r:
                        tool = "right_triangle"
                    elif event.key == pygame.K_t:
                        tool = "equilateral_triangle"
                    elif event.key == pygame.K_h:
                        tool = "rhombus"
                    elif event.key == pygame.K_f:
                        tool = "fill"
                    elif event.key == pygame.K_x:
                        tool = "text"

                    # -------------------------
                    # BRUSH SIZE SELECTION
                    # -------------------------
                    elif event.key == pygame.K_1:
                        brush_size = 2
                    elif event.key == pygame.K_2:
                        brush_size = 5
                    elif event.key == pygame.K_3:
                        brush_size = 10

                    # -------------------------
                    # COLOR SELECTION
                    # -------------------------
                    elif event.key == pygame.K_b:
                        current_color = (0, 0, 255)      # blue
                    elif event.key == pygame.K_g:
                        current_color = (0, 255, 0)      # green
                    elif event.key == pygame.K_k:
                        current_color = (0, 0, 0)        # black
                    elif event.key == pygame.K_y:
                        current_color = (255, 255, 0)    # yellow
                    elif event.key == pygame.K_m:
                        current_color = (255, 0, 255)    # magenta
                    elif event.key == pygame.K_n:
                        current_color = (0, 255, 255)    # cyan
                    elif event.key == pygame.K_u:
                        current_color = (255, 0, 0)      # red

                    # Clear canvas
                    elif event.key == pygame.K_SPACE:
                        screen.fill(BG_COLOR)
                        canvas = screen.copy()

            # -------------------------
            # MOUSE BUTTON DOWN
            # -------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Ignore clicks on toolbar area for drawing
                if event.pos[1] < TOOLBAR_HEIGHT:
                    continue

                # Left mouse button
                if event.button == 1:
                    # Fill tool acts immediately on click
                    if tool == "fill":
                        flood_fill(screen, event.pos, current_color, TOOLBAR_HEIGHT)
                        canvas = screen.copy()

                    # Text tool starts text cursor placement
                    elif tool == "text":
                        text_active = True
                        text_pos = event.pos
                        text_input = ""
                        canvas = screen.copy()

                    else:
                        drawing = True
                        start_pos = event.pos
                        last_pos = event.pos
                        canvas = screen.copy()

                        # Pencil starts with a point
                        if tool == "pencil":
                            pygame.draw.line(screen, current_color, event.pos, event.pos, brush_size)
                            canvas = screen.copy()

                        # Eraser starts with a point
                        elif tool == "eraser":
                            pygame.draw.line(screen, BG_COLOR, event.pos, event.pos, brush_size)
                            canvas = screen.copy()

            # -------------------------
            # MOUSE BUTTON UP
            # -------------------------
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    end_pos = event.pos

                    # Finalize straight line
                    if tool == "line":
                        screen.blit(canvas, (0, 0))
                        pygame.draw.line(screen, current_color, start_pos, end_pos, brush_size)

                    # Finalize rectangle
                    elif tool == "rect":
                        screen.blit(canvas, (0, 0))
                        rect = make_rect(start_pos, end_pos)
                        pygame.draw.rect(screen, current_color, rect, brush_size)

                    # Finalize circle
                    elif tool == "circle":
                        screen.blit(canvas, (0, 0))
                        center, radius = make_circle_data(start_pos, end_pos)
                        if radius > 0:
                            pygame.draw.circle(screen, current_color, center, radius, brush_size)

                    # Finalize square
                    elif tool == "square":
                        screen.blit(canvas, (0, 0))
                        rect = make_square(start_pos, end_pos)
                        pygame.draw.rect(screen, current_color, rect, brush_size)

                    # Finalize right triangle
                    elif tool == "right_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_right_triangle(start_pos, end_pos)
                        pygame.draw.polygon(screen, current_color, points, brush_size)

                    # Finalize equilateral triangle
                    elif tool == "equilateral_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_equilateral_triangle(start_pos, end_pos)
                        pygame.draw.polygon(screen, current_color, points, brush_size)

                    # Finalize rhombus
                    elif tool == "rhombus":
                        screen.blit(canvas, (0, 0))
                        points = make_rhombus(start_pos, end_pos)
                        pygame.draw.polygon(screen, current_color, points, brush_size)

                    canvas = screen.copy()
                    drawing = False
                    start_pos = None
                    last_pos = None

            # -------------------------
            # MOUSE MOTION
            # -------------------------
            if event.type == pygame.MOUSEMOTION:
                # Freehand drawing tools
                if drawing:
                    current_pos = event.pos

                    # Pencil tool
                    if tool == "pencil":
                        draw_freehand_line(screen, current_color, last_pos, current_pos, brush_size)
                        last_pos = current_pos
                        canvas = screen.copy()

                    # Eraser tool
                    elif tool == "eraser":
                        draw_freehand_line(screen, BG_COLOR, last_pos, current_pos, brush_size)
                        last_pos = current_pos
                        canvas = screen.copy()

                    # Straight line preview
                    elif tool == "line":
                        screen.blit(canvas, (0, 0))
                        pygame.draw.line(screen, current_color, start_pos, current_pos, brush_size)

                    # Rectangle preview
                    elif tool == "rect":
                        screen.blit(canvas, (0, 0))
                        rect = make_rect(start_pos, current_pos)
                        pygame.draw.rect(screen, current_color, rect, brush_size)

                    # Circle preview
                    elif tool == "circle":
                        screen.blit(canvas, (0, 0))
                        center, radius = make_circle_data(start_pos, current_pos)
                        if radius > 0:
                            pygame.draw.circle(screen, current_color, center, radius, brush_size)

                    # Square preview
                    elif tool == "square":
                        screen.blit(canvas, (0, 0))
                        rect = make_square(start_pos, current_pos)
                        pygame.draw.rect(screen, current_color, rect, brush_size)

                    # Right triangle preview
                    elif tool == "right_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_right_triangle(start_pos, current_pos)
                        pygame.draw.polygon(screen, current_color, points, brush_size)

                    # Equilateral triangle preview
                    elif tool == "equilateral_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_equilateral_triangle(start_pos, current_pos)
                        pygame.draw.polygon(screen, current_color, points, brush_size)

                    # Rhombus preview
                    elif tool == "rhombus":
                        screen.blit(canvas, (0, 0))
                        points = make_rhombus(start_pos, current_pos)
                        pygame.draw.polygon(screen, current_color, points, brush_size)

        # If text tool is active, show live text preview
        if text_active:
            screen.blit(canvas, (0, 0))
            preview_surface = text_font.render(text_input, True, current_color)
            screen.blit(preview_surface, text_pos)

        # Draw toolbar at the end so it stays visible
        draw_ui(screen, font, tool, current_color, brush_size, text_active)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


main()