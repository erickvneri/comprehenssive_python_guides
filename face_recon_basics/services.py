#!/usr/bin/env python
# MIT License
#
# Copyright (c) 2023 erickvneri
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
import cv2
import face_recognition
import os
from datetime import datetime


CWD = os.path.dirname(os.path.realpath(__file__))
PRETRAINED_MODEL_BASE = cv2.data.haarcascades


def detect_faces(filename: str, profile: str = "default", output_filename: str = None):
    result: list[str] = None
    model = PRETRAINED_MODEL_BASE + "haarcascade_frontalface_default.xml"
    classifier = cv2.CascadeClassifier(model)
    face_classifier_configs = dict(
        default=dict(scaleFactor=1.25, minNeighbors=6, minSize=(30, 30)),
        v1=dict(scaleFactor=1.6, minNeighbors=6, minSize=(30, 30)),
        v2=dict(scaleFactor=1.8, minNeighbors=6, minSize=(30, 30)),
    )

    # read file
    asset = cv2.imread(filename)
    gray_scaled = cv2.cvtColor(asset, cv2.COLOR_BGR2GRAY)

    # detect faces vector
    faces = classifier.detectMultiScale(asset, **face_classifier_configs[profile])
    print("detected faces", len(faces))

    if output_filename:
        if len(faces) > 1:
            location = CWD + "/" + output_filename
            os.mkdir(location)
            os.chdir(location)

        prefix_count = 0
        for x, y, w, h in faces:
            cv2.rectangle(asset, (x, y), (x + w, y + h), (0, 0, 0), 0)
            roi_color = asset[y : y + h, x : x + w]

            # results into files
            prefix = prefix_count and f"({prefix_count})_" or ""
            file_name = "{}{}".format(prefix, output_filename)
            cv2.imwrite(file_name, roi_color)
            prefix_count += 1

        os.chdir(CWD)


def recognition(base_file: str, target_file: str) -> float:
    load_base = face_recognition.load_image_file(base_file)
    load_target = face_recognition.load_image_file(target_file)
    encoding_base = face_recognition.face_encodings(load_base)
    encoding_target = face_recognition.face_encodings(load_target)
    distance: list[float] = face_recognition.face_distance(
        encoding_base[0], encoding_target
    )
    percent = [(1 - dist) * 100 for dist in distance]
    return round(percent[0], 2)


def detect_eyes(filename: str, profile: str):
    model = PRETRAINED_MODEL_BASE + "haarcascade_eye.xml"
    classifier = cv2.CascadeClassifier(model)
    pass


def detect_smile(filename: str, profile: str):
    model = PRETRAINED_MODEL_BASE + "haarcascade_smile.xml"
    classifier = cv2.CascadeClassifier(model)
    pass
