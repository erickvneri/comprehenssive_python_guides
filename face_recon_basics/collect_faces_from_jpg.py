# MIT License
#
# Copyright (c) 2022 erickvneri
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging
import cv2
import sys
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# path parameter passed
# at script execution
#
# example:
# $ python collect_faces_from_jpg image.jpg
_file = sys.argv[1]


def main():
    """
    Basic python script which implements
    OpenCV and extracts faces from jpg images.
    """
    img = cv2.imread(_file)
    gray_scaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(
        gray_scaled, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30)
    )
    logging.info(f"faces detected: {len(faces)}")

    # process faces
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 0)
        roi_color = img[y : y + h, x : x + w]

        # dump results into files
        file_name = f"crop_{_file}"
        cv2.imwrite(file_name, roi_color)
        logging.info(f"{file_name} file generated")


if __name__ == "__main__":
    main()
