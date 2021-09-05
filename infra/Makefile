status:
	systemctl status karspexet-docker.service
setup:
	sudo cp karspexet-docker.service /etc/systemd/system/
	sudo cp karspexet.conf /etc/nginx/conf.d/
restart:
	docker pull ghcr.io/karspexet/karspexet
	sudo systemctl daemon-reload
	sudo systemctl restart karspexet-docker.service
	docker system prune --force
