FROM alpine:3.20

ARG APP_VERSION=1.0
ENV APP_ENV=development

RUN echo "Build-time APP_VERSION=$APP_VERSION" > /build-info.txt

CMD sh -c 'echo "Runtime APP_ENV=$APP_ENV"; echo "Contents of /build-info.txt:"; cat /build-info.txt'
