#!/usr/bin/env python3

import sys
import json

from collections import defaultdict
from argparse import ArgumentParser

from label_stats import assign_labels


def argparser():
    ap = ArgumentParser()
    ap.add_argument('--thresholds', default='0.5', metavar='FLOAT[,FLOAT...]')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('jsonl', nargs='+')
    return ap


def process(fn, stats, args):
    min_threshold = min(args.thresholds)
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            if args.limit is not None and ln > args.limit:
                break
            d = json.loads(l)
            r = {
                k: v for k, v in d['register_probabilities'].items()
                if v >= min_threshold    # minor optimization
            }
            for t in args.thresholds:
                labels = assign_labels(r, t)
                stats[t][' '.join(sorted(labels))] += 1


def main(argv):
    args = argparser().parse_args(argv[1:])
    args.thresholds = [float(t) for t in args.thresholds.split(',')]

    stats = defaultdict(lambda: defaultdict(int))
    for fn in args.jsonl:
        process(fn, stats, args)

    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
