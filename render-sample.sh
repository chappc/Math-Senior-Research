#! /bin/bash
python make-art-description.py
python rayTracing.py art-description.ad art-description-shadow.jpeg
python test1.py art-description.ad art-description-shadow.jpeg
