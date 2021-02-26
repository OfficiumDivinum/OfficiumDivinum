export USE_HOSTNAME=bede.2e0byo.co.uk
# Set up the server hostname
echo $USE_HOSTNAME > /etc/hostname
hostname -F /etc/hostname
# install docker
sudo apt-get remove -y docker docker-engine docker.io containerd runc
sudo apt-get update

sudo apt-get install -y\
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository -y\
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
# Download Docker
# curl -fsSL get.docker.com -o get-docker.sh
# # Install Docker using the stable channel (instead of the default "edge")
# CHANNEL=stable sh get-docker.sh
# # Remove Docker install script
# rm get-docker.sh
docker swarm init --advertise-addr $(curl ifconfig.me)
docker node ls
