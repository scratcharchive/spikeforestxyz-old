import tempfile
import dandi.dandiarchive as da
import dendro.client as dc
import lindi


def dandi_import():
    dandiset_id = '000618'  # https://neurosift.app/?p=/dandiset&dandisetId=000618&dandisetVersion=draft
    dandiset_version = 'draft'
    dendro_project_id = '9e302504'  # https://dendro.vercel.app/project/9e302504?tab=project-home

    parsed_url = da.parse_dandi_url(f"https://dandiarchive.org/dandiset/{dandiset_id}")

    project = dc.load_project(dendro_project_id)

    num_processed = 0
    with parsed_url.navigate() as (client, dandiset, assets):
        if dandiset is None:
            print(f"Dandiset {dandiset_id} not found.")
            return
        for asset_obj in dandiset.get_assets('path'):
            if not asset_obj.path.endswith(".nwb"):
                continue
            print('=====================')
            print(asset_obj.path)

            dandi_asset_url = asset_obj.download_url
            dandi_asset_path = asset_obj.path
            output_path = f'recordings/{dandiset_id}/{dandi_asset_path}.lindi.json'
            ff = project.get_file(output_path)
            if ff is not None:
                print("Skipping - already exists")
                continue
            f = lindi.LindiH5pyFile.from_hdf5_file(
                dandi_asset_url,
                local_cache=lindi.LocalCache()
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                lindi_fname = f'{tmpdir}/tmp.nwb.lindi.json'
                f.write_lindi_file(
                    lindi_fname,
                    generation_metadata={
                        'generated_by': 'spikeforestxyz',
                        'dandiset_id': dandiset_id,
                        'dandiset_version': dandiset_version,
                        'dandi_asset_path': dandi_asset_path,
                        'dandi_asset_url': dandi_asset_url
                    }
                )
                lindi_file_url = dc.upload_file_blob(
                    project_id=dendro_project_id,
                    file_name=lindi_fname
                )
            dc.set_file(
                project=project,
                file_name=output_path,
                url=lindi_file_url,
                metadata={
                    'dandisetId': dandiset_id,
                    'dandisetVersion': dandiset_version,
                    'dandiAssetPath': dandi_asset_path
                }
            )
            num_processed = num_processed + 1
            if num_processed >= 3:
                break

if __name__ == '__main__':
    dandi_import()
