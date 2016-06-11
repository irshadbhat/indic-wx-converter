travis:
	python setup.py test --coverage \
		--coverage-package-name=wxconv
clean:
	find . -iname "*.pyc" -exec rm -vf {} \;
	find . -iname "__pycache__" -delete
