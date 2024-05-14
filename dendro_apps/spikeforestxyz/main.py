#!/usr/bin/env python


from dendro.sdk import App
from recording_summary.recording_summary import RecordingSummaryProcessor

app = App(
    name="spikeforestxyz",
    description="Processors for SpikeForestXYZ",
    app_image="ghcr.io/magland/spikeforestxyz:latest",
    app_executable="/app/main.py",
)


app.add_processor(RecordingSummaryProcessor)

if __name__ == "__main__":
    app.run()
