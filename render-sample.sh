#! /bin/bash
python makeArtDescription.py;
python rayTracing.py art-description.ad art-description-shadow.jpeg;
python renderObject.py art-description.ad art-description-shadow.jpeg;
