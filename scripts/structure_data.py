# in scripts/structure_data.py
from backend.src.utils.logger.logging import logger as logging
from sqlalchemy.orm import Session
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.app.services.llm_service import structure_specification


def main():
    """
    Finds unstructured specs, processes them in batches with the LLM service, and saves the results.
    """
    db = SessionLocal()
    try:
        logging.info("Starting specification structuring process...")

        # Step 1: Fetch only the IDs of specs to be processed.
        spec_ids_to_process = (
            db.query(Specification.id)
            .filter(Specification.structured_value.is_(None))
            .order_by(Specification.id)
            .all()
        )
        spec_ids = [item[0] for item in spec_ids_to_process]

        # === THE FIX IS HERE ===
        # Commit the session to end the read-only transaction before starting new write transactions in the loop.
        db.commit()

        total_specs = len(spec_ids)
        logging.info(f"Found {total_specs} unstructured specifications to process.")

        if not total_specs:
            return

        structured_count = 0
        batch_size = 20

        # Step 2: Process the IDs in batches
        for i in range(0, total_specs, batch_size):
            batch_ids = spec_ids[i : i + batch_size]

            try:
                # Step 3: For each batch, start a single, safe transaction
                with db.begin():
                    batch_specs = (
                        db.query(Specification)
                        .filter(Specification.id.in_(batch_ids))
                        .all()
                    )

                    for spec in batch_specs:
                        if len(spec.specification_value.strip()) < 5 or (
                            spec.specification_value.strip().startswith("[")
                            and spec.specification_value.strip().endswith("]")
                        ):
                            continue

                        structured_data = structure_specification(
                            spec.specification_name,
                            spec.specification_value,
                            spec.category,
                        )

                        if structured_data:
                            spec.structured_value = structured_data
                            structured_count += 1
                            logging.info(
                                f"Structured: {spec.category} -> {spec.specification_name} (ID: {spec.id})"
                            )

                logging.info(
                    f"Batch {i//batch_size + 1}/{(total_specs + batch_size - 1)//batch_size} committed."
                )

            except Exception as e:
                logging.exception(
                    f"Error processing batch starting with ID {batch_ids[0]}. This batch will be rolled back. Error: {e}"
                )

        logging.info(
            f"Successfully structured a total of {structured_count} specifications."
        )

    except Exception as e:
        logging.exception(
            f"A critical error occurred during the structuring process: {e}"
        )
    finally:
        db.close()


def preview_specifications(limit: int = 20):
    """
    Preview function to see what specifications exist in the database.
    Useful for debugging and understanding the data structure.
    """
    db = SessionLocal()

    try:
        specs = db.query(Specification).join(Laptop).limit(limit).all()

        print(f"\n=== Preview of {len(specs)} specifications ===")
        for spec in specs:
            print(f"Laptop: {spec.laptop.full_model_name}")
            print(f"Category: {spec.category}")
            print(f"Name: {spec.specification_name}")
            print(f"Value: {spec.specification_value[:100]}...")
            print(f"Structured: {'Yes' if spec.structured_value else 'No'}")
            print("-" * 50)

    except Exception as e:
        logging.exception(f"Error previewing specifications: {e}")
    finally:
        db.close()


def test_single_spec():
    """
    Test structuring on a single specification for debugging.
    """
    db = SessionLocal()

    try:
        # Get one unstructured spec for testing
        spec = (
            db.query(Specification)
            .filter(Specification.structured_value.is_(None))
            .first()
        )

        if not spec:
            print("No unstructured specifications found to test.")
            return

        print("Testing specification:")
        print(f"Category: {spec.category}")
        print(f"Name: {spec.specification_name}")
        print(f"Value: {spec.specification_value}")
        print("-" * 50)

        structured_data = structure_specification(
            spec.specification_name, spec.specification_value, spec.category
        )

        if structured_data:
            print("Structured result:")
            import json

            print(json.dumps(structured_data, indent=2))
        else:
            print("No structured data returned - check LLM service and prompts.")

    except Exception as e:
        logging.exception(f"Error testing single spec: {e}")
    finally:
        db.close()


def analyze_categories():
    """
    Analyze what categories and spec names we actually have in the database.
    Useful for understanding the data before structuring.
    """
    db = SessionLocal()

    try:
        # Get category distribution
        result = (
            db.query(
                Specification.category, db.func.count(Specification.id).label("count")
            )
            .group_by(Specification.category)
            .all()
        )

        print("\n=== Category Distribution ===")
        for category, count in result:
            print(f"{category}: {count} specs")

        # Get sample spec names by category
        print("\n=== Sample Spec Names by Category ===")
        for category, _ in result:
            sample_specs = (
                db.query(Specification.specification_name)
                .filter(Specification.category == category)
                .distinct()
                .limit(5)
                .all()
            )

            print(f"\n{category}:")
            for (spec_name,) in sample_specs:
                print(f"  - {spec_name}")

    except Exception as e:
        logging.exception(f"Error analyzing categories: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if "--preview" in sys.argv:
        preview_specifications()
    elif "--test" in sys.argv:
        test_single_spec()
    elif "--analyze" in sys.argv:
        analyze_categories()
    else:
        main()
