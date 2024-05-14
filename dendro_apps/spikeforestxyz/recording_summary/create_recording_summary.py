from typing import List
import json
import os
import lindi


def create_recording_summary(
    *,
    input: str,
    output: str
):
    from .nwbextractors import NwbRecordingExtractor, NwbSortingExtractor
    f = lindi.LindiH5pyFile.from_lindi_file(input, local_cache=lindi.LocalCache())
    rec = NwbRecordingExtractor(h5py_file=f)  # type: ignore
    sorting_true = NwbSortingExtractor(h5py_file=f)  # type: ignore
    sorting_true_figurls = _create_sorting_figurls(sorting=sorting_true)
    x = {
        'version': '2',
        'num_channels': int(rec.get_num_channels()),
        'channel_ids': rec.get_channel_ids().tolist(),
        'samplerate': float(rec.get_sampling_frequency()),
        'duration_sec': float(rec.get_num_frames() / rec.get_sampling_frequency()),
        'sorting_true': {
            'unit_ids': sorting_true.get_unit_ids().tolist(),  # type: ignore
            'figurls': sorting_true_figurls
        },
        'figurls': []
    }
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    with open(output, 'w') as f:
        json.dump(x, f, indent=4)


def _create_sorting_figurls(*, sorting):  # type: ignore
    import spikeinterface as si
    sorting: si.BaseSorting = sorting
    figurls = []
    figurls.append({
        'name': 'autocorrelograms',
        'url': _create_autocorrelograms_figurl(sorting=sorting)
    })
    return figurls


def _create_autocorrelograms_figurl(*, sorting):  # type: ignore
    import sortingview.views as vv
    import spikeinterface as si
    from .helpers.compute_correlogram_data import compute_correlogram_data
    sorting: si.BaseSorting = sorting
    unit_ids = sorting.get_unit_ids()
    autocorrelograms: List[vv.AutocorrelogramItem] = []
    for unit_id in unit_ids:
        times = sorting.get_unit_spike_train(unit_id=unit_id)
        times = times / sorting.get_sampling_frequency()
        a = compute_correlogram_data(spike_train_1=times, spike_train_2=None, window_size_msec=50, bin_size_msec=1)
        bin_edges_sec = a["bin_edges_sec"]
        bin_counts = a["bin_counts"]
        autocorrelograms.append(vv.AutocorrelogramItem(unit_id=unit_id, bin_edges_sec=bin_edges_sec, bin_counts=bin_counts))

    view = vv.Autocorrelograms(autocorrelograms)
    return view.url(label='autocorrelograms')
