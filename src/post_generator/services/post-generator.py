from pathlib import Path
from PIL import Image, UnidentifiedImageError

insta_width = 1080
insta_height = 1080
insta_ratio = insta_width / insta_height

def load_image(image_path: str) -> Image.Image:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError("Image does not exist")
    try:
        image = Image.open(path)
        return image.convert("RGBA")
    except UnidentifiedImageError:
        raise FileNotFoundError(f"Image could not be opened: {image_path}")


def crop_to_square(image):
    width, height = image.size

    if width > height:
        left = (width - height) // 2
        right = left + height
        return image.crop((left, 0, right, height))

    elif height > width:
        top = (height - width) // 2
        bottom = top + width
        return image.crop((0, top, width, bottom))
    return image


def resize_to_instagram_size(image: Image.Image) -> Image.Image:
    return image.resize((insta_width, insta_ratio), Image.Resampling.LANCZOS)

def process_background(image_path: str) -> Image.Image:
    image = load_image(image_path)
    image = crop_to_square(image)
    image = resize_to_instagram_size(image)
    return image