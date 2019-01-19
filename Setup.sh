#!/usr/bin/env bash
docker-compose kill
docker-compose rm -f
docker system prune --volumes -f
docker-compose up --build
