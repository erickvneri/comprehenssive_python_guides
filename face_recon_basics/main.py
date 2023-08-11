#!/usr/bin/env python
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
import sys
import cv2
import logging
import numpy as np
import face_recognition
from datetime import datetime
from argparse import ArgumentParser

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

opencv_face_detect_config = dict(
    default=dict(scaleFactor=1.25, minNeighbors=6, minSize=(30, 30)),
    refined_v1=dict(scaleFactor=1.6, minNeighbors=6, minSize=(30, 30)),
    refined_v2=dict(scaleFactor=1.8, minNeighbors=6, minSize=(30, 30)),
)


def find_and_crop_faces(
    filename: str, profile: str
) -> list[str]:  # generated image file name
    faces_found: list[str] = []

    # read image file
    img = cv2.imread(filename)
    gray_scaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # load pretrained model
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # detect faces
    faces = face_cascade.detectMultiScale(
        gray_scaled, **opencv_face_detect_config[profile]
    )
    logging.info(f"faces detected: {len(faces)}")

    # write cropped faces into files
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 0)
        roi_color = img[y : y + h, x : x + w]

        # results into files
        file_name = "{}_{}".format(str(datetime.now()), filename)
        cv2.imwrite(file_name, roi_color)
        logging.info(f"cropped image located at: '{file_name}'")
        faces_found.append(file_name)

    return faces_found


def compare_faces(*filenames) -> float:
    file_a, file_b = filenames

    load_a = face_recognition.load_image_file(file_a)
    load_b = face_recognition.load_image_file(file_b)

    encoding_a = face_recognition.face_encodings(load_a)
    encoding_b = face_recognition.face_encodings(load_b)

    distance: list[float] = face_recognition.face_distance(encoding_a[0], encoding_b)
    percent = [(1 - dist) * 100 for dist in distance]
    return round(percent[0], 2)


def main():
    # Configure CLI
    cli = ArgumentParser()
    options = cli.add_subparsers(title="options", dest="subcommand")

    crop_service = options.add_parser("crop")
    crop_service.add_argument("--file", "-f", type=str, required=True)
    crop_service.add_argument(
        "--profile",
        "-p",
        choices=["default", "refined_v1", "refined_v2"],
        default="default",
    )

    compare_service = options.add_parser("compare")
    compare_service.add_argument("--compare-base", "-cb", type=str, required=True)
    compare_service.add_argument("--compare-target", "-ct", type=str, required=True)

    args = cli.parse_args()

    # Handle CLI requests
    if args.subcommand == "crop":
        filename = args.file
        cropped_image_files: list[str] = find_and_crop_faces(filename, args.profile)
    elif args.subcommand == "compare":
        result = compare_faces(args.compare_base, args.compare_target)
        logging.info(f"comparission result: {result}")


if __name__ == "__main__":
    main()
