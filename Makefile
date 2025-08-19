test-unit:
	pytest crypto_ensemble/1_data/1_ingestion/2_normalizer/tests/unit crypto_ensemble/1_data/1_ingestion/5_health/tests/unit crypto_ensemble/6_monitoring/tests/unit

test-contract:
	pytest crypto_ensemble/1_data/1_ingestion/1_connectors/tests/contract crypto_ensemble/1_data/1_ingestion/2_normalizer/tests/contract crypto_ensemble/1_data/1_ingestion/3_router/tests/contract crypto_ensemble/1_data/1_ingestion/4_sinks/tests/contract crypto_ensemble/1_data/1_ingestion/6_capture/tests/contract

test-chain:
	python crypto_ensemble/7_tests_chain/runner.py

verify-module:
	black --check .
	isort --check-only .
	./flake8 .
	./pydocstyle crypto_ensemble
	mypy --strict crypto_ensemble/core crypto_ensemble/aliases
	$(MAKE) test-unit
	$(MAKE) test-contract
	$(MAKE) test-chain

bench-module:
	pytest --maxfail=1 --disable-warnings --benchmark-only
