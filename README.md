# payments-svc

API de pagos en Python para el curso de Platzi sobre testing y code review con IA.

El proyecto esta preparado para avanzar por incrementos de clase. Para el Modulo B parte de una base limpia: `amounts.py` y `refunds.py` tienen contratos confirmados, tests unitarios y una configuracion reproducible de mutation testing.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## Tests

```powershell
python -m unittest tests.test_amounts tests.test_refunds -v
```

## Smoke test

```powershell
python scripts/smoke_test.py
```

## Mutation testing

```powershell
cosmic-ray init cosmic-ray.toml mutation.sqlite
cosmic-ray exec cosmic-ray.toml mutation.sqlite
cr-report mutation.sqlite
```

## API local

```powershell
uvicorn payments_svc.api:app --reload
```

Endpoints:

- `GET /health`
- `POST /payments`
- `POST /refunds`

