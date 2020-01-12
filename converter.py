
import os
import sys
import glob
import shutil
import argparse

from PIL import Image


def conv2gif(src, dest, config):
    shutil.copy(src, dest)
    return True

def conv2jpg(src, dest, config):
    im = Image.open(src)
    try:
        im = im.convert("RGB")
    except:
        print('error convert {}'.format(src))
        return False

    im.thumbnail(config['size'], Image.BICUBIC)
    try:
        exif = im.info['exif']
        im.save(dest, "JPEG", exif=exif, quality=85)
    except:
        im.save(dest, "JPEG", quality=85)
    return True

def conv2video(src, dest, config):

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

def conv2audio(src, dest, config):

    command = "ffmpeg -i \"{}\" -vn -f ogg -c:a libopus -b:a 96k \
        -map_metadata 0 -threads 8 -y \"{}\"".format(src, dest)
    # command = "ffmpeg -i \"%s\" -vn -ar 44100 -ac 2 -f ogg -acodec libvorbis \
        # -ab 192k -map_metadata 0 -threads 8 -y \"%s\"".format(ini, new)
    os.system(command)

def conv2folder(source, output, depth, force, config):

    # supported formats
    formats = [
        (conv2jpg, '.jpg', ['.jpg', '.jpeg', '.tif',
                    '.tiff', '.png', '.bmp'], config['image']),
        (conv2gif, '.gif', ['.gif'], config['animation']),
        # (conv2video, '.mp4', ['.mov', '.mp4', '.avi', '.3gp', '.wmv',
        #               '.webm', '.mts', '.m2ts', '.mpg', '.vob',
        #               '.ts', '.flv', '.mkv'], config['video']),
        # (conv2audio, '.ogg', ['.flac', '.mp3', '.webm', '.mkv', '.mp4',
        #                 '.mov', '.ts', '.flv', '.avi'], config['audio']),
    ]

    src = os.path.dirname(os.path.abspath(source) + '/') + '/'
    dest = os.path.abspath(output) + '/'

    if depth < 0:
        print('max_depth', depth, src)
        return

    if not os.path.isdir(src):
        raise OSError('{} does not exist'.format(src))

    if not os.path.isdir(dest):
        if force or (input('Create {} [y/N]: '.format(dest)) == 'y'):
            os.makedirs(dest)
        else:
            sys.exit()

    print('src: {}'.format(src))

    for elem in sorted(glob.glob(src + '/*')):
        basename = os.path.basename(elem)
        name, ext = os.path.splitext(basename)
        srcNew = src + '/' + basename

        if '!' in basename:
            print('skipped: {}'.format(srcNew))
            continue

        check = False
        if os.path.isdir(elem):
            destNew = dest + '/' + basename
            conv2folder(srcNew, destNew, depth - 1, force, config)
            check = True

        for func, target, exts, conf in formats:
            if ext.lower() in exts:
                check = True
                destNew = dest + '/' + name + target
                if not os.path.isfile(destNew):
                    try:
                        func(srcNew, destNew, conf)
                    except:
                        print('error', srcNew, destNew)
                else:
                    break

        if not check:
            print('Error file {} type'.format(srcNew))

def main(config):

    conf = {
        'image': {'size': (1920, 1080)},
        'animation': {},
        'video': {},
        'audio': {},
    }

    conv2folder(
        config.src,
        config.dest,
        depth=config.max_depth,
        force=config.force,
        config=conf
    )


if __name__ in '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str)
    parser.add_argument('dest', type=str)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--max_depth', type=int, default=2)
    args = parser.parse_args()
    main(args)
