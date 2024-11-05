import sys
import json

from math import isclose
from argparse import ArgumentParser


def argparser():
    ap = ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('preds1')
    ap.add_argument('preds2')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--threshold', type=float, default=None)
    ap.add_argument('--rel_tol', type=float, default=0.01)
    ap.add_argument('--min-chars', type=int, default=10)
    return ap


def compare(sl, l1, l2, args):
    sd, d1, d2 = json.loads(sl), json.loads(l1), json.loads(l2)
    assert sd['id'] == d1['id'] == d2['id']

    text = sd['text']
    r1, r2 = d1['register_probabilities'], d2['register_probabilities'],
    assert r1.keys() == r2.keys()

    close, short, total = 0, 0, 0
    for k in r1:
        if args.threshold is not None:
            r1[k] = r1[k] > args.threshold
            r2[k] = r2[k] > args.threshold
        if len(text) < args.min_chars:
            short += 1
        elif isclose(r1[k], r2[k], rel_tol=args.rel_tol):
            close += 1
        else:
            print(d1['id'], k, r1[k], r2[k], file=sys.stderr)
        total += 1
    return close, short, total


def main(argv):
    args = argparser().parse_args(argv[1:])

    sum_close, sum_short, sum_total = 0, 0, 0
    with open(args.source) as sf:
        with open(args.preds1) as p1:
            with open(args.preds2) as p2:
                for i, (sl, l1, l2) in enumerate(zip(sf, p1, p2), start=1):
                    if args.limit is not None and i > args.limit:
                        break
                    close, short, total = compare(sl, l1, l2, args)
                    sum_close += close
                    sum_short += short
                    sum_total += total

    sum_other = sum_total - sum_close - sum_short
    print(f'short: {sum_short}/{sum_total} ({sum_short/sum_total:.1%})')
    print(f'close: {sum_close}/{sum_total} ({sum_close/sum_total:.1%})')
    print(f'other: {sum_other}/{sum_total} ({sum_other/sum_total:.1%})')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
