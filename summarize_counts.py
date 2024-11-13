#!/usr/bin/env python3

import sys
import json

from collections import defaultdict
from argparse import ArgumentParser

from label_stats import (
    LABEL_HIERARCHY,
    TOP_LEVEL_LABELS,
    LABEL_MAP,
    NO_LABEL,
    HYBRID_LABEL,
)


def argparser():
    ap = ArgumentParser()
    ap.add_argument('json', nargs='+')
    return ap


def is_hybrid(labels):
    return (sum(l in TOP_LEVEL_LABELS for l in labels) > 1 or
            sum(l not in TOP_LEVEL_LABELS for l in labels) > 1)


def summarize(counts, args):
    total = sum(counts.values())
    stats = defaultdict(int)
    for label_str, count in counts.items():
        if not label_str:
            stats[NO_LABEL] += count
            continue
        labels = set(label_str.split(' '))
        if is_hybrid(labels):
            stats[HYBRID_LABEL] += count
        else:
            for label in labels:
                key = LABEL_MAP[label]
                stats[key] += count
    return stats, total


def main(argv):
    args = argparser().parse_args(argv[1:])

    totals = defaultdict(lambda: defaultdict(int))
    for i, fn in enumerate(args.json):
        with open(fn) as f:
            d = json.load(f)
        if i > 0:
            assert d.keys() == totals.keys(), 'thresholds mismatch'
        for t in d:
            for k, v in d[t].items():
                totals[t][k] += v

    def label_string(k):
        if k is NO_LABEL:
            return 'no register'
        elif k[1] is None:
            return k[0]
        else:
            return f'    {k[0]}, {k[1].strip("{}")}'

    for threshold in sorted(totals.keys()):
        stats, total = summarize(totals[threshold], args)

        # For each top-level label p, fill in implicit "other" 2nd-level
        # entry so that 2nd-level counts add up to top-level count
        for p in TOP_LEVEL_LABELS:
            parent_total = stats.get((p, None), 0)
            if parent_total:
                child_total = sum(stats.get((p, c), 0) for c in LABEL_HIERARCHY[p])
                stats[(p, '{other}')] = parent_total - child_total

        keyf = lambda k: (k[0] or '~', k[1] or '')    # sort order for None
        print(threshold)
        for k in sorted(stats.keys(), key=keyf):
            print(f'{label_string(k)}: {stats[k]} ({stats[k]/total:.1%})')
        print(f'TOTAL: {total}')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
