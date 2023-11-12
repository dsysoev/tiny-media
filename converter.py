
import argparse
import os
import shutil
import sys
from typing import NoReturn, Tuple, Dict, List

import numpy as np
import torch
import tqdm
from torch.utils.data import Dataset, DataLoader
from torchvision.io import read_image, write_jpeg
from torchvision.transforms import v2


class ImageDataset(Dataset):
    """Image dataset."""

    def __init__(self, tasks, transform=None):
        """
        Arguments:
            tasks (List[Tuple[str, str]]): Tuple (input_path, output_path)
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.tasks = tasks
        self.transform = transform

    def __len__(self):
        return len(self.tasks)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        # print(idx)
        src_path, target_path = self.tasks[idx]
        # print(src_path)
        try:
            image = read_image(src_path)
        except RuntimeError:
            return {'image': np.zeros((1, 1, 1)), 'target_path': target_path}

        if self.transform:
            image = self.transform(image)

        return {'image': image, 'target_path': target_path}


def conv2gif(src: str, dest: str, config: Dict) -> bool:

    shutil.copy(src, dest)
    return True


def conv2video(src: str, dest: str, config: Dict) -> bool:

    # slow VP9
    # first pass
    # command = "ffmpeg -y -i \"{}\" -vf scale=1280:720:force_original_aspect_ratio=decrease \
    #     -c:v libvpx-vp9 -pass 1 -b:v 1000K -threads 8 \
    #     -speed 4 -tile-columns 6 -frame-parallel 1 -an -f webm \
    #     /dev/null;".format(src)
    # os.system(command)
    # second pass
    # command = "ffmpeg -i \"{}\" -vf scale=1280:720:force_original_aspect_ratio=decrease \
    #     -c:v libvpx-vp9 -pass 2 -b:v 1000K -threads 8 \
    #     -speed 2 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 \
    #     -lag-in-frames 25 -c:a libopus -b:a 64k -f webm \"{}\"".format(src, dest)
    # os.system(command)

    # fast MP4
    command = "ffmpeg -i \"{}\" -vf scale=854:480 \
        -c:v libx264 -preset slow -pix_fmt yuv420p \
        -b:v 1000K -minrate 500k -maxrate 2000k -bufsize 2000k \
        -c:a aac -b:a 128k -f mp4 \"{}\"".format(src, dest)
    os.system(command)
    return True


def conv2audio(src: str, dest: str, config: Dict) -> bool:

    command = "ffmpeg -i \"{}\" -vn -f ogg -c:a libopus -b:a 96k \
        -map_metadata 0 -threads 8 -y \"{}\"".format(src, dest)
    # command = "ffmpeg -i \"%s\" -vn -ar 44100 -ac 2 -f ogg -acodec libvorbis \
        # -ab 192k -map_metadata 0 -threads 8 -y \"%s\"".format(ini, new)
    os.system(command)
    return True


def create_tasks(source: str, output: str, depth: int, config: Dict) -> Tuple[list[Tuple[str, str]], Dict[str, list]]:

    src = os.path.dirname(os.path.abspath(source) + '/') + '/'
    dest = os.path.abspath(output) + '/'

    if not os.path.isdir(src):
        raise OSError('{} does not exist'.format(src))

    if not os.path.isdir(dest):
        if input('Create {} [y/N]: '.format(dest)) == 'y':
            os.makedirs(dest)
        else:
            sys.exit()

    print('src  : {}\ndest : {}\n'.format(src, dest))

    tasks = []
    other = {}
    for root, dirs, files in sorted(os.walk(src)):
        actual_depth = root[len(src):].count(os.sep) + 1
        if actual_depth > depth:
            continue

        folder_name = os.path.basename(os.path.normpath(root))
        if '!' in folder_name:
            print('folder {} was skipped (! exist in name)'.format(root))
            continue

        for f in files:
            elem = os.path.join(root, f)
            name, ext = os.path.splitext(os.path.basename(elem))
            ext = ext.lower()

            if ext not in config['image']['ext_list']:
                # format does not supported yet
                if ext not in other:
                    other[ext] = []
                other[ext].append(elem)
                continue

            out = os.path.join(dest, root[len(src):], name + '.jpg')

            if os.path.exists(out):
                continue

            tasks.append((elem, out))

    return tasks, other


def dataset_thumbnail(tasks: List[Tuple[str, str]], config: Dict) -> NoReturn:

    resize = v2.Resize(size=config['image']['size'],
                       antialias=True,
                       interpolation=v2.InterpolationMode.BICUBIC)

    dataset = ImageDataset(tasks=tasks, transform=resize)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=10)

    quality = config['image']['quality']
    for sample in tqdm.tqdm(dataloader):
        target_path = sample['target_path'][0]
        image = sample['image'][0]

        if image.shape == (1, 1, 1):
            print(f'error reading file {target_path}')
            continue

        dirname = os.path.dirname(target_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        try:
            write_jpeg(image, target_path, quality=quality)
        except RuntimeError:
            print(f'error converting file {target_path}')


def main() -> NoReturn:
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str)
    parser.add_argument('dest', type=str)
    parser.add_argument('--max_depth', type=int, default=2)
    args = parser.parse_args()

    config = {
        'image': {'size': 960, 'quality': 85, 'ext_list': ['.jpg', '.png']},
        'animation': {},
        'video': {},
        'audio': {},
    }

    tasks, other = create_tasks(
        args.src,
        args.dest,
        args.max_depth,
        config=config
    )

    print('number of tasks : {}'.format(len(tasks)))
    for key, items in other.items():
        print(f'file extension: "{key}" len: {len(items)}')

    # converting images
    dataset_thumbnail(tasks, config)

    print('Done')


if __name__ in '__main__':
    main()
