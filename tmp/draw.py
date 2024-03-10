# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np
from so import WordMatr, Solver
import random
import time

random.seed(40)

class fieldDraw(object):
  def __init__(self, cell_size, letter_box, words_crd):
    self.letter_box = WordMatr(letter_box)

    self.cell_count = len(self.letter_box)
    self.cell_size = cell_size
    self.border_size = 10

    self.line_color = (50, 50, 50)
    self.font_color = (255, 255, 255)
    self.font = ImageFont.truetype("DejaVuSans.ttf", 36)

    self.field_size = cell_size * self.cell_count + 2 * self.border_size

    self.field = np.zeros((self.field_size, self.field_size, 3), dtype=np.uint8)

    self.draw_grid()
    self.fill_cell(words_crd)
    self.draw_letters()
    self.show_field()

  def draw_grid(self):
    for n in range(self.cell_count + 1):
      line_pose = self.border_size + self.cell_size * n
      line_begin = self.border_size
      line_end = self.field_size - self.border_size
      cv2.line(self.field, (line_begin, line_pose), (line_end, line_pose), self.line_color)
      cv2.line(self.field, (line_pose, line_begin), (line_pose, line_end), self.line_color)

  def draw_letters(self):
    field_pil = Image.fromarray(self.field)
    field_draw = ImageDraw.Draw(field_pil)
    for i in range(self.cell_count):
      for j in range(self.cell_count):
        field_draw.text((22 + i * self.cell_size, 12 + j * self.cell_size),
          self.letter_box.square[j][i], font=self.font, fill=self.font_color)
    self.field = np.array(field_pil, dtype=np.uint8)

  def show_field(self):
    cv2.imshow('field', self.field)
    cv2.waitKey(0)

  def fill_cell(self, words_crd):
    for word in words_crd:
      color = (int(random.uniform(0,255)),
                int(random.uniform(0,255)),
                int(random.uniform(0,255)))
      for crd in word:
        cv2.rectangle(self.field,
          (self.border_size + self.cell_size * crd[1] + 1,
           self.border_size + self.cell_size * crd[0] + 1),
          (self.border_size + self.cell_size * crd[1] + self.cell_size - 1,
           self.border_size + self.cell_size * crd[0] + self.cell_size - 1),
          color)


def draw_field():

  shift = 0
  for word in words:
    # print(word)
    pts = []
    shift += 1
    color_ = (int(random.uniform(0,255)), int(random.uniform(0,255)), int(random.uniform(0,255)))
    cv2.circle(field,
               ((word[0][1] * 50 + 15 + shift, word[0][0] * 50 + 15 + shift)),
               5,
               (0, 255, 255))
    for ch in word:
      cv2.line(field, (border + cell_size * ch[1], border + cell_size * ch[0]),
                      (border + cell_size * ch[1], border + cell_size * ch[0] + 50),
                      color_)
      cv2.line(field, (border + cell_size * ch[1] + 50, border + cell_size * ch[0]),
                      (border + cell_size * ch[1] + 50, border + cell_size * ch[0] + 50),
                      (color_))
      cv2.line(field, (border + cell_size * ch[1], border + cell_size * ch[0]),
                      (border + cell_size * ch[1] + 50, border + cell_size * ch[0]),
                      color_)
      cv2.line(field, (border + cell_size * ch[1], border + cell_size * ch[0] + 50),
                      (border + cell_size * ch[1] + 50, border + cell_size * ch[0] + 50),
                      color_)

      pts.append((ch[1] * 50 + 15 + shift, ch[0] * 50 + 15 + shift))
    cv2.polylines(field, np.int32([pts]), False, (30, 10, 200))

  # im  =  Image.new ( "RGB", (width,height), back_ground_color )
  field_pil = Image.fromarray(field)
  #configuration
  draw  =  ImageDraw.Draw ( field_pil )
  unicode_font = ImageFont.truetype("DejaVuSans.ttf", font_size)
  for i in range(N):
    for j in range(N):
      draw.text ( (22 + i * 50, 12 + j * 50),
                  A.square[j][i], font=unicode_font, fill=font_color )

  field = np.array(field_pil, dtype=np.uint8)

  cv2.imshow('field', field)
  cv2.waitKey(0)



if __name__ == "__main__":
    # draw_field()
  letter_box = 'square4x4.txt'
  solver = Solver('text.txt', (3, 10))
  solver.solve(letter_box)
  words = solver.get_unique_words()
  field_draw = fieldDraw(50, letter_box, words)