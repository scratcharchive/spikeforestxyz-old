import sys
import os
thispath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(thispath, '..'))
from dendro_apps.spikeforestxyz.recording_summary.create_recording_summary import create_recording_summary


def test_create_recording_summary():
    url = 'https://fsbucket-dendro.flatironinstitute.org/dendro-uploads/9e302504/sha1/25/e6/60/25e660c238e3c576a14d5489eb8f0eb6832147a7'
    path = 'test1.nwb.lindi.json'
    _download_file(url, path)
    create_recording_summary(path)


def _download_file(url, path):
    import requests
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    test_create_recording_summary()
