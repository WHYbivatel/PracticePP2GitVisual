import pygame
import math


def main():
    pygame.init()

    # Window size
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint with Shapes")

    clock = pygame.time.Clock()

    # Background color of the canvas
    BG_COLOR = (255, 255, 255)

    # Fill screen with white at the beginning
    screen.fill(BG_COLOR)

    # Current drawing color
    current_color = (0, 0, 255)  # blue by default

    # Current selected tool
    # Available tools:
    # brush, rect, circle, eraser, square, right_triangle,
    # equilateral_triangle, rhombus
    tool = "brush"

    # Brush size
    brush_radius = 8

    # Is the user currently drawing?
    drawing = False

    # Previous mouse position for brush/eraser drawing
    last_pos = None

    # Start position for shapes
    start_pos = None

    # Copy of canvas used for previewing shapes while dragging
    canvas = screen.copy()

    # Font for UI text
    font = pygame.font.SysFont("arial", 20)

    running = True
    while running:
        # Check which modifier keys are held
        pressed = pygame.key.get_pressed()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            # Close window
            if event.type == pygame.QUIT:
                running = False

            # Keyboard controls
            if event.type == pygame.KEYDOWN:
                # Exit shortcuts
                if event.key == pygame.K_w and ctrl_held:
                    running = False
                elif event.key == pygame.K_F4 and alt_held:
                    running = False
                elif event.key == pygame.K_ESCAPE:
                    running = False

                # -------------------------
                # Tool selection
                # -------------------------
                elif event.key == pygame.K_1:
                    tool = "brush"
                elif event.key == pygame.K_2:
                    tool = "rect"
                elif event.key == pygame.K_3:
                    tool = "circle"
                elif event.key == pygame.K_4:
                    tool = "eraser"
                elif event.key == pygame.K_5:
                    tool = "square"
                elif event.key == pygame.K_6:
                    tool = "right_triangle"
                elif event.key == pygame.K_7:
                    tool = "equilateral_triangle"
                elif event.key == pygame.K_8:
                    tool = "rhombus"

                # -------------------------
                # Color selection
                # -------------------------
                elif event.key == pygame.K_r:
                    current_color = (255, 0, 0)      # red
                elif event.key == pygame.K_g:
                    current_color = (0, 255, 0)      # green
                elif event.key == pygame.K_b:
                    current_color = (0, 0, 255)      # blue
                elif event.key == pygame.K_k:
                    current_color = (0, 0, 0)        # black
                elif event.key == pygame.K_y:
                    current_color = (255, 255, 0)    # yellow
                elif event.key == pygame.K_p:
                    current_color = (255, 0, 255)    # pink
                elif event.key == pygame.K_c:
                    current_color = (0, 255, 255)    # cyan

                # Clear the whole canvas
                elif event.key == pygame.K_SPACE:
                    screen.fill(BG_COLOR)
                    canvas = screen.copy()

            # Mouse button pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Left mouse button starts drawing
                if event.button == 1:
                    drawing = True
                    start_pos = event.pos
                    last_pos = event.pos

                    # Save current canvas for shape preview
                    canvas = screen.copy()

                    # Immediately draw one point if brush or eraser is selected
                    if tool == "brush":
                        pygame.draw.circle(screen, current_color, event.pos, brush_radius)
                    elif tool == "eraser":
                        pygame.draw.circle(screen, BG_COLOR, event.pos, brush_radius)

                # Mouse wheel up increases brush size
                elif event.button == 4:
                    brush_radius = min(100, brush_radius + 1)

                # Mouse wheel down decreases brush size
                elif event.button == 5:
                    brush_radius = max(1, brush_radius - 1)

                # Right mouse button also decreases brush size
                elif event.button == 3:
                    brush_radius = max(1, brush_radius - 1)

            # Mouse button released
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    end_pos = event.pos

                    # Finalize shapes when mouse is released
                    if tool == "rect":
                        screen.blit(canvas, (0, 0))
                        rect = make_rect(start_pos, end_pos)
                        pygame.draw.rect(screen, current_color, rect, 2)

                    elif tool == "circle":
                        screen.blit(canvas, (0, 0))
                        center, radius = make_circle_data(start_pos, end_pos)
                        if radius > 0:
                            pygame.draw.circle(screen, current_color, center, radius, 2)

                    elif tool == "square":
                        screen.blit(canvas, (0, 0))
                        rect = make_square(start_pos, end_pos)
                        pygame.draw.rect(screen, current_color, rect, 2)

                    elif tool == "right_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_right_triangle(start_pos, end_pos)
                        pygame.draw.polygon(screen, current_color, points, 2)

                    elif tool == "equilateral_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_equilateral_triangle(start_pos, end_pos)
                        pygame.draw.polygon(screen, current_color, points, 2)

                    elif tool == "rhombus":
                        screen.blit(canvas, (0, 0))
                        points = make_rhombus(start_pos, end_pos)
                        pygame.draw.polygon(screen, current_color, points, 2)

                    # Save the finished canvas
                    canvas = screen.copy()
                    drawing = False
                    start_pos = None
                    last_pos = None

            # Mouse movement
            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    current_pos = event.pos

                    # Free drawing with brush
                    if tool == "brush":
                        draw_line(screen, current_color, last_pos, current_pos, brush_radius)
                        last_pos = current_pos

                    # Eraser works the same way as brush,
                    # but draws with background color
                    elif tool == "eraser":
                        draw_line(screen, BG_COLOR, last_pos, current_pos, brush_radius)
                        last_pos = current_pos

                    # Shape preview while dragging
                    elif tool == "rect":
                        screen.blit(canvas, (0, 0))
                        rect = make_rect(start_pos, current_pos)
                        pygame.draw.rect(screen, current_color, rect, 2)

                    elif tool == "circle":
                        screen.blit(canvas, (0, 0))
                        center, radius = make_circle_data(start_pos, current_pos)
                        if radius > 0:
                            pygame.draw.circle(screen, current_color, center, radius, 2)

                    elif tool == "square":
                        screen.blit(canvas, (0, 0))
                        rect = make_square(start_pos, current_pos)
                        pygame.draw.rect(screen, current_color, rect, 2)

                    elif tool == "right_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_right_triangle(start_pos, current_pos)
                        pygame.draw.polygon(screen, current_color, points, 2)

                    elif tool == "equilateral_triangle":
                        screen.blit(canvas, (0, 0))
                        points = make_equilateral_triangle(start_pos, current_pos)
                        pygame.draw.polygon(screen, current_color, points, 2)

                    elif tool == "rhombus":
                        screen.blit(canvas, (0, 0))
                        points = make_rhombus(start_pos, current_pos)
                        pygame.draw.polygon(screen, current_color, points, 2)

        # Draw simple UI bar on top
        draw_ui(screen, font, tool, current_color, brush_radius)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def draw_line(screen, color, start, end, radius):
    """
    Draw a smooth thick line using many circles between two points.
    This prevents gaps when the mouse moves quickly.
    """
    if start is None or end is None:
        return

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max(abs(dx), abs(dy))

    # If mouse did not move, draw one circle
    if distance == 0:
        pygame.draw.circle(screen, color, start, radius)
        return

    for i in range(distance + 1):
        x = int(start[0] + dx * i / distance)
        y = int(start[1] + dy * i / distance)
        pygame.draw.circle(screen, color, (x, y), radius)


def make_rect(start, end):
    """
    Create a rectangle no matter in which direction
    the mouse is dragged.
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
    Create a square.
    Side length is the smaller of width and height,
    so the shape always remains a square.
    """
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))

    # Determine in which direction the user dragged
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
    Use the starting point as the center of the circle.
    Radius is the distance from start point to current point.
    """
    cx, cy = start
    ex, ey = end

    radius = int(math.sqrt((ex - cx) ** 2 + (ey - cy) ** 2))
    return (cx, cy), radius


def make_right_triangle(start, end):
    """
    Create a right triangle inside the rectangle
    formed by start and end points.

    Vertices:
    - start point
    - point with x from start, y from end
    - end point
    This guarantees a 90-degree angle.
    """
    x1, y1 = start
    x2, y2 = end

    return [(x1, y1), (x1, y2), (x2, y2)]


def make_equilateral_triangle(start, end):
    """
    Create an equilateral triangle.

    The start point is the top vertex.
    The horizontal distance from start to end determines the side length.
    """
    x1, y1 = start
    x2, _ = end

    # Side length is based on horizontal drag distance
    side = abs(x2 - x1)

    # Avoid zero-size triangle
    if side == 0:
        side = 1

    # Decide whether triangle goes to the right or to the left
    direction = 1 if x2 >= x1 else -1

    # Height of an equilateral triangle: sqrt(3)/2 * side
    height = int((math.sqrt(3) / 2) * side)

    # Top vertex
    p1 = (x1, y1)

    # Bottom left / right vertices
    p2 = (x1 - direction * side // 2, y1 + height)
    p3 = (x1 + direction * side // 2, y1 + height)

    return [p1, p2, p3]


def make_rhombus(start, end):
    """
    Create a rhombus inside the rectangle formed by start and end.

    The vertices are:
    - top middle
    - right middle
    - bottom middle
    - left middle
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


def draw_ui(screen, font, tool, color, brush_radius):
    """
    Draw a simple info panel at the top of the window.
    """
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, screen.get_width(), 45))

    info = (
        f"Tool: {tool}   |   Size: {brush_radius}   |   Color: {color}"
    )
    text_surface = font.render(info, True, (0, 0, 0))
    screen.blit(text_surface, (10, 12))

    # Small box that shows the current selected color
    pygame.draw.rect(screen, color, (860, 10, 24, 24))
    pygame.draw.rect(screen, (0, 0, 0), (860, 10, 24, 24), 2)


main()