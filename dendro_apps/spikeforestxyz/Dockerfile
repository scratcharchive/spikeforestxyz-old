FROM python:3.9-slim

# Install dendro
RUN pip install dendro==0.2.15

# Install kachery-cloud
RUN pip install kachery-cloud==0.4.9

# Install spikeinterface
RUN pip install spikeinterface==0.100.6

# Install lindi
RUN pip install lindi==0.3.4

# Copy files into the container
RUN mkdir /app
COPY *.py /app/
COPY recording_summary/*.py /app/recording_summary/
COPY recording_summary/helpers/*.py /app/recording_summary/helpers/
