


.PHONY: prep launch clean

prep:
	bower install

launch:
	docker-compose up

clean:
	docker kill $(docker ps -q)
	docker rm $(docker ps -a -q)
	docker rmi $(docker images -q)
	rm -rf db logs media

# docker kill $(docker ps -q)
# docker rm $(docker ps -a -q)
# docker rmi $(docker images -q)

# docker rmi $(docker images -q -f dangling=true)
