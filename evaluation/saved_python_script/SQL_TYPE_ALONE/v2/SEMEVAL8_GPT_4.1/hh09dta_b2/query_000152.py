def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]

    # Households where a member uses a plot/land for farming (su01 == 1)
    farming_households = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Individuals in those households
    df_farming = df_portad.merge(farming_households, on="folio", how="inner")

    # Remove missing ages
    df_farming = df_farming[df_farming["edad"].notnull()]

    # Compute overall average age in this subset
    overall_avg_age = df_farming["edad"].mean()

    # For each state, count and average age of individuals older than overall average
    df_older = df_farming[df_farming["edad"] > overall_avg_age]

    result = (
        df_older.groupby("ent")
        .agg(
            n_older_than_avg=("edad", "size"),
            avg_age_older=("edad", "mean")
        )
        .reset_index()
        .rename(columns={"ent": "state"})
    )

    return result