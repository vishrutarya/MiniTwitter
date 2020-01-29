# Welcome to MiniTwitter!

## Summary
This code instantiates a simplified version of the microblogging service Twitter. It's built in the Python language, uses the Flask framework, a MySQL database, and deploys via Docker containers. The application was built following Miguel Grinberg's Flask tutorial.

A note on Elasticsearch. The original version of the app, which was deployed locally, included full-text search functionality via the Elasticsearch search engine. While this worked for a local deployment, including Elasticsearch on the remote AWS deployment required a significantly more expensive instance due to Elasticsearch's memory requirements. Therefore, the Elasticsearch functionality has been commented out to make it more widely compatible with remote instances. If the deployment is less memory constrained, the Elasticsearch code can be uncommented.

## Addenda
### Remote instance dependency installs

```
# GIT
apt-get install git

# DOCKER
# docker: uninstall old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# docker: update apt-get
sudo apt-get update

# docker: install using the repo
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update

# docker: install docker-ce
sudo apt-get install docker-ce docker-ce-cli containerd.io

# verify docker-ce installation
sudo docker run hello-world

# DOCKER COMPOSE
# docker compose: install
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# docker compose: verify installation
docker-compose --version
```