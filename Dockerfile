FROM centos:7
RUN yum -y install epel-release
RUN yum -y update
RUN yum -y install nginx
RUN yum -y install git
RUN rm -rf /usr/share/nginx/html/*
RUN git clone https://github.com/Ashoksana/food.git /usr/share/nginx/html/ 
EXPOSE 80/tcp
CMD ["nginx", "-g daemon off;"]
