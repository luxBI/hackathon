
import PIL
from PIL import Image
import numpy as np

def vectorize_image(img):
  image = np.array(Image.open(
        img
        ).resize((100,100)).convert('L')).ravel().astype(float)/255.0
  return image.reshape(1,-1)