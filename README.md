# ecommAPI
* Django-based app that aims to recreate a simple e-commerce shop.
* Implements payments with Stripe API.
* Secured with dj-rest-auth and JWT

## Functionality
* SwaggerUI docs available at `localhost:8000/api/swagger` (DEBUG=True only).
* Allows for creation of products, categories.
* Users can create reviews of products.
* Users can create a cart and add items to it.
* Cart can be ordered with a coupon, which creates an Order object.
* At `/api/orders/<order_id>/session/` Stripe Session is created and returns ID and url to payment.
* Stripe Webhook detects successful payment and updates Order accordingly.

## Tech stack
* Django 4.0
* Django REST Framework
* Stripe
* Docker
* PostgreSQL

## Setup
1. Clone repository:
`$ git clone https://github.com/amadeuszklimaszewski/ecommapi/`
2. Run in root directory:
`$ make build-dev`
3. Provide `STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY` in .env file
4. Run project: `make up-dev`
5. Provide Stripe's `WEEBHOK_SECRET` in .env

## Tests
`$ make test`

## Create admin
`$ make superuser`

## Makefile
`Makefile` contains useful command aliases

