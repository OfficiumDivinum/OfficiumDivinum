docker network create --driver=overlay traefik-public
export NODE_ID=$(docker info -f '{{.Swarm.NodeID}}')
docker node update --label-add traefik-public.traefik-public-certificates=true $NODE_ID
export EMAIL=admin@2e0byo.co.uk
export DOMAIN=traefik.sys.2e0byo.co.uk
export USERNAME=admin
export HASHED_PASSWORD=$(openssl passwd -apr1)
curl -L dockerswarm.rocks/traefik.yml -o traefik.yml
docker stack deploy -c traefik.yml traefik
docker stack ps traefik
