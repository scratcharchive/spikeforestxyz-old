from dendro.sdk import ProcessorBase, InputFile, OutputFile
from dendro.sdk import BaseModel, Field


class RecordingSummaryContext(BaseModel):
    input: InputFile = Field(description="Input .nwb.lindi.json file")
    output: OutputFile = Field(description="Output .json file")


class RecordingSummaryProcessor(ProcessorBase):
    name = "spikeforestxyz.recording_summary"
    description = "Create recording summary for a recording .nwb.lindi.json file"
    label = "spikeforestxyz.recording_summary"
    tags = []
    attributes = {"wip": True}

    @staticmethod
    def run(context: RecordingSummaryContext):
        from .create_recording_summary import create_recording_summary

        output_fname = 'output.nwb.lindi.json'
        context.input.download(output_fname)
        create_recording_summary(
            output_fname
        )
        context.output.upload(output_fname)
