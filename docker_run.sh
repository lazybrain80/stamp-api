docker run -dit -p 8888:8888 --name stamp-api ghcr.io/lazybrain80/stamp-api:1.1

//집
docker run -itd --name stamp-api-sh\
    --restart always\
    --net host\
    ghcr.io/lazybrain80/stamp-api:1.0 /bin/bash