set -xe

if [ "$1" == "green" ]; then
  a=8000;
  b=8001;
else
  a=8001;
  b=8000;
fi;

sed -i -e "s/127.0.0.1:$a/127.0.0.1:$b/" /etc/nginx/conf.d/karspexet.conf
nginx -t
systemctl restart nginx.service

grep "127.0.0.1" /etc/nginx/conf.d/karspexet.conf
