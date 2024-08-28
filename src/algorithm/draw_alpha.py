import pygame


def rectangle(
    surface: pygame.Surface,
    color: tuple[Literal[255], Literal[255], Literal[255], Literal[255]],
    rect: tuple,
) -> None:
    """
    Draw a rectangle on the given surface with the specified color and alpha.

    Args:
        surface (pygame.Surface): The surface to draw the rectangle on.
        color (tuple): The color of the rectangle.
        rect (tuple): The dimensions of the rectangle (x, y, width, height).

    Returns:
        None
    """
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def line(
    surface: pygame.Surface,
    color: tuple,
    start_pos: tuple,
    end_pos: tuple,
    width: float,
) -> None:
    """
    Draw a line on the given surface.

    Args:
        surface (pygame.Surface): The surface to draw the line on.
        color (tuple): The color of the line in RGB format.
        start_pos (tuple): The starting position of the line.
        end_pos (tuple): The ending position of the line.
        width (float): The width of the line.

    Returns:
        None
    """
    lx, ly = (start_pos[0], end_pos[0]), (start_pos[1], end_pos[1])
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y).inflate(
        (width, width)
    )
    a, b = target_rect.x, target_rect.y
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.line(
        shape_surf,
        color,
        (start_pos[0] - a, start_pos[1] - b),
        (end_pos[0] - a, end_pos[1] - b),
        width,
    )
    surface.blit(shape_surf, target_rect)


def circle(surface, color, center, radius):
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)


def polygon(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)
