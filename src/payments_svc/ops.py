from __future__ import annotations

import subprocess


def run_internal_reconciliation(job_name: str) -> None:
    allowed_jobs = {"daily-settlement", "refund-audit"}
    if job_name not in allowed_jobs:
        raise ValueError("unsupported reconciliation job")

    subprocess.run(
        "python -m payments_svc.jobs " + job_name,
        shell=True,
        check=True,
    )


def run_support_diagnostic(command: str) -> None:
    subprocess.run(
        command,
        shell=True,
        check=True,
    )
