FROM node:14-buster

WORKDIR /frontend

COPY frontend/package.json .
COPY frontend/yarn.lock .
RUN yarn install
COPY frontend/ .

CMD ["yarn", "start"]
