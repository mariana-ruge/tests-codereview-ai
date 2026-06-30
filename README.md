# payments-svc

API de pagos en Python para el curso de Platzi sobre testing y code review con IA.

El proyecto esta preparado para avanzar por incrementos de clase. Para el Modulo B parte de una base limpia: `amounts.py` y `refunds.py` tienen contratos confirmados, tests unitarios y una configuracion reproducible de mutation testing.

## Instalacion

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Tests

```sh
python -m unittest discover -s tests -p "test_*.py" -v
```

## Smoke test

```sh
python scripts/smoke_test.py
```

## Mutation testing

```sh
cosmic-ray init --force cosmic-ray.toml mutation-amounts.sqlite
cosmic-ray exec cosmic-ray.toml mutation-amounts.sqlite
cr-report mutation-amounts.sqlite

cosmic-ray init --force cosmic-ray-refunds.toml mutation-refunds.sqlite
cosmic-ray exec cosmic-ray-refunds.toml mutation-refunds.sqlite
cr-report mutation-refunds.sqlite

cosmic-ray init --force cosmic-ray-auth.toml mutation-auth.sqlite
cosmic-ray exec cosmic-ray-auth.toml mutation-auth.sqlite
cr-report mutation-auth.sqlite

cosmic-ray init --force cosmic-ray-api.toml mutation-api.sqlite
cosmic-ray exec cosmic-ray-api.toml mutation-api.sqlite
cr-report mutation-api.sqlite
```

## API local

```sh
uvicorn payments_svc.api:app --reload
```

Endpoints:

- `GET /health`
- `POST /payments`
- `POST /refunds`

