"""Entry point: run the Jumia orders CSV through the ETL pipeline."""
from pathlib import Path

from etl import CSVExtractor, DataLoader, DataTransformer, Pipeline

BASE_DIR = Path(__file__).parent

REQUIRED_FIELDS = [
    "order_id",
    "order_date",
    "customer_email",
    "city",
    "product_sku",
    "quantity",
    "unit_price_kes",
    "status",
]


def main() -> None:
    pipeline = Pipeline(
        extractor=CSVExtractor(BASE_DIR / "data" / "orders.csv", name="orders.csv"),
        transformer=DataTransformer(REQUIRED_FIELDS),
        loader=DataLoader(BASE_DIR / "output" / "clean_orders.csv"),
    )
    print(pipeline.run().report())


if __name__ == "__main__":
    main()
