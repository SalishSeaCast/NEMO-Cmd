# docker container description file for NEMO-Cmd package testing environment
#
# Primarily intended for creation of a docker image for use by bitbucket-pipelines.yml.

FROM continuumio/miniconda3

ADD ./environment-test.yaml /tmp/environment-test.yaml
RUN conda env create -f /tmp/environment-test.yaml
