FROM node:20-alpine
ENV NODE_ENV=production

WORKDIR /app

COPY ./discord-client/package*.json ./
RUN npm ci --omit=dev

COPY ./discord-client/ ./

CMD ["node", "index.js"]