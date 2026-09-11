def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]

    # Filter households where a member uses a plot/land for farming (su01=1)
    df_su = tables["ii_su"]
    df_su_farming = df_su[df_su["su01"] == 1]

    # Get household IDs with farming land use
    household_ids = df_su_farming["folio"].unique()

    # Filter portad for these households
    df_portad_farming = df_portad[df_portad["folio"].isin(household_ids)]

    # Calculate overall average age in this subset
    overall_avg_age = df_portad_farming["edad"].mean()

    # Select individuals older than this average age
    df_older = df_portad_farming[df_portad_farming["edad"] > overall_avg_age]

    # Count how many are older
    count_older = len(df_older)

    # Calculate their average age
    avg_age_older = df_older["edad"].mean()

    # Return results in a DataFrame
    return pd.DataFrame(
        {
            "count_older_than_avg": [count_older],
            "average_age_older": [avg_age_older]
        }
    )