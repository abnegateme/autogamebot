import sys
import cv2
import pytesseract
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'D:\\soft\\Tesseract-OCR\\tesseract.exe'
import numpy as np
from collections import deque

import argparse

# def auto_canny(image, sigma=0.33):
# 	# compute the median of the single channel pixel intensities
# 	v = np.median(image)

# 	# apply automatic Canny edge detection using the computed median
# 	lower = int(max(0, (1.0 - sigma) * v))
# 	upper = int(min(255, (1.0 + sigma) * v))
# 	edged = cv2.Canny(image, lower, upper)

# 	# return the edged image
# 	return edged

def process_image(image):
  height, width = image.shape
  flags = cv2.THRESH_BINARY + cv2.THRESH_OTSU
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

  image = image[int(0.30 * height):-int(0.25 * height), :] #TODO
  _, processed = cv2.threshold(image, 0, 255, flags)
  processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)

  return processed

def get_bounding_boxes(image):
  print(type(image))
  contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  bbs = [cv2.boundingRect(ctr) for ctr in contours if cv2.contourArea(ctr) > 200]
  return bbs

def sort_detected_letters(bounding_boxes):
  bbs_np = np.array(bounding_boxes)
  shape = int(np.sqrt(len(bounding_boxes)))
  bbs_np = bbs_np[bbs_np[:, 1].argsort()].reshape(shape, shape, 4)
  for i in range(shape):
    tmp = bbs_np[i, :, :]
    bbs_np[i, :, :] = tmp[tmp[:, 0].argsort()]

  bbs_np = bbs_np.reshape(len(bounding_boxes), 4)
  print(bbs_np)
  return bbs_np.tolist()

def make_letter_box(bbs, image):
  max_h = 0
  all_width = 0
  for bb in bbs:
    all_width += bb[2]
    if bb[3] > max_h:
      max_h = bb[3]

  pos = 5
  box = np.zeros((max_h+10, all_width + (len(bbs) + 1) * pos), dtype=np.uint8)
  for bb in bbs:
    box[10:10+bb[3],pos:pos+bb[2]] = image[bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]]
    pos += (bb[2] + 5)

  return box


def get_letters_from_image(image_path):
  """
  https://stackoverflow.com/questions/50431647/how-to-detect-symbols-on-a-image-and-save-it
  """
  image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
  processed_image = process_image(image)
  bbs = get_bounding_boxes(processed_image)
  bbs = sort_detected_letters(bbs)
  letter_box = make_letter_box(bbs, processed_image)
  letters = pytesseract.image_to_string(letter_box, lang='rus')

  return letters


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--image_path', type=str)
    args = parser.parse_args()

    letters = get_letters_from_image(args.image_path)
    print(letters)
