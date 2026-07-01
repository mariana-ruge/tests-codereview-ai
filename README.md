# payments-svc

API de pagos en Python para el curso de Platzi sobre testing y code review con IA.

El proyecto esta preparado para avanzar por incrementos de clase. Para el Modulo C parte de una base limpia de producto: `amounts.py`, `refunds.py`, `auth.py` y `api.py` tienen contratos confirmados y tests unitarios.

Los artefactos especificos del revisor de PR del Modulo B se dejan fuera de esta rama para que las demos de auditoria de codigo existente empiecen sin ruido.

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
sh scripts/mutation_domain.sh
```

## API local

```sh
uvicorn payments_svc.api:app --reload
```

Endpoints:

- `GET /health`
- `POST /payments`
- `POST /refunds`

