import os
from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

# The modern SDK only accepts private_key at initialization
imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY")
)

# Keep the URL endpoint in a separate variable if you need to build explicit URLs later
IMAGEKIT_URL = os.getenv("IMAGEKIT_URL")