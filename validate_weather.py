import great_expectations as gx
from great_expectations.checkpoint import UpdateDataDocsAction
from extraction.config import CITIES

context = gx.get_context(mode="file", project_root_dir=".")

datasource = context.data_sources.add_or_update_sql(
    name="weather_bigquery",
    connection_string="bigquery://weather-pipeline-495522/weather_raw",
)

table_asset = datasource.add_table_asset(
    name="daily_weather_asset", table_name="daily_weather"
)

batch_definition = table_asset.add_batch_definition_whole_table(name="full_load")

for suite_name in ["raw_weather_suite"]:
    try:
        context.suites.delete(suite_name)
    except Exception:
        pass

for vd_name in ["weather_raw_validation"]:
    try:
        context.validation_definitions.delete(vd_name)
    except Exception:
        pass

for cp_name in ["weather_raw_checkpoint"]:
    try:
        context.checkpoints.delete(cp_name)
    except Exception:
        pass

suite = context.suites.add_or_update(gx.ExpectationSuite(name="raw_weather_suite"))

# expect columns to exist
for col in [
    "city",
    "date",
    "temp_min",
    "temp_max",
    "temp_mean",
    "precipitation_mm",
    "windspeed_max",
    "humidity_mean",
    "weather_code",
    "ingested_at",
]:
    suite.add_expectation(gx.expectations.ExpectColumnToExist(column=col))

# expect column values to not be null
for col in ["city", "date", "ingested_at"]:
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column=col))

# expect column values to be in between
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="temp_max", min_value=-10, max_value=55
    )
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="humidity_mean", min_value=0, max_value=100
    )
)

# expect table row count to be between
suite.add_expectation(
    gx.expectations.ExpectTableRowCountToBeBetween(min_value=1, max_value=10_000)
)

# expect column values to be in set
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="city", value_set=[c["city_name"] for c in CITIES]
    )
)

validation_definition = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(
        name="weather_raw_validation", data=batch_definition, suite=suite
    )
)

checkpoint = context.checkpoints.add_or_update(
    gx.Checkpoint(
        name="weather_raw_checkpoint",
        validation_definitions=[validation_definition],
        actions=[UpdateDataDocsAction(name="update_data_docs")],
    )
)

results = checkpoint.run()
context.open_data_docs()

print(f"\nValidation passed: {results.success}")
for vr in results.run_results.values():
    stats = vr.statistics
    print(f"  Evaluated: {stats['evaluated_expectations']}")
    print(f"  Successful: {stats['successful_expectations']}")
    print(f"  Failed: {stats['unsuccessful_expectations']}")

for result in vr.results:
    if not result.success:
        print(f"\n  FAILED: {result.expectation_config.type}")
        print(f"\n    Column: {result.expectation_config.kwargs}")
        print(f"\n    Result: {result.result}")
