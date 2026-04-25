from src.post_generator.config import Config
from src.post_generator.services import composition, mask, transform
from pathlib import Path
import random

def generate_post(config: Config):
    """
    Orchestrate the generation of the Instagram post.
    """
    print(f"Starting generation with config:")
    print(f"Photo: {config.photo}")
    print(f"Position: {config.position}")
    print(f"Text: {config.text}")
    print(f"X: {config.x}")
    print(f"Y: {config.y}")
    print(f"Output path: {config.output_path}")
    print(f"Output name: {config.output_name}")

    # Skeleton for future integration:
    # 1. Load the background image (config.photo)
    # bg = Image.open(config.photo)
    
    # 2. Setup PRNG for repeatable transforms if needed
    # rng = random.Random(42)
    # position = transform.choose_position(config.position, rng)
    
    # 3. Create Mask
    # generated_mask = mask.build_smooth_mask(...)
    
    # 4. Compose Image
    # result = composition.compose(bg, generated_mask)
    
    # 5. Render Text
    # ...
    
    # 6. Save Image
    # output_dir = config.output_path if config.output_path else "."
    # out_path = Path(output_dir) / config.output_name
    # composition.save_output(result, str(out_path))
    
    print("Generation complete!")
