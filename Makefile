.PHONY: doc runGittk runDemo build deploy buildTest deployTest

.venv:
	python3 -m venv .venv
	. .venv/bin/activate ; \
	pip install -r tools/requirements.txt
	#  Regen requirements;
	#    pip freeze > tools/requirements.txt

build: .venv
	. .venv/bin/activate ; \
	rm -rf dist ; \
	tools/prepareBuild.sh release ; \
	cd tmp ; \
	python3 -m build

buildTest: .venv
	. .venv/bin/activate ; \
	rm -rf dist ; \
	tools/prepareBuild.sh test ; \
	cd tmp ; \
	python3 -m build ;

deployTest: .venv
	. .venv/bin/activate ; \
	python3 -m twine upload --repository testpypi tmp/dist/* --verbose

deploy: .venv
	. .venv/bin/activate ; \
	python3 -m twine upload tmp/dist/* --repository ttkode --verbose

