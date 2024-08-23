# Use the official Nginx image as the base image
FROM nginx

MAINTAINER rajeshindala143@gmail.com
# Remove the default Nginx configuration file
RUN rm /etc/nginx/nginx.conf

# Copy the custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the website files to the container
COPY site1 /usr/share/nginx/html/site1
COPY site2 /usr/share/nginx/html/site2

