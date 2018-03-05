FROM python:3
MAINTAINER david.tennander@gmail.com & christoffer@lambertsson.me

WORKDIR /usr/src/app

COPY requirements/dev.txt ./
COPY requirements/base.txt ./
RUN pip install --no-cache-dir -r base.txt

# Install NPM
RUN apt-get update && \
        apt-get install --no-install-recommends -y \
            nodejs=0.10.29~dfsg-2 \
            npm=1.4.21+ds-2 \
            postgresql-client=9.4+165+deb8u3 && \
        rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN npm install -g n && n stable
RUN npm install -g npm

COPY package.json ./

RUN npm install

COPY . .

RUN node_modules/webpack/bin/webpack.js --config webpack.config.js

CMD ["bash", "./docker_command.sh"]
