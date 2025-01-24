// base
docker build -t ghcr.io/lazybrain80/stamp-api:1.0 .
docker build -f Dockerfile4OpenCV -t ghcr.io/lazybrain80/base-stamp-api .
// arm64 build
docker buildx create --name stampArm64Builder --use

docker buildx build --platform linux/arm64 -t ghcr.io/lazybrain80/stamp-api:1.1 --push .