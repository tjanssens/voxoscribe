"""Generate icon assets for VoxoScribe."""

from PIL import Image, ImageDraw


def create_icon(color: str, filename: str, size: int = 64) -> None:
    """Create a circular icon with the given color.

    Args:
        color: Fill color for the icon
        filename: Output filename
        size: Icon size in pixels
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    padding = 4
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=color
    )

    inner_padding = size // 4
    draw.ellipse(
        [inner_padding, inner_padding, size - inner_padding, size - inner_padding],
        fill='white'
    )

    image.save(filename, 'PNG')
    print(f"Created {filename}")


def create_ico(filename: str) -> None:
    """Create Windows ICO file with multiple sizes.

    Args:
        filename: Output filename
    """
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        padding = max(1, size // 16)
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill='#4a90d9'
        )

        inner_padding = size // 4
        draw.ellipse(
            [inner_padding, inner_padding, size - inner_padding, size - inner_padding],
            fill='white'
        )

        mic_width = max(2, size // 8)
        mic_height = max(4, size // 4)
        mic_x = (size - mic_width) // 2
        mic_y = (size - mic_height) // 2 - size // 16

        draw.rounded_rectangle(
            [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height],
            radius=mic_width // 2,
            fill='#4a90d9'
        )

        stand_width = max(1, size // 16)
        stand_x = (size - stand_width) // 2
        stand_y = mic_y + mic_height
        stand_height = max(2, size // 8)

        draw.rectangle(
            [stand_x, stand_y, stand_x + stand_width, stand_y + stand_height],
            fill='#4a90d9'
        )

        images.append(image)

    images[0].save(filename, format='ICO', sizes=[(s, s) for s in sizes])
    print(f"Created {filename}")


def main():
    """Generate all icons."""
    create_icon('#808080', 'icon_idle.png')
    create_icon('#ff4444', 'icon_recording.png')
    create_icon('#ffaa00', 'icon_processing.png')

    create_ico('icon.ico')

    print("All icons generated successfully!")


if __name__ == '__main__':
    main()
