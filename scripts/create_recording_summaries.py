import dendro.client as dc


def create_recording_summaries():
    dendro_project_id = '9e302504'  # https://dendro.vercel.app/project/9e302504?tab=project-home

    project = dc.load_project(dendro_project_id)
    batch_id = dc.create_batch_id()

    all_recording_names = _get_all_recording_names(project)
    for name in all_recording_names:
        print('=====================')
        print(name)
        output_fname = f'recording_summaries/{name}.nwb.lindi.json'
        ff = project.get_file(output_fname)
        if ff is not None:
            print("Skipping - already exists")
            continue
        dc.submit_job(
            project=project,
            processor_name='spikeforestxyz.recording_summary',
            input_files=[
                dc.SubmitJobInputFile(
                    name='input',
                    file_name=f'recordings/{name}.nwb.lindi.json'
                )
            ],
            output_files=[
                dc.SubmitJobOutputFile(
                    name='output',
                    file_name=output_fname
                )
            ],
            parameters=[],
            batch_id=batch_id,
            required_resources=dc.DendroJobRequiredResources(
                numCpus=2,
                numGpus=0,
                memoryGb=4,
                timeSec=60 * 60
            ),
            run_method='local'
        )


def _get_all_recording_names(project: dc.Project):
    # for example 000618/sub-hybrid-janelia/sub-hybrid-janelia_ses-hybrid-drift-siprobe-rec-16c-1200s-11_ecephys
    # which comes from the file recordings/000618/sub-hybrid-janelia/sub-hybrid-janelia_ses-hybrid-drift-siprobe-rec-16c-1200s-11_ecephys.nwb.lindi.json
    def helper(folder_name: str):
        ret = []
        folder = project.get_folder(folder_name)
        files = folder.get_files()
        for file in files:
            if file.file_name.endswith('.nwb.lindi.json'):
                a = file.file_name[:-len('.nwb.lindi.json')]
                a = a[len('recordings/'):]
                ret.append(a)
        folders = folder.get_folders()
        for folder in folders:
            a = helper(folder.path)
            ret.extend(a)
        return ret
    return helper('recordings')


if __name__ == "__main__":
    create_recording_summaries()
