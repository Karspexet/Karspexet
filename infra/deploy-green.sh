set -xe
/usr/bin/docker stop karspexet-green
/usr/bin/docker rm karspexet-green
/usr/bin/docker run \
  --name karspexet-green \
  --expose 8001 \
  --detach \
  --env-file /srv/karspexet/env.list \
  --user root \
  --network=host \
  --mount type=bind,source=/var/spool/postfix,target=/var/spool/postfix \
  -v /srv/karspexet/shared/uploads:/app/uploads \
  ghcr.io/karspexet/karspexet \
  gunicorn karspexet.wsgi --bind 0.0.0.0:8001
