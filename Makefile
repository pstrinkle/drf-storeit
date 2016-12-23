


.PHONY: launch

launch:
	docker-compose up

# docker kill $(docker ps -q)
# docker rmi $(docker images -q)
# docker rmi $(docker images -q -f dangling=true)
# docker rm $(docker ps -a -q)