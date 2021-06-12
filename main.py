import csv
import sys
from typing import List, Tuple
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

dist_dir = Path('dist')
dist_dir.mkdir(exist_ok=True)
len_lable = 'TripLength'
traffic_label = 'Traffic'
type_label = 'VehicleType'


def to_percentage(arr):
    return np.array(arr) / sum(arr)


def save_fig(
    cnt: List[Tuple[int, int]],
    title: str = 'result',
):
    print(f'Save "{title}"...')
    lengths = [x[0] for x in cnt]
    traffics = [x[1] for x in cnt]
    fig, x1 = plt.subplots()
    x1.autoscale()
    x1.set_xlabel(len_lable)
    x1.set_ylabel(traffic_label)
    x1.bar(lengths, traffics)
    # Draw accumulation
    traffics_p = to_percentage(traffics)
    traffics_acc = traffics[::]
    for i in range(1, len(traffics_p)):
        traffics_p[i] += traffics_p[i - 1]
        traffics_acc[i] += traffics_acc[i - 1]
    x2 = x1.twinx()
    x2.set_ylabel(f'{traffic_label} (accumulate)')
    x2.plot(lengths, traffics_p, color='red')
    # Find 10x % point
    i = 10
    for l, tp, t in zip(lengths, traffics_p, traffics_acc):
        if 100 * tp >= i:
            print(f'{i}%: {l} ({t})')
            i += 10
    if i <= 100:
        print(f'100%: {lengths[-1]} ({traffics_acc[-1]})')
    # # Debug
    # print(*zip(lengths, traffics_p, traffics_acc), sep='\n')
    # Save figure
    fig.tight_layout()
    x1.set_title(title)
    plt.savefig(f'{dist_dir}/{title}.png', bbox_inches='tight')
    plt.clf()
    # Save csv
    with open(dist_dir / f'{title}.csv', 'w') as f:
        header = 'Length,Traffic,AccTraffic,AccTrafficPercentage'
        f.write(header + '\n')
        for r in zip(lengths, traffics, traffics_acc, traffics_p):
            f.write(','.join(map(str, r)) + '\n')


if __name__ == '__main__':
    root_dir = Path(sys.argv[1])
    if not root_dir.is_dir():
        print(f'{root_dir} dir not found!')
        exit(1)
    cnt_all = defaultdict(int)
    cnt_small = defaultdict(int)
    for p in root_dir.glob('*.csv'):
        dr = csv.DictReader(p.open())
        for row in dr:
            l = int(float(row[len_lable]))
            cnt_all[l] += 1
            if row[type_label] in {'31', '41'}:
                cnt_small[l] += 1
    cnt_all = sorted([(k, v) for k, v in cnt_all.items()])
    save_fig(cnt_all, f'{root_dir}-result')
    cnt_small = sorted([(k, v) for k, v in cnt_small.items()])
    save_fig(cnt_small, f'{root_dir}-small')
