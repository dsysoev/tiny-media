# Photo utils

## Install

```shell
cd tiny-media/ 
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Face recognition

```bash
# find similar images into photo collection
python face_recognition.py -img target.jpg -folder /path/to/photo/collection/ --results results.csv
```
