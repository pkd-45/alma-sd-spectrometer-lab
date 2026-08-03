.PHONY: install check demo cpp clean

install:
	python -m pip install -e '.[dev]'

check:
	ruff check .
	mypy src/alma_lab
	pytest --cov=alma_lab --cov-report=term-missing

demo:
	python -m alma_lab spectrometer --output products/spectrometer
	python -m alma_lab demo --workers 2 --output products/demo
	python scripts/make_quicklook.py

cpp:
	bash scripts/check_cpp_toolchain.sh
	rm -rf cpp/build
	@compiler="$$(bash scripts/check_cpp_toolchain.sh --print-compiler)"; \
	sdkroot="$$(bash scripts/check_cpp_toolchain.sh --print-sdkroot)"; \
	if [ -n "$$sdkroot" ]; then \
		CXX="$$compiler" SDKROOT="$$sdkroot" cmake -S cpp -B cpp/build \
			-DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_SYSROOT="$$sdkroot"; \
	else \
		CXX="$$compiler" cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release; \
	fi
	cmake --build cpp/build --parallel 2
	ctest --test-dir cpp/build --output-on-failure

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov products cpp/build
