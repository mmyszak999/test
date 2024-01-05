db-name=postgres

build-dev:
	-cp -n ./.env.template ./.env
	docker-compose build

up-dev:
	docker-compose run --rm backend bash -c "python manage.py migrate"
	docker-compose up

build-prod:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml build

up-prod:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml run --rm backend bash -c "python manage.py migrate"
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d

collectstatic:
	docker-compose exec -u 0 backend bash -c "python manage.py collectstatic --no-input"
	
migrations:
	docker-compose exec backend bash -c "python manage.py makemigrations && python manage.py migrate"

superuser:
	docker-compose exec backend bash -c "python manage.py createsuperuser"

test:
	docker-compose exec backend bash -c "python manage.py test $(location)"

backend-bash:
	docker-compose exec backend bash

django-shell:
	docker-compose exec backend bash -c "python manage.py shell_plus --ipython --print-sql"

reset-db:
	docker-compose stop backend
	docker-compose exec db bash -c "runuser postgres -c 'dropdb $(db-name); createdb $(db-name)'"
	docker-compose start backend
	make migrations