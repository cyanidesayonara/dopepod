# dopepod [DEPRECATED]
dopepod was a web app capable of playing and searching a wide variety of free podcasts. Registered users could also
subscribe to podcasts and create a playlist of episodes. It used the Python web-framework Django as a backend.
The podcasts were scraped from the web using Python packages Scrapy and requests. The frontend framework Bootstrap was
used for CSS and JS. JavaScript libraries JQuery, Slick, vanilla-lazyload were sticky-kit are also used for frontendstuff.

Go to [dop3pod](https://github.com/cyanidesayonara/dop3pod) instead.

## Server instructions
### Install Elastisearch
sudo apt update  
wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.3.1/elasticsearch-2.3.1.deb    
sudo dpkg -i elasticsearch-2.3.1.deb  
sudo systemctl enable elasticsearch  
sudo nano /etc/elasticsearch/elasticsearch.yml  
-> cluster.name: elasticsearch  
-> node.name: dopepod  
-> bootstrap.mlockall: true  
sudo nano /etc/default/elasticsearch  
-> ES_HEAP_SIZE=512m  
-> MAX_LOCKED_MEMORY=unlimited  
sudo update-rc.d elasticsearch defaults 95 10  
sudo systemctl start elasticsearch  
curl -X GET 'http://localhost:9200'

### Install Nginx
sudo apt update  
sudo apt install nginx  
sudo ufw allow 'Nginx Full'  
sudo systemctl enable nginx  
sudo vim /etc/nginx/sites-available/dopepod.me  
sudo vim /etc/nginx/sites-available/em.dopepod.me  
sudo ln -s /etc/nginx/sites-available/dopepod.me /etc/nginx/sites-enabled/  
sudo ln -s /etc/nginx/sites-available/em.dopepod.me /etc/nginx/sites-enabled/

### Install Let's Encrypt
sudo add-apt-repository ppa:certbot/certbot  
sudo apt install psudo journalctl -u gunicornython-certbot-nginx  
sudo certbot --nginx -d dopepod.me -d www.dopepod.me -d em.dopepod.me -d www.em.dopepod.me  
sudo certbot renew --dry-run

### Install Matomo
sudo lsapt-get install unzip php7.2  
sudo cd /var/www  
sudo wget http://builds.piwik.org/latest.zip  
sudo unzip latest.zip  
sudo rm *html *zip  
sudo chown -R www-data:www-data /var/www/piwik

### Install PHP & MySQL
sudo apt-get install php7.2-fpm php-mysql mysql-server php-mbstring php-xml  
sudo mysql_secure_installation

### Add swap to Digital Ocean Ubuntu
sudo swapon --show  
free -h  
sudo fallocate -l 1G /swapfile  
ls -lh /swapfile  
sudo chmod 600 /swapfile  
sudo mkswap /swapfile  
sudo swapon /swapfile  
sudo swapon --show  
sudo cp /etc/fstab /etc/fstab.bak  
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab  
cat /proc/sys/vm/swappiness  
sudo nano /etc/sysctl.conf  
-> vm.swappiness=10  
-> vm.vfs_cache_pressure=50

## References
https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-16-04  
https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04  
https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04  
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04    
https://www.digitalocean.com/community/tutorials/how-to-install-piwik-on-an-ubuntu-12-04-cloud-server  
https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-18-04
