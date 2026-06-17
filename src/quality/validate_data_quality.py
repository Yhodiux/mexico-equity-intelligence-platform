from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "market_prices_raw.parquet"
DEFAULT_SILVER_PATH = PROJECT_ROOT / "data" / "silver" / "market_prices_silver.parquet"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "metadata" / "data_quality_report.json"


@dataclass(frozen=True)
class QualityCheck:
    name: str
    passed: bool
    severity: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "severity": self.severity,
            "details": self.details,
        }


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def read_dataset(path: Path, dataset_name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{dataset_name} dataset not found: {path}")

    data = pd.read_parquet(path)
    logging.info("Read %s rows from %s", len(data), path)
    return data


def check_row_count(dataset_name: str, data: pd.DataFrame) -> QualityCheck:
    row_count = len(data)
    return QualityCheck(
        name=f"{dataset_name}_row_count_greater_than_zero",
        passed=row_count > 0,
        severity="critical",
        details={"row_count": row_count},
    )


def check_required_columns(dataset_name: str, data: pd.DataFrame, required_columns: set[str]) -> QualityCheck:
    missing_columns = sorted(required_columns - set(data.columns))
    return QualityCheck(
        name=f"{dataset_name}_required_columns_present",
        passed=not missing_columns,
        severity="critical",
        details={
            "required_columns": sorted(required_columns),
            "missing_columns": missing_columns,
        },
    )


def check_not_null(dataset_name: str, data: pd.DataFrame, column: str) -> QualityCheck:
    null_count = int(data[column].isna().sum()) if column in data.columns else len(data)
    return QualityCheck(
        name=f"{dataset_name}_{column}_not_null",
        passed=null_count == 0,
        severity="critical",
        details={"column": column, "null_count": null_count},
    )


def check_no_duplicates(dataset_name: str, data: pd.DataFrame, columns: list[str]) -> QualityCheck:
    if not set(columns).issubset(data.columns):
        duplicate_count = len(data)
        samples: list[dict[str, Any]] = []
    else:
        duplicate_mask = data.duplicated(columns, keep=False)
        duplicate_count = int(duplicate_mask.sum())
        samples = data.loc[duplicate_mask, columns].head(10).to_dict(orient="records")

    return QualityCheck(
        name=f"{dataset_name}_{'_'.join(columns)}_unique",
        passed=duplicate_count == 0,
        severity="critical",
        details={
            "columns": columns,
            "duplicate_row_count": duplicate_count,
            "sample_duplicates": samples,
        },
    )


def check_non_negative(dataset_name: str, data: pd.DataFrame, column: str) -> QualityCheck:
    if column not in data.columns:
        invalid_count = len(data)
        min_value = None
    else:
        values = pd.to_numeric(data[column], errors="coerce")
        invalid_count = int((values < 0).sum())
        min_value = None if values.dropna().empty else float(values.min())

    return QualityCheck(
        name=f"{dataset_name}_{column}_non_negative",
        passed=invalid_count == 0,
        severity="critical",
        details={
            "column": column,
            "invalid_count": invalid_count,
            "min_value": min_value,
        },
    )


def check_high_greater_or_equal_low(data: pd.DataFrame) -> QualityCheck:
    required_columns = {"high_price", "low_price"}
    if not required_columns.issubset(data.columns):
        invalid_count = len(data)
        samples: list[dict[str, Any]] = []
    else:
        invalid_mask = data["high_price"] < data["low_price"]
        invalid_count = int(invalid_mask.sum())
        samples = (
            data.loc[invalid_mask, ["ticker", "date", "high_price", "low_price"]]
            .head(10)
            .to_dict(orient="records")
        )

    return QualityCheck(
        name="silver_high_price_greater_or_equal_low_price",
        passed=invalid_count == 0,
        severity="critical",
        details={"invalid_count": invalid_count, "sample_invalid_rows": samples},
    )


def check_close_between_low_and_high(data: pd.DataFrame) -> QualityCheck:
    required_columns = {"close_price", "low_price", "high_price"}
    if not required_columns.issubset(data.columns):
        invalid_count = len(data)
        checked_count = 0
        samples: list[dict[str, Any]] = []
    else:
        comparable = data[["close_price", "low_price", "high_price"]].notna().all(axis=1)
        invalid_mask = comparable & (
            (data["close_price"] < data["low_price"]) | (data["close_price"] > data["high_price"])
        )
        checked_count = int(comparable.sum())
        invalid_count = int(invalid_mask.sum())
        samples = (
            data.loc[invalid_mask, ["ticker", "date", "close_price", "low_price", "high_price"]]
            .head(10)
            .to_dict(orient="records")
        )

    return QualityCheck(
        name="silver_close_price_between_low_price_and_high_price",
        passed=invalid_count == 0,
        severity="critical",
        details={
            "checked_count": checked_count,
            "invalid_count": invalid_count,
            "sample_invalid_rows": samples,
        },
    )


def build_report(raw: pd.DataFrame, silver: pd.DataFrame) -> dict[str, Any]:
    raw_required_columns = {"date", "ticker", "open", "high", "low", "close", "adj_close", "volume"}
    silver_required_columns = {
        "date",
        "ticker",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adjusted_close",
        "volume",
        "daily_return",
        "intraday_volatility",
        "price_range",
        "volume_category",
        "trend_flag",
        "issuer_name",
        "sector",
        "ingestion_timestamp",
    }

    checks = [
        check_row_count("raw", raw),
        check_row_count("silver", silver),
        check_required_columns("raw", raw, raw_required_columns),
        check_required_columns("silver", silver, silver_required_columns),
        check_not_null("silver", silver, "ticker"),
        check_not_null("silver", silver, "date"),
        check_no_duplicates("silver", silver, ["ticker", "date"]),
    ]

    for column in ["open_price", "high_price", "low_price", "close_price", "adjusted_close"]:
        checks.append(check_non_negative("silver", silver, column))

    checks.append(check_non_negative("silver", silver, "volume"))
    checks.append(check_high_greater_or_equal_low(silver))
    checks.append(check_close_between_low_and_high(silver))

    failed_checks = [check for check in checks if not check.passed and check.severity == "critical"]
    generated_at = pd.Timestamp.utcnow().isoformat()

    return {
        "generated_at": generated_at,
        "status": "passed" if not failed_checks else "failed",
        "summary": {
            "total_checks": len(checks),
            "passed_checks": sum(1 for check in checks if check.passed),
            "failed_checks": len(failed_checks),
        },
        "datasets": {
            "raw": {
                "record_count": len(raw),
                "column_count": len(raw.columns),
                "columns": list(raw.columns),
            },
            "silver": {
                "record_count": len(silver),
                "column_count": len(silver.columns),
                "columns": list(silver.columns),
            },
        },
        "checks": [check.to_dict() for check in checks],
    }


def write_report(report: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=True, default=str)
        file.write("\n")

    logging.info("Wrote data quality report to %s", output_path)
    return output_path


def run_data_quality(raw_path: Path, silver_path: Path, output_path: Path) -> Path:
    raw = read_dataset(raw_path, "Raw")
    silver = read_dataset(silver_path, "Silver")
    report = build_report(raw, silver)
    report_path = write_report(report, output_path)

    if report["status"] != "passed":
        failed_names = [
            check["name"]
            for check in report["checks"]
            if not check["passed"] and check["severity"] == "critical"
        ]
        raise RuntimeError(f"Data quality validation failed: {', '.join(failed_names)}")

    logging.info("Data quality validation passed with %s checks", report["summary"]["total_checks"])
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Raw and Silver market data quality.")
    parser.add_argument(
        "--raw-path",
        type=Path,
        default=DEFAULT_RAW_PATH,
        help="Path to the raw market prices parquet file.",
    )
    parser.add_argument(
        "--silver-path",
        type=Path,
        default=DEFAULT_SILVER_PATH,
        help="Path to the silver market prices parquet file.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path where the data quality JSON report will be written.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    output_path = run_data_quality(args.raw_path, args.silver_path, args.output_path)
    logging.info("Data quality completed successfully: %s", output_path)


if __name__ == "__main__":
    main()
