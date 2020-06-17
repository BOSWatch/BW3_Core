FROM alpine:3.10 AS build-base
RUN apk add git make cmake g++ libusb-dev libpulse

FROM build-base AS rtl_fm
ARG RTL_SDR_VERSION=0.6.0
RUN git clone --depth 1 --branch ${RTL_SDR_VERSION} https://github.com/osmocom/rtl-sdr.git /opt/rtl_sdr
WORKDIR /opt/rtl_sdr/build
RUN cmake .. && make

FROM build-base AS multimon
ARG MULTIMON_VERSION=1.1.8
RUN git clone --depth 1 --branch ${MULTIMON_VERSION} https://github.com/EliasOenal/multimon-ng.git /opt/multimon
WORKDIR /opt/multimon/build
RUN cmake .. && make

FROM alpine:3.10 AS boswatch
ARG BW_VERSION=develop
RUN apk add git && \
    git clone --depth 1 --branch ${BW_VERSION} https://github.com/BOSWatch/BW3-Core.git /opt/boswatch

FROM python:3.6-alpine AS runner
LABEL maintainer="bastian@schroll-software.de"

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk update

#           for RTL    for MM
RUN apk add libusb-dev libpulse rtl-sdr && \
    pip3 install pyyaml

COPY --from=boswatch /opt/boswatch/ /opt/boswatch/
COPY --from=multimon /opt/multimon/build/multimon-ng /opt/multimon/multimon-ng
#COPY --from=rtl_fm /opt/rtl_sdr/build/src/* /opt/rtl_sdr/

RUN mkdir /opt/boswatch/log/
RUN mkdir /log/
RUN chmod 755 /opt/multimon/multimon-ng /opt/boswatch/*

COPY ./config/* /opt/boswatch/config/
COPY ./module/* /opt/boswatch/module/
COPY ./plugin/* /opt/boswatch/plugin/
