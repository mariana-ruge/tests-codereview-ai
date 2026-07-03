# payments-svc

API de pagos en Python para validar reglas de negocio, pruebas y revisiones automatizadas en un servicio pequeno y realista.

El servicio expone operaciones basicas de pagos y reembolsos. Los modulos `amounts.py`, `refunds.py`, `auth.py` y `api.py` tienen contratos confirmados y tests unitarios.

El repositorio incluye automatizaciones de revision, reglas de seguridad y documentos operativos para gobernar el uso del revisor con IA.

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

