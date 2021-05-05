
import os
import sys
import shutil
import argparse
import datetime

import exifread


class bcolors:
    ANSWER = '\033[91m'
    ENDC = '\033[0m'


def answer_bool(text, force=False):
    text = bcolors.ANSWER + "%s [Y/n/q] " % text + bcolors.ENDC
    if force:
        print(text)
        return True
    answer = input(text)
    if answer == 'y' or answer == 'Y' or answer == '':
        return True
    elif answer == 'Q' or answer == 'q':
        print("You have completed the program")
        sys.exit()
    else:
        return False


def image_datetime(srcname):
    # Open image file for reading (binary mode)
    with open(srcname, 'rb') as f:
        # Return Exif tags
        tags = exifread.process_file(f)

    if 'EXIF DateTimeOriginal' not in tags:
        mtime = os.stat(srcname)[8]
        t = datetime.datetime.fromtimestamp(mtime)
        return t.strftime('%Y%m%d')

    datename = str(tags['EXIF DateTimeOriginal'])
    return datename.replace(':', '')[:8]


def collect_view(src, out, force=False, template_name=''):

    if answer_bool("Move media from original source ?", force=force):
        action = shutil.move
    else:
        action = shutil.copy

    if not os.path.isdir(src):
        raise Exception("Folder does not exist {}".format(src))

    if os.path.isdir(out) == False:
        raise Exception("Folder does not exist {}".format(out))

    data = {}
    for root, dirnames, filenames in os.walk(src):
        # skip folder
        if root.endswith('.medresframes'):
            continue
        for filename in filenames:
            srcname = os.path.join(root, filename)
            if not os.path.isfile(srcname):
                continue
            if srcname.endswith('.deletemarker'):
                continue
            date = image_datetime(srcname)
            if date not in data:
                data[date] = []
            data[date].append(srcname)


    for key in sorted(data):
        display = []
        for filename in data[key]:
            _, ext = os.path.splitext(filename)
            if ext.lower() in ['.jpg', '.jpeg', '.gif']:
                display.append(filename)

        if display and not template_name:
            ls = "'" + "' '".join(display) + "'"
            call = "montage {:} -auto-orient -geometry 200x200+5+5 -tile 5x -shadow :- | display".format(ls)
            os.system(call)

        print('Selected images: ')
        for filename in data[key]:
            print("{} {}".format('show' if filename in display else 'not show', filename))

        eventname = "{:}/{:}".format(key[:4], key)
        if not template_name:
            answer = input('Set folder name ?\n{}'.format(eventname))
            eventname = answer.strip()
        else:
            eventname = template_name

        for i, filename in enumerate(data[key]):
            foldername = os.path.join(out, key[:4], key + ' ' + eventname) + '/'
            dirfolder = os.path.dirname(foldername)
            outname = os.path.join(foldername, os.path.basename(filename))

            if not os.path.exists(dirfolder):
                if answer_bool("Create folder %s ?" % (dirfolder), force=force):
                    os.makedirs(dirfolder)
                else:
                    break

            if not os.path.isfile(outname):
                print("{} {:} {:}".format(action.__name__, filename, outname))
                action(filename, outname)
            else:
                print('file {} already exist'.format(filename))


if __name__ in '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str)
    parser.add_argument('dest', type=str)
    parser.add_argument('-template_name', type=str, default='')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    collect_view(args.src, args.dest, args.force, args.template_name)
