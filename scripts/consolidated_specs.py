"""
Script to consolidate fragmented battery specifications into unified records.
Run after initial structuring to merge battery life test results.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.utils.logger.logging import logger as logging
import json


def consolidate_battery_specs(db: Session):
    """
    Consolidate battery specifications:
    1. Find all battery specs for each laptop
    2. Merge battery life tests into main battery records
    3. Remove redundant entries
    """
    logging.info("Starting battery specification consolidation...")

    # Get all laptops that have battery specs
    laptop_ids = (
        db.query(Specification.laptop_id)
        .filter(Specification.category == "Battery")
        .distinct()
        .all()
    )

    for (laptop_id,) in laptop_ids:
        try:
            # Get all battery specs for this laptop
            battery_specs = (
                db.query(Specification)
                .filter(
                    and_(
                        Specification.laptop_id == laptop_id,
                        Specification.category == "Battery",
                    )
                )
                .order_by(Specification.id)
                .all()
            )

            if not battery_specs:
                continue

            # Separate battery options from battery life tests
            battery_options = []
            battery_life_tests = []

            for spec in battery_specs:
                if "Battery Life -" in spec.specification_name:
                    battery_life_tests.append(spec)
                elif "Battery Option" in spec.specification_name:
                    battery_options.append(spec)

            # Process each battery option
            for battery_option in battery_options:
                if not battery_option.structured_value:
                    continue

                structured = battery_option.structured_value
                if not isinstance(structured, dict):
                    continue

                # Initialize test_results if not present
                if "test_results" not in structured or not structured["test_results"]:
                    structured["test_results"] = []

                # Add all battery life tests to this battery option
                for life_test in battery_life_tests:
                    test_name = life_test.specification_name.replace(
                        "Battery Life - ", ""
                    )

                    # Extract hours from value
                    hours_match = re.search(
                        r"([\d.]+)\s*hours?", life_test.specification_value, re.I
                    )
                    if hours_match:
                        hours = float(hours_match.group(1))

                        # Check if this test already exists
                        test_exists = any(
                            t.get("test_name") == test_name
                            for t in structured["test_results"]
                        )

                        if not test_exists:
                            structured["test_results"].append(
                                {"test_name": test_name, "hours": hours}
                            )

                # Update the structured value
                battery_option.structured_value = structured
                db.flush()

            # Delete redundant battery life test entries
            for life_test in battery_life_tests:
                db.delete(life_test)

            logging.info(
                f"Consolidated {len(battery_life_tests)} battery life tests "
                f"into {len(battery_options)} battery options for laptop_id={laptop_id}"
            )

        except Exception as e:
            logging.exception(
                f"Error consolidating battery specs for laptop_id={laptop_id}: {e}"
            )

    logging.info("Battery consolidation complete.")


def fix_processor_frequencies(db: Session):
    """
    Fix processor frequency parsing issues using regex on raw values.
    """
    logging.info("Fixing processor frequency issues...")

    processor_specs = (
        db.query(Specification)
        .filter(
            and_(
                Specification.category == "Processor",
                Specification.specification_name.like("%Frequencies%"),
            )
        )
        .all()
    )

    for spec in processor_specs:
        try:
            if not spec.structured_value:
                spec.structured_value = {}

            structured = spec.structured_value
            raw_value = spec.specification_value

            # Extract all GHz values
            ghz_values = re.findall(r"([\d.]+)\s*GHz", raw_value, re.I)
            if ghz_values:
                frequencies = [float(v) for v in ghz_values]

                # Set base to lowest, max to highest
                if not structured.get("base_frequency_ghz"):
                    structured["base_frequency_ghz"] = min(frequencies)
                if not structured.get("max_frequency_ghz"):
                    structured["max_frequency_ghz"] = max(frequencies)

                # Extract model from spec_name
                if not structured.get("model"):
                    model_match = re.search(
                        r"(Core\s+i[3579]-?\d+[A-Z]+|AMD\s+Ryzen.*?\d+[A-Z]?|Intel.*?Core.*?Ultra.*?\d+[A-Z])",
                        spec.specification_name,
                        re.I,
                    )
                    if model_match:
                        structured["model"] = model_match.group(1).strip()

                # Infer brand
                if not structured.get("brand"):
                    model = structured.get("model", "")
                    spec_text = f"{spec.specification_name} {raw_value}"
                    if "intel" in spec_text.lower() or "core" in spec_text.lower():
                        structured["brand"] = "Intel"
                    elif "amd" in spec_text.lower() or "ryzen" in spec_text.lower():
                        structured["brand"] = "AMD"

                spec.structured_value = structured
                logging.info(f"Fixed processor frequencies for spec_id={spec.id}")

        except Exception as e:
            logging.exception(f"Error fixing processor spec_id={spec.id}: {e}")

    # Commit all changes at once
    try:
        db.commit()
        logging.info("Processor frequency fixes complete.")
    except Exception as e:
        db.rollback()
        logging.exception(f"Failed to commit processor fixes: {e}")


def validate_all_structured_data(db: Session):
    """
    Run validation checks and report quality metrics.
    """
    logging.info("Running validation checks...")

    total_specs = (
        db.query(Specification)
        .filter(Specification.structured_value.isnot(None))
        .count()
    )

    # Check processor completeness
    processor_specs = (
        db.query(Specification)
        .filter(
            and_(
                Specification.category == "Processor",
                Specification.structured_value.isnot(None),
            )
        )
        .all()
    )

    processor_issues = []
    for spec in processor_specs:
        structured = spec.structured_value
        if not isinstance(structured, dict):
            continue

        missing_fields = []
        if not structured.get("brand"):
            missing_fields.append("brand")
        if not structured.get("model"):
            missing_fields.append("model")

        if missing_fields:
            processor_issues.append(
                {
                    "id": spec.id,
                    "name": spec.specification_name,
                    "missing": missing_fields,
                }
            )

    # Check display completeness
    display_specs = (
        db.query(Specification)
        .filter(
            and_(
                Specification.category == "Display",
                Specification.structured_value.isnot(None),
            )
        )
        .all()
    )

    display_issues = []
    for spec in display_specs:
        structured = spec.structured_value
        if isinstance(structured, dict):
            if not structured.get("resolution"):
                display_issues.append(
                    {
                        "id": spec.id,
                        "name": spec.specification_name,
                        "issue": "missing resolution",
                    }
                )

    # Report
    print("\n=== Validation Report ===")
    print(f"Total structured specs: {total_specs}")
    print(f"\nProcessor issues: {len(processor_issues)}/{len(processor_specs)}")
    for issue in processor_issues[:5]:
        print(f"  ID {issue['id']}: {issue['name']} - missing {issue['missing']}")

    print(f"\nDisplay issues: {len(display_issues)}/{len(display_specs)}")
    for issue in display_issues[:5]:
        print(f"  ID {issue['id']}: {issue['name']} - {issue['issue']}")

    quality_score = (
        (
            (total_specs - len(processor_issues) - len(display_issues))
            / total_specs
            * 100
        )
        if total_specs > 0
        else 0
    )
    print(f"\nOverall Quality Score: {quality_score:.1f}%")


if __name__ == "__main__":
    import sys
    import re

    db = SessionLocal()
    try:
        if "--consolidate" in sys.argv:
            consolidate_battery_specs(db)
        elif "--fix-processors" in sys.argv:
            fix_processor_frequencies(db)
        elif "--validate" in sys.argv:
            validate_all_structured_data(db)
        else:
            print("Usage:")
            print(
                "  python consolidate_specs.py --consolidate    # Merge battery specs"
            )
            print("  python consolidate_specs.py --fix-processors # Fix processor data")
            print("  python consolidate_specs.py --validate       # Check data quality")
    finally:
        db.close()
