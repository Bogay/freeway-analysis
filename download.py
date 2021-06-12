import shutil
import time
import sys
import re
import tarfile
import tempfile
from pathlib import Path
import requests as rq

header = 'VehicleType,DetectionTime_O,GantryID_O,DetectionTime_D,GantryID_D,TripLength,TripEnd,TripInformation'


def get_url(d, h):
    url_t = 'https://tisvcloud.freeway.gov.tw/history/TDCS/M06A/%s/%02d/TDCS_M06A_%s_%02d0000.csv'
    return url_t % (d, h, d, h)


if __name__ == '__main__':
    day = sys.argv[1]
    if not re.match(r'^\d{8,8}$', day):
        print('Invalid day format, should be like 20210611')
        exit(1)
    # Check existence
    root_url = f'https://tisvcloud.freeway.gov.tw/history/TDCS/M06A/{day}'
    resp = rq.get(root_url)
    if not resp.ok:
        # It may be tar.gz file
        resp = rq.get(
            f'https://tisvcloud.freeway.gov.tw/history/TDCS/M06A/M06A_{day}.tar.gz'
        )
        # Extract
        if resp.ok:
            print('Tarball found! Extracting...')
            # Make directory
            root_dir = Path(day)
            root_dir.mkdir(exist_ok=True)
            with tempfile.NamedTemporaryFile() as tmp_f:
                with open(tmp_f.name, 'wb') as f:
                    f.write(resp.content)
                with tarfile.open(tmp_f.name) as tf:
                    tf.extractall(root_dir)
                # Write header
                for c in root_dir.glob('**/*.csv'):
                    o = c.read_text()
                    with c.open('w') as f:
                        f.write(header + '\n')
                        f.write(o)
                # Remove empty dir
                shutil.rmtree(root_dir / 'M06A')
            exit(0)
        print('It seems that the day has no data')
        print(f'Try visit {root_url}')
        exit(1)
    # Make directory
    root_dir = Path(day)
    root_dir.mkdir(exist_ok=True)
    # Download data
    for i in range(24):
        url = get_url(day, i)
        resp = rq.get(url)
        assert resp.ok, (resp.status_code, resp.text)
        with open(root_dir / url.split('/')[-1], 'w') as f:
            f.write(header + '\n')
            f.write(resp.text)
        print(f'Finish download {i}')
        if i != 23:
            time.sleep(40)
