# Use your existing Alpine-based base image
FROM monica:4.1.2-apache
#FROM lscr.io/linuxserver/monica:latest

# Install HAProxy
RUN apt update && apt install -y haproxy bash supervisor default-libmysqlclient-dev default-mysql-client default-mysql-client-core

# Copy the entrypoint script that generates haproxy.cfg
COPY entrypoint-ha.sh /usr/local/bin/entrypoint-ha.sh
COPY supervisord.conf /etc/supervisor/conf.d/monica-and-haproxy.conf
COPY supervisor.sh /usr/local/bin/supervisor.sh

RUN chmod +x /usr/local/bin/entrypoint-ha.sh
RUN chmod +x /usr/local/bin/supervisor.sh

# Expose the port defined in environment variables for HAProxy
EXPOSE 3306

# Set the default entrypoint to generate the HAProxy config and start services
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
#CMD ["sh", "-c", "/usr/local/bin/entrypoint-ha.sh & apache2-foreground"]
#CMD ["apache2-foreground"]
CMD ["/usr/local/bin/supervisor.sh"]
