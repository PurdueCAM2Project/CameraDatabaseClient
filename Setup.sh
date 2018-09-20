#!/usr/bin/env bash
docker-compose kill
docker-compose rm -f
docker system prune --all -f
docker-compose up
