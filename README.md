# Welcome to MiniTwitter!

## Summary
This code instantiates MiniTwitter, a simple microblogging service akin to a minimalist version of Twitter (hence the name).

**Goal and functionality.** MiniTwitter's main goal is to faciliate communication over the web by enabling users to publish short textual *posts* that are viewable by all users. After signing up for the service, users are able to:
1. make posts of their own; 
1. *follow* other users and see their followed users' posts alongside their own on the 'Home' page; 
1. see all users' posts on the 'Explore' page.

The Profile page also features the count of the user's followers as well as the count of users they follow. Following and unfollowing occurs via the target user's profile page.

**Implementation details.** Despite it's simplicity, MiniTwitter is a full-stack web application with database, application, and visualization layers. It's built in the Python language, uses the Flask web framework, handles data through a SQLite (or MySQL) database, and deploys via a Docker container.[1] The service was built following Miguel Grinberg's Flask tutorial. 

## Quick Start
Navigate to the directory the application should be stored.
```
cd <path_to_dir_where_minitwitter_should_be_stored>
```

Make a virtual environment in a new dir `env`; activate this virtual environment.
```
python3 -m venv env
source env/bin/activate
```

Clone this branch (`del_es`) of the repo and navigate to it.
```
git clone -b del_es https://github.com/vishrutarya/minitwitter.git
cd minitwitter
```

Build the Docker container via Docker Compose.
```
docker-compose up -d --build
```

Connect to the service. In the browser, navigate to:
```
<ip_address>:8000
```

where `ip_address` should be replaced by the IP address of the host machine.[2]

## Quick Remove
Stop and remove the service's container (and networks, volumes, and images).
```
docker-compose down
```

Optionally, remove the associated Docker images. Find the relevant images:
```
docker images
```

Remove the relevant images:
```
docker rmi <IMAGE_ID>
```

## Addenda
### Remote instance dependency installs
If MiniTwitter is to be installed on a *remote* instance (eg., provisioned through AWS), three packages (Git, Docker, Docker Compose) must be installed before running the above quick start instructions. To install these packages on Ubuntu 16.04, run the following-commands on the remote instance:

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

### Note on Elasticsearch
The original version of MiniTwitter, which was deployed locally, included full-text search functionality (implemented via the Elasticsearch search engine). Although this worked for a local deployment, Elasticsearch's memory requirements implied deploying it on AWS would require a more expensive instance. Therefore, the Elasticsearch functionality has been deprecated in this repo to make it more widely compatible with remote instances. 

For less memory constrained deployments where Elasticsearch is desired, see the `master` branch which includes both Elasticsearch and MySQL containers.

### Notes
1. The version on this repo's `master` branch adds full-text search and a MySQL database. This fuller service is organized into three Docker containers, one for each of the application, MySQL database, and Elasticsearch search engine for full-text search.
2. If you're launching the web service locally -- i.e., on your laptop or desktop -- the default IP address for your machine is `localhost` which is equivalent to `127.0.0.1`.