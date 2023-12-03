# 1GB image is just big.
# Some of the lines are taken from alpine template of gorialis'
# FROM gorialis/discord.py:3.8-alpine-minimal
FROM python:3.8-alpine
RUN \
  echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
  echo "http://dl-8.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN \
  apk --no-cache add -q git mercurial cloc openssl openssl-dev openssh alpine-sdk bash gettext sudo build-base gnupg linux-headers xz && \
  ln -s /usr/include/locale.h /usr/include/xlocale.h && \
  pip install -U pip Cython pytest -q --retries 30 && \
  # remove caches
  rm -rf /root/.cache/pip/* && \
  rm -rf /var/cache/apk/* && \
  find /usr/local -depth \
    \( \
      \( -type d -a \( -name test -o -name tests \) \) \
    -o \
    \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
    \) -exec rm -rf '{}' +

# Actual Dockerfile content
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["docker/entrypoint"]
