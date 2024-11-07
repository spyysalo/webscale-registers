#!/usr/bin/env python3

import sys
import re
import matplotlib.pyplot as plt

import numpy as np
import seaborn as sns
import matplotlib.patheffects as path_effects

from argparse import ArgumentParser
from collections import OrderedDict

# regexes for stats lines
TOP_LEVEL_RE = re.compile(r'^([A-Z]{2}): ([0-9]+)')
SECOND_LEVEL_RE = re.compile(r'^ +([A-Z]{2}, [a-z{}]+): ([0-9]+)')
NO_REGISTER_RE = re.compile(r'.*?no register.*: ([0-9]+)')
TOTAL_RE = re.compile(r'^TOTAL: ([0-9]+)')

# color by label
COLOR_MAP = {
    'MT': (0.75, 0.50, 0.17),
    'LY': (0.5920891529639701, 0.6418467016378244, 0.1935069134991043),
    'SP': (0.9, 0.9, 0.9),
    #'ID': (0.9677975592919913, 0.44127456009157356, 0.5358103155058701),
    'ID': (0.98046875, 0.16015625, 0.10546875),
    #'NA': (0.22335772267769388, 0.6565792317435265, 0.8171355503265633),
    'NA': (0.0625, 0.55078125, 0.99609375),
    #'HI': (0.21044753832183283, 0.6773105080456748, 0.6433941168468681),
    'HI': (0.22265625, 0.66796875, 0.99609375),
    #'IN': (0.19783576093349015, 0.6955516966063037, 0.3995301037444499),
    'IN': (0.32421875, 0.83203125, 0.16015625),
    #'OP': (0.6423044349219739, 0.5497680051256467, 0.9582651433656727),
    'OP': (0.8046875, 0.0859375, 0.44921875),
    #'IP': (1.0, 0.80, 0.23),
    'IP': (0.96484375, 0.72265625, 0.10546875),
    'no label': (0.5, 0.5, 0.5),
}


def argparser():
    ap = ArgumentParser()
    ap.add_argument('--title')
    ap.add_argument('--save')
    ap.add_argument('stats')
    return ap


def parse_stats(fn):
    inner, outer, no_label = OrderedDict(), OrderedDict(), None
    with open(fn) as f:
        for l in f:
            m = TOP_LEVEL_RE.search(l)
            if m:
                label, count = m.groups()
                assert label not in inner
                inner[label] = int(count)
                continue
            m = SECOND_LEVEL_RE.search(l)
            if m:
                label, count = m.groups()
                assert label not in outer
                outer[label] = int(count)
                continue
            m = NO_REGISTER_RE.search(l)
            if m:
                assert no_label is None
                no_label = int(m.group(1))
                continue
            m = TOTAL_RE.search(l)
            if m:
                #print('total', m.groups())
                continue
            raise ValueError(f'failed to parse line: {l}')
    return inner, outer, no_label


def add_labels(ax, wedges, labels, distance):
    for i, wedge in enumerate(wedges):
        angle = (wedge.theta2 - wedge.theta1) / 2.0 + wedge.theta1
        x = distance * wedge.r * np.cos(np.radians(angle))
        y = distance * wedge.r * np.sin(np.radians(angle))
        text = ax.text(
            x, y, labels[i],
            ha='center', va='center',
            fontsize=10, color="black"
        )
        text.set_path_effects([
            path_effects.Stroke(linewidth=2, foreground='white'),
            path_effects.Normal()
        ])


def main(argv):
    args = argparser().parse_args(argv[1:])

    inner, outer, no_label = parse_stats(args.stats)

    inner['no label'] = no_label
    outer['no label'] = no_label

    assert sum(inner.values()) == sum(outer.values()), 'totals mismatch'

    fig, ax = plt.subplots(figsize=(8, 8))

    inner_labels = list(inner.keys())
    #inner_colors = sns.color_palette('Set2')
    inner_colors = [COLOR_MAP[i] for i in inner_labels]
    outer_colors = [
        inner_colors[inner_labels.index(k.split(',')[0])]
        for k in outer.keys()
    ]

    inner_wedges, _ = ax.pie(
        inner.values(),
        colors=inner_colors,
        radius=0.6,
    )
    outer_wedges, _ = ax.pie(
        outer.values(),
        labels=outer.keys(),
        colors=outer_colors,
        wedgeprops=dict(width=0.4, edgecolor='white'),
    )

    add_labels(ax, inner_wedges, inner_labels, 0.5)

    if args.title is not None:
        plt.title(args.title)

    if args.save is None:
        plt.show()
    else:
        plt.savefig(args.save)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
