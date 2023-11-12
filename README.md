# Photo utils

# Install

```shell
cd tiny-media/ 
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Tools

## Collect photos and video from phone

```bash
# Collect (copy or move) photos and video from source folder to destination folder
# Each photo day move to new folder with following name: 
# `{DESTINATION_PATH}/YYYY/YYYYmmDD {template_name}`
# For skip questions use option `--force`
python collect.py /path/to/source/ /path/to/destination/ -template_name TEST
```

## Convert images to thumbnail

```bash
# convert images to thumbnail
python converter.py /path/to/source/ /path/to/destination/
```

## Face recognition

```bash
# find similar images into photo collection
python face_recognition.py -img target.jpg -folder /path/to/photo/collection/ --results results.csv
# File with photo representation was created (/path/to/photo/collection/representation_vgg_face.pkl)

# slow but more accurate preset
python face_recognition.py -img target.jpg -folder /path/to/photo/collection/ --results results.csv --detector_backend retinaface
```
