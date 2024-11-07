#!/usr/bin/env python3

import sys
import json

from argparse import ArgumentParser

from label_stats import assign_labels


def argparser():
    ap = ArgumentParser()
    ap.add_argument('--threshold', type=float, default=0.5)
    ap.add_argument('textfile')
    ap.add_argument('labelfile')
    ap.add_argument('registers', help='R1[,R2...]')
    return ap


def process(textl, labell, args):
    textd = json.loads(textl)
    labeld = json.loads(labell)
    assert textd['id'] == labeld['id'], 'id mismatch'
    probabilities = labeld['register_probabilities']
    labels = assign_labels(probabilities, args.threshold)
    if labels & args.registers:
        assert 'register_probabilities' not in textd
        textd['register_probabilities'] = probabilities
        print(json.dumps(textd, ensure_ascii=False))


def main(argv):
    args = argparser().parse_args(argv[1:])
    args.registers = set(args.registers.split(','))

    with open(args.textfile) as textf:
        with open(args.labelfile) as labelf:
            for textl, labell in zip(textf, labelf):
                process(textl, labell, args)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
