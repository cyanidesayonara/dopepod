# dopepod

dopepod is a web app capable of playing and searching a wide variety of free podcasts. Registered users can also subscribe to podcasts and create a playlist of episodes. It uses the Python web-framework Django as a backend. The podcasts are scraped from the web using Python packages Scrapy and requests. The frontend framework Bootstrap is used for CSS and JS. JavaScript libraries JQuery, Slick, vanilla-lazyload and sticky-kit are also used.

# Install Elastisearch

sudo apt update
wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.3.1/elasticsearch-2.3.1.deb
sudo dpkg -i elasticsearch-2.3.1.deb
sudo systemctl enable elasticsearch
sudo nano /etc/elasticsearch/elasticsearch.yml
cluster.name: elasticsearch
node.name: dopepod
sudo systemctl start elasticsearch
curl -X GET 'http://localhost:9200'

# Install Nginx

sudo apt update
sudo apt install nginx
sudo ufw allow 'Nginx Full'
sudo systemctl enable nginx
sudo vim /etc/nginx/sites-available/dopepod.me
sudo vim /etc/nginx/sites-available/em.dopepod.me
sudo ln -s /etc/nginx/sites-available/dopepod.me /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/em.dopepod.me /etc/nginx/sites-enabled/

# Install Let's Encrypt

sudo add-apt-repository ppa:certbot/certbot
sudo apt install psudo journalctl -u gunicornython-certbot-nginx
sudo certbot --nginx -d dopPepod.me -d www.dopepod.me -d em.dopepod.me -d www.em.dopepod.me
sudo certbot renew --dry-run

# Install Matomo

sudo lsapt-get install unzip php7.2
sudo cd /var/www
sudo wget http://builds.piwik.org/latest.zip
sudo unzip latest.zip
sudo rm *html *zip
sudo chown -R www-data:www-data /var/www/piwik

# Install PHP & MySQL

sudo apt-get install php7.2-fpm php-mysql mysql-server php-mbstring php-xml
sudo mysql_secure_installation

#REFS
https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-16-04
https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04
https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04  
https://www.digitalocean.com/community/tutorials/how-to-install-piwik-on-an-ubuntu-12-04-cloud-server
