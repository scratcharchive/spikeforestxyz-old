import time
import uuid
import shutil
import numpy as np
import h5py
import lindi
import kachery_cloud as kcl
from .helpers.compute_correlogram_data import compute_correlogram_data
# from .nwbextractors import NwbRecordingExtractor, NwbSortingExtractor


def create_recording_summary(
    nwb_lindi_fname: str
):
    staging_area = lindi.StagingArea.create(dir=nwb_lindi_fname + '.d')
    f = lindi.LindiH5pyFile.from_lindi_file(
        nwb_lindi_fname,
        mode='r+',
        staging_area=staging_area,
        local_cache=lindi.LocalCache()
    )
    # rec = NwbRecordingExtractor(h5py_file=f)  # type: ignore
    # sorting_true = NwbSortingExtractor(h5py_file=f)  # type: ignore

    # Load the spike times from the units group
    units_group = f['/units']
    assert isinstance(units_group, h5py.Group)
    print('Loading spike times')
    spike_times = units_group['spike_times'][()]  # type: ignore
    spike_times_index = units_group['spike_times_index'][()]  # type: ignore
    num_units = len(spike_times_index)
    total_num_spikes = len(spike_times)
    print(f'Loaded {num_units} units with {total_num_spikes} total spikes')

    # Compute autocorrelograms for all the units
    print('Computing autocorrelograms')
    auto_correlograms = []
    p = 0
    timer = time.time()
    for i in range(num_units):
        spike_train = spike_times[p:spike_times_index[i]]
        elapsed = time.time() - timer
        if elapsed > 2:
            print(f'Computing autocorrelogram for unit {i + 1} of {num_units} ({len(spike_train)} spikes)')
            timer = time.time()
        r = compute_correlogram_data(
            spike_train_1=spike_train,
            spike_train_2=None,
            window_size_msec=100,
            bin_size_msec=1
        )
        bin_edges_sec = r['bin_edges_sec']
        bin_counts = r['bin_counts']
        auto_correlograms.append({
            'bin_edges_sec': bin_edges_sec,
            'bin_counts': bin_counts
        })
        p = spike_times_index[i]
    autocorrelograms_array = np.zeros(
        (num_units, len(auto_correlograms[0]['bin_counts'])),
        dtype=np.uint32
    )
    for i, ac in enumerate(auto_correlograms):
        autocorrelograms_array[i, :] = ac['bin_counts']
    bin_edges_array = np.zeros(
        (num_units, len(auto_correlograms[0]['bin_edges_sec'])),
        dtype=np.float32
    )
    for i, ac in enumerate(auto_correlograms):
        bin_edges_array[i, :] = ac['bin_edges_sec']

    # Create a new dataset in the units group to store the autocorrelograms
    print('Writing autocorrelograms to output file')
    ds = units_group.create_dataset('acg', data=autocorrelograms_array)
    ds.attrs['description'] = 'the autocorrelogram for each spike unit'
    ds.attrs['namespace'] = 'hdmf-common'
    ds.attrs['neurodata_type'] = 'VectorData'
    ds.attrs['object_id'] = str(uuid.uuid4())

    ds = units_group.create_dataset('acg_bin_edges', data=bin_edges_array)
    ds.attrs['description'] = 'the bin edges in seconds for the autocorrelogram for each spike unit'
    ds.attrs['namespace'] = 'hdmf-common'
    ds.attrs['neurodata_type'] = 'VectorData'
    ds.attrs['object_id'] = str(uuid.uuid4())

    # Update the colnames attribute of the units group
    colnames = units_group.attrs['colnames']
    assert isinstance(colnames, np.ndarray)
    colnames = colnames.tolist()
    colnames.append('acg')
    colnames.append('acg_bin_edges')
    units_group.attrs['colnames'] = colnames

    f.flush()  # write changes to the file

    def on_store_blob(filename: str):
        url = kcl.store_file(filename)
        return url

    def on_store_main(filename: str):
        shutil.copyfile(filename, nwb_lindi_fname)
        return nwb_lindi_fname

    staging_store = f.staging_store
    assert staging_store is not None
    print('Uploading supporting files')
    f.upload(
        on_upload_blob=on_store_blob,
        on_upload_main=on_store_main
    )

