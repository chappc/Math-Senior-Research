#! /bin/bash
python make-art-description.py
python ray-tracing2.py art-description.ad art-description-shadow.jpeg
python test1.py art-description.ad art-description-shadow.jpeg