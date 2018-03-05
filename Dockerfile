FROM python:3

WORKDIR /usr/src/app

COPY requirements/dev.txt ./
COPY requirements/base.txt ./
RUN pip install --no-cache-dir -r base.txt

# Install NPM
RUN apt-get update && \
        apt-get install -y nodejs npm postgresql-client && \
    		rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN npm install -g n && n stable
RUN npm install -g npm

COPY package.json ./

RUN npm install

COPY . .

RUN node_modules/webpack/bin/webpack.js --config webpack.config.js

CMD ["bash", "./docker_command.sh"]
