# Welcome to MiniTwitter!

## Summary
This code instantiates MiniTwitter, a simple microblogging service akin to a minimalist version of Twitter (hence the name).

**High-level goal and functionality.** MiniTwitter's main goal is to facilitate communication over the web. It does this by enabling users to make textual *posts*, displaying these posts publicly as the author's *stream*, enabling users to follow one another such that each user's *feed* is a chronological list of all the posts made by the user and those the user is following, and search across all posts.

**Technology stack.** Despite it's simplicity, MiniTwitter is a full-stack web application with database, application, and visualization layers. It's built in Python using the Flask web framework, handles data through a SQLite (or MySQL) database, employs the Elasticsearch engine for full-text search, and deploys via three Docker containers (application, database, Elasticsearch).[1] The service was built following Miguel Grinberg's Flask tutorial. 

## Demo

### Post

![](/gifs/post.gif)

## Quick Start
Navigate to the directory in which the application should be stored.
```
cd <path_to_dir_where_minitwitter_should_be_stored>
```

Make a virtual environment in a new dir, `env`; activate this virtual environment.
```
python3 -m venv env
source env/bin/activate
```

Ensure Git, Docker, and Docker Compose are installed via the below commands. See the Addenda for instructions on how to install any of these missing packages if on Ubuntu 16.04.
```
git --version
docker --version
docker-compose --version
```

Clone the repo and navigate to it.
```
git clone https://github.com/vishrutarya/minitwitter.git
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

where `ip_address` should be replaced by the IP address of the host machine.[1]

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

### Notes
1. If you're launching the web service locally -- i.e., on your laptop or desktop -- the default IP address for your machine is `localhost` which is equivalent to `127.0.0.1`.