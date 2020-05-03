from pygame.draw import rect as draw_rect

def darken_color(color, factor):
    return tuple(int(c * factor) for c in color)


def draw_piece(surf, color, left, top, width, height, size):
    padding_factor = 0.025
    shadow_factor = 0.085
    margin_factor = 0.05

    base_color = color
    margin_color = darken_color(color, 0.8)
    bottom_color = darken_color(color, 0.4)

    # Applying padding
    padding = int(size * padding_factor)
    left, top = left + padding, top + padding
    width, height = width - 2 * padding, height - 2 * padding
    size = size - 2 * padding

    # Applying shadow effect
    shadow = int(size * shadow_factor)
    top_rect = (left, top, width - shadow, height - shadow)
    bottom_rect = (left + shadow, top + shadow, width - shadow, height - shadow)

    draw_rect(surf, bottom_color, bottom_rect)
    draw_rect(surf, base_color, top_rect)

    # Draw margins
    draw_rect(surf, margin_color, top_rect, int(size * margin_factor))

