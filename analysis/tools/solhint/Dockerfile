FROM node:lts-alpine

RUN npm install -g solhint

RUN solhint init-config

CMD ["/bin/sh"]

COPY  .solhint.json .solhint.json

CMD ["node"]