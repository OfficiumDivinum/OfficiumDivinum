# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM tiangolo/node-frontend:10 as build-stage

WORKDIR /app

COPY ./ /app/

ARG FRONTEND_ENV=production

ENV VUE_APP_ENV=${FRONTEND_ENV}

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.15

RUN mkdir -p /usr/share/nginx/html/manual

COPY --from=build-stage /app/srv /usr/share/nginx/html/manual
COPY ./nginx-conf/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
COPY ./nginx-conf/01-login.conf /etc/nginx/extra-conf.d/01-login.conf