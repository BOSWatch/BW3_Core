FROM alpine:3.10 AS boswatch
ARG BW_VERSION=develop
RUN apk add git && \
    git clone --depth 1 --branch ${BW_VERSION} https://github.com/BOSWatch/BW3-Core.git /opt/boswatch

FROM python:3.6-alpine AS runner
LABEL maintainer="bastian@schroll-software.de"

RUN pip3 install pyyaml

RUN mkdir /log/
COPY --from=boswatch /opt/boswatch/ /opt/boswatch/
COPY ./config/* /opt/boswatch/config/
