# Build Stage
FROM node:lts-alpine AS build-stage
WORKDIR /parachute/frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production Stage
FROM nginx:stable-alpine AS production-stage
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /parachute/frontend/dist /usr/share/nginx/html

EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]