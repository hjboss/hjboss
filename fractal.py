#!/usr/bin/env python
"""
Copyright 2021 The HongJiang Library Authors. All right reserved.
Use of this source that is governed by a Apache-style
license that can be found in the LICENSE file.

定義常見的 分形幾何圖(Fractal Geometry) 生成器

@authors hjboss <hongjiangproject@gmail.com> 2021-04 $
"""
import hashlib
import json
import math
from datetime import datetime
from PIL import Image, ImageDraw

class FractalGeometry:
  ''' Fractal Geometry Bitmap '''
  def __init__(self, radius: int, minimize: bool = False) -> None:
    self.id = 'FractalGeometry'
    self.radius = radius or 512
    self.maxwidth = self.radius
    self.minimize = bool(minimize)
    self.background = (18, 80, 123, 255) # 碧城
    self.itercolors = {0: (234, 238, 241, 255)} # 淺雲
    self.background = (234, 238, 241, 255)
    self.itercolors = {0: (18, 80, 123, 255)}
    self.background = (0, 0, 0, 0)
    self.pointsdata = 0

    self.info('begin fractal geometries')

  def weierstrass(self, polygons: list, offset: float, iterations: int) -> None:
    radian = 1 / (2 + abs(math.sin(math.pi * offset * 0.5)) * 2)
    factor = radian if offset >= 0 else -radian
    data_iterations = [polygons for _ in range(iterations + 1)]

    for iters in range(iterations):
      data_iterations[iters + 1] = []

      for idx in range(len(data_iterations[iters])):
        points = data_iterations[iters][idx]

        points.extend([
          (
            round(points[0][0] + (points[1][0] - points[0][0]) * radian),
            round(points[0][1] + (points[1][1] - points[0][1]) * radian),
          ),
          (
            round(points[1][0] - (points[1][0] - points[0][0]) * radian),
            round(points[1][1] - (points[1][1] - points[0][1]) * radian),
          ),
          (
            round(
              (points[0][0] + points[1][0]) * 0.5 +
              (points[1][1] - points[0][1]) *
              math.cos(math.pi * radian * 0.5) * factor
            ),
            round(
              (points[0][1] + points[1][1]) * 0.5 -
              (points[1][0] - points[0][0]) *
              math.cos(math.pi * radian * 0.5) * factor
            ),
          ),
        ])

        if abs(points[2][0]) > self.maxwidth:
          self.maxwidth = abs(points[2][0])

        if abs(points[2][1]) > self.maxwidth:
          self.maxwidth = abs(points[2][1])

        if abs(points[3][0]) > self.maxwidth:
          self.maxwidth = abs(points[2][0])

        if abs(points[3][1]) > self.maxwidth:
          self.maxwidth = abs(points[2][1])

        if abs(points[4][0]) > self.maxwidth:
          self.maxwidth = abs(points[2][0])

        if abs(points[4][1]) > self.maxwidth:
          self.maxwidth = abs(points[2][1])

        data_iterations[iters + 1].extend([
          [
            (points[0][0], points[0][1]),
            (points[2][0], points[2][1]),
          ],
          [
            (points[2][0], points[2][1]),
            (points[4][0], points[4][1]),
          ],
          [
            (points[4][0], points[4][1]),
            (points[3][0], points[3][1]),
          ],
          [
            (points[3][0], points[3][1]),
            (points[1][0], points[1][1]),
          ],
        ])

    self.serial('weierstrass', {'offset': offset, 'iterations': iterations})
    self.info('weierstrass: {0}'.format(sum([len(e) for e in data_iterations])))

    return data_iterations

  def canvas(self, npolygon: int, offset: float, iterations: int) -> None:
    data_iterations, minimize = [], (512, 512)

    for points in self.npolygon_triangles(npolygon):
      polygons = [
        [
          (points[0][0], points[0][1]),
          (points[1][0], points[1][1]),
        ],
        [
          (points[1][0], points[1][1]),
          (points[2][0], points[2][1]),
        ],
        [
          (points[2][0], points[2][1]),
          (points[0][0], points[0][1]),
        ],
      ]

      data_iterations.append(self.weierstrass(polygons, offset, iterations))

    if self.minimize is False:
      self.maxwidth = int(self.maxwidth * 1.189207115002721)
      minimize = (1024, 1024)

    effectives = self.maxwidth * 2 + 1
    geometries = Image.new('RGBA', (effectives, effectives), self.background)
    rgbapixels = ImageDraw.Draw(geometries)
    self.info('canvas.geometries: {0}x{0}'.format(effectives))

    for idx, triangles in enumerate(self.npolygon_triangles(npolygon)):
      rgbapixels.polygon(
        [
          (triangles[0][0] + self.maxwidth, triangles[0][1] + self.maxwidth),
          (triangles[1][0] + self.maxwidth, triangles[1][1] + self.maxwidth),
          (triangles[2][0] + self.maxwidth, triangles[2][1] + self.maxwidth),
        ],
        fill=self.itercolors.get(0, self.background)
      )

      for iters in range(iterations):
        rgba = self.itercolors.get(iters + 1, self.background)

        for points in data_iterations[idx][iters]:
          rgbapixels.polygon(
            [
              (points[2][0] + self.maxwidth, points[2][1] + self.maxwidth),
              (points[3][0] + self.maxwidth, points[3][1] + self.maxwidth),
              (points[4][0] + self.maxwidth, points[4][1] + self.maxwidth),
            ],
            fill=rgba
          )
          rgbapixels.line(
            (
              points[0][0] + self.maxwidth,
              points[0][1] + self.maxwidth,
              points[1][0] + self.maxwidth,
              points[1][1] + self.maxwidth,
            ),
            fill=rgba
          )

          self.pointsdata += 1

      self.pointsdata += 1

    self.info('canvas.rgbapixels: {0}'.format(self.pointsdata))

    #geometries.resize(minimize).save(self.id + '.png')
    #geometries.save(self.id + '.bmp')
    geometries.save(self.id + '.png')
    self.info('finish fractal geometries')

  def npolygon_triangles(self, npolygon: int) -> list:
    factor = 0.6180339887498949
    offset = factor + 1

    if npolygon == 3:
      x2nd = int(self.radius * math.cos(math.pi / 3))
      y2nd = int(self.radius * math.sin(math.pi / 3))

      return [
        [
          (0, 0),
          (-x2nd, -y2nd),
          (x2nd, -y2nd),
        ],
        [
          (0, 0),
          (self.radius, 0),
          (x2nd, y2nd),
        ],
        [
          (0, 0),
          (-x2nd, y2nd),
          (-self.radius, 0),
        ],
      ]

    if npolygon == 6:
      x2nd = int(self.radius * math.cos(math.pi / 3))
      y2nd = int(self.radius * math.sin(math.pi / 3))

      return [
        [
          (0, 0),
          (-x2nd, -y2nd),
          (x2nd, -y2nd),
        ],
        [
          (0, 0),
          (x2nd, -y2nd),
          (self.radius, 0),
        ],
        [
          (0, 0),
          (self.radius, 0),
          (x2nd, y2nd),
        ],
        [
          (0, 0),
          (x2nd, y2nd),
          (-x2nd, y2nd),
        ],
        [
          (0, 0),
          (-x2nd, y2nd),
          (-self.radius, 0),
        ],
        [
          (0, 0),
          (-self.radius, 0),
          (-x2nd, -y2nd),
        ],
      ]

    if npolygon == 7:
      x2nd = int(self.radius * math.cos(math.pi * 3  / 14))
      y2nd = int(self.radius * math.sin(math.pi * 3  / 14))
      x3rd = int(self.radius * math.cos(math.pi * 1  / 14))
      y3rd = int(self.radius * math.sin(math.pi * 1  / 14))
      x4th = int(self.radius * math.cos(math.pi * 5  / 14))
      y4th = int(self.radius * math.sin(math.pi * 5  / 14))

      x5th = int(self.radius * math.cos(math.pi * 1  / 3 ) * offset)
      y5th = int(self.radius * math.sin(math.pi * 1  / 3 ) * offset)

      x6th = int(self.radius * math.cos(math.pi * 8  / 21) * offset)
      y6th = int(self.radius * math.sin(math.pi * 8  / 21) * offset)
      x7th = int(self.radius * math.cos(math.pi * 1  / 21) * offset)
      y7th = int(self.radius * math.sin(math.pi * 1  / 21) * offset)

      x8th = int(self.radius * math.cos(math.pi * 2  / 21) * offset)
      y8th = int(self.radius * math.sin(math.pi * 2  / 21) * offset)
      x9th = int(self.radius * math.cos(math.pi * 5  / 21) * offset)
      y9th = int(self.radius * math.sin(math.pi * 5  / 21) * offset)

      xath = int(self.radius * math.cos(math.pi * 4  / 21) * offset)
      yath = int(self.radius * math.sin(math.pi * 4  / 21) * offset)
      xbth = int(self.radius * math.cos(math.pi * 10 / 21) * offset)
      ybth = int(self.radius * math.sin(math.pi * 10 / 21) * offset)

      xcth = int(self.radius * math.cos(math.pi * 3  / 14) * factor)
      ycth = int(self.radius * math.sin(math.pi * 3  / 14) * factor)
      xdth = int(self.radius * math.cos(math.pi * 19 / 42) * factor)
      ydth = int(self.radius * math.sin(math.pi * 19 / 42) * factor)
      xeth = int(self.radius * math.cos(math.pi * 5  / 42) * factor)
      yeth = int(self.radius * math.sin(math.pi * 5  / 42) * factor)

      return [
        [
          (0, 0),
          (0, -self.radius),
          (x2nd, -y2nd),
        ],
        [
          (0, 0),
          (x2nd, -y2nd),
          (x3rd, y3rd),
        ],
        [
          (0, 0),
          (x3rd, y3rd),
          (x4th, y4th),
        ],
        [
          (0, 0),
          (x4th, y4th),
          (-x4th, y4th),
        ],
        [
          (0, 0),
          (-x4th, y4th),
          (-x3rd, y3rd),
        ],
        [
          (0, 0),
          (-x3rd, y3rd),
          (-x2nd, -y2nd),
        ],
        [
          (0, 0),
          (-x2nd, -y2nd),
          (0, -self.radius),
        ],

        [
          (0, -self.radius),
          (-x5th, -self.radius - y5th),
          (x5th, -self.radius - y5th),
        ],
        [
          (x3rd, y3rd),
          (x3rd + x8th, y3rd - y8th),
          (x3rd + x9th, y3rd + y9th),
        ],
        [
          (-x3rd, y3rd),
          (-x3rd - x9th, y3rd + y9th),
          (-x3rd - x8th, y3rd - y8th),
        ],

        [
          (x4th, y4th),
          (x4th + xath, y4th + yath),
          (x4th - xbth, y4th + ybth),
        ],
        [
          (-x4th, y4th),
          (-x4th + xbth, y4th + ybth),
          (-x4th - xath, y4th + yath),
        ],

        [
          (x2nd + xcth, -y2nd - ycth),
          (x2nd + xcth + xdth, -y2nd - ycth + ydth),
          (x2nd, -y2nd),
        ],
        [
          (x2nd + xcth, -y2nd - ycth),
          (x2nd + xcth + xeth, -y2nd - ycth + yeth),
          (x2nd + xcth + xdth, -y2nd - ycth + ydth),
        ],
        [
          (x2nd + xcth, -y2nd - ycth),
          (x2nd + xcth + xcth, -y2nd - ycth - ycth),
          (x2nd + xcth + xeth, -y2nd - ycth + yeth),
        ],
        [
          (x2nd + xcth, -y2nd - ycth),
          (x2nd + xcth - xdth, -y2nd - ycth - ydth),
          (x2nd + xcth + xcth, -y2nd - ycth - ycth),
        ],
        [
          (x2nd + xcth, -y2nd - ycth),
          (x2nd + xcth - xeth, -y2nd - ycth - yeth),
          (x2nd + xcth - xdth, -y2nd - ycth - ydth),
        ],
        [
          (x2nd + xcth, -y2nd - ycth),
          (x2nd, -y2nd),
          (x2nd + xcth - xeth, -y2nd - ycth - yeth),
        ],

        [
          (-x2nd - xcth, -y2nd - ycth),
          (-x2nd, -y2nd),
          (-x2nd - xcth - xdth, -y2nd - ycth + ydth),
        ],
        [
          (-x2nd - xcth, -y2nd - ycth),
          (-x2nd - xcth - xdth, -y2nd - ycth + ydth),
          (-x2nd - xcth - xeth, -y2nd - ycth + yeth),
        ],
        [
          (-x2nd - xcth, -y2nd - ycth),
          (-x2nd - xcth - xeth, -y2nd - ycth + yeth),
          (-x2nd - xcth - xcth, -y2nd - ycth - ycth),
        ],
        [
          (-x2nd - xcth, -y2nd - ycth),
          (-x2nd - xcth - xcth, -y2nd - ycth - ycth),
          (-x2nd - xcth + xdth, -y2nd - ycth - ydth),
        ],
        [
          (-x2nd - xcth, -y2nd - ycth),
          (-x2nd - xcth + xdth, -y2nd - ycth - ydth),
          (-x2nd - xcth + xeth, -y2nd - ycth - yeth),
        ],
        [
          (-x2nd - xcth, -y2nd - ycth),
          (-x2nd - xcth + xeth, -y2nd - ycth - yeth),
          (-x2nd, -y2nd),
        ],
      ]

    raise RuntimeError('invalid npolygon number')

  def serial(self, code: str, parameters: dict) -> str:
    parameters.update({'radius': self.radius, 'minimize': self.minimize})

    self.id = '.'.join([
      code,
      hashlib.sha1(json.dumps(parameters).encode('utf8')).hexdigest(),
    ])

  def info(self, message) -> None:
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + f' {message}')

if __name__ == '__main__':
  fractal = FractalGeometry(int(5741 / 2), minimize=False)
  fractal.canvas(7, -1/3, 9)
