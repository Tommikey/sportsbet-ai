FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD sed -i "s/\$PORT/${PORT:-80}/g" /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
