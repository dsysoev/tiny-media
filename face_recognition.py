
import argparse

from deepface import DeepFace


if __name__ in '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-img', type=str, help='path to source image')
    parser.add_argument('-folder', type=str, help='path to image database folder')
    parser.add_argument('--results', default='results.csv', type=str, help='path output file with results')
    parser.add_argument('--function', default='find', type=str)
    parser.add_argument('--model', default='Facenet512', type=str)
    parser.add_argument('--detector_backend', default='opencv', type=str)
    parser.add_argument('--prog_bar', default=False, type=bool)
    args = parser.parse_args()

    if args.function == 'find':
        model = DeepFace.build_model(args.model)
        df = DeepFace.find(img_path=args.img,
                           model=model,
                           enforce_detection=False,
                           detector_backend=args.detector_backend,
                           db_path=args.folder,
                           prog_bar=args.prog_bar)

        df['source'] = str(args.img)
        df.to_csv(path_or_buf=args.results, header=True)
    else:
        raise NotImplementedError('function {} does not implemented'.format(args.function))
