


.PHONY: prep launch


prep:
	pushd api; bower install; popd;

launch:
	docker-compose up

