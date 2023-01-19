.PHONY: all nodeps test check lint coverage package deploy clean

all: clean check
	pip install -t dist .

nodeps:
	pip install --no-deps --upgrade -t dist .

test:
	pytest

check: lint coverage

lint:
	black --line-length 79 --check --exclude dist .
	# flake8 --exclude dist .
	isort --check --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width=79 quicksilver/**/*.py test/**/*.py

coverage:
	coverage run --source quicksilver -m pytest
	coverage report --fail-under 50

package: all
	sam package --s3-bucket artifacts.jairtrejo.mx --output-template-file packaged-template.yaml

deploy: package
	sam deploy --template-file packaged-template.yaml --stack-name avatar-jairtrejo-api --capabilities CAPABILITY_IAM --parameter-overrides Stage=Prod CorsDomain=https://avatar.jairtrejo.com DomainName=api-avatar.jairtrejo.com SSLCertificateArn=arn:aws:acm:us-east-1:501965419031:certificate/0b9bca2d-cf0c-45ff-8d0d-b01eee8d1357 HostedZoneId=Z0431545UH073TJJS79M

clean:
ifneq ($(wildcard dist/**),)
	rm -r ./dist/**
endif
	coverage erase
