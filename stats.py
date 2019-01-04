import os
import datetime
import argparse
import collections


if __name__ in '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-folder', default='./', type=str)
    parser.add_argument('--filename', default='stats.csv', type=str)

    args = parser.parse_args()

    root = args.folder
    rootlen = len(root)

    cnt_dirs = 0
    full_files = []
    for root, dirs, files in os.walk(root,):
        # skip folders starts with dot
        if root[rootlen:rootlen + 1] == '.':
            continue
        cnt_dirs += 1
        full_files += [os.path.join(root, name) for name in files]

    size_files = 0
    output = []
    extdata = collections.defaultdict(int)
    for file_path in reversed(sorted(full_files)):
        size = os.path.getsize(file_path)
        _, ext = os.path.splitext(file_path)
        extdata[ext.lower()] += 1
        size_files += size
        output.append("{},file,{}".format(size, file_path[rootlen:]))

    extdata = collections.OrderedDict(
        sorted(extdata.items(), key=lambda t: "{:06d}".format(t[1]) + str(t[0]))
        )

    with open(args.filename, 'w') as f:
        f.write('# datetime: {}\n'.format(datetime.datetime.now()))
        f.write('# number of dirs : {}\n'.format(cnt_dirs))
        f.write('# number of files: {}\n'.format(sum(extdata.values())))
        f.write('# size of files  : {}\n'.format(size_files))
        f.write('# file extensions stats\n')
        for key, value in extdata.items():
            f.write('# {:10s} number of files : {}\n'.format(key, value))
        f.write('size,type,filepath\n')
        f.write("\n".join(output))

    print('{} file was created'.format(args.filename))
