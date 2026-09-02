def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_inr = tables["ii_inr"]

    # Filter households that use a plot/land for farming/vegetables
    # su01 == 1 means HHM use a plot/land for farming/vegetables
    land_use = df_su[df_su["su01"] == 1][["folio"]]

    # Filter households that did NOT produce or sell honey in last 12 months
    # inr02i == 3 means no honey production/sale
    honey_no_produce = df_inr[df_inr["inr02i"] == 3][["folio"]]

    # Merge to get households that satisfy both conditions
    households = pd.merge(land_use, honey_no_produce, on="folio", how="inner")

    # Count households per household (folio)
    household_counts = households.groupby("folio").size().reset_index(name="count")
    # Keep only households with at least 40 such households
    valid_households = household_counts[household_counts["count"] >= 40]["folio"]

    # Filter original households to keep only valid ones
    df_valid = df_portad[df_portad["folio"].isin(valid_households)]

    # Merge with su to get land use info
    df_su_valid = df_su[df_su["folio"].isin(valid_households)]

    # Filter households that use land for farming/vegetables
    df_land_farming = df_su_valid[df_su_valid["su01"] == 1][["folio"]]

    # Get the final set of households
    final_households = pd.merge(df_valid, df_land_farming, on="folio", how="inner")

    # Merge with df_inr to check honey production
    df_inr_valid = df_inr[df_inr["folio"].isin(final_households["folio"])]

    # For each household, check if honey production/sale is '3' (no)
    honey_no = df_inr_valid.groupby("folio")["inr02i"].apply(lambda x: all(x == 3)).reset_index()

    # Keep households where all entries have '3' for honey (i.e., did not produce/sell honey)
    households_no_honey = honey_no[honey_no["inr02i"] == True]["folio"]

    # Final households: those that use land for farming/vegetables, did not produce honey, and have at least 40 such households
    final_folios = households_no_honey

    # Filter the main dataframe to these households
    df_final = df_portad[df_portad["folio"].isin(final_folios)]

    # Merge with df_inr to get ages
    df_final_inr = df_inr[df_inr["folio"].isin(df_final["folio"])]

    # Merge with df_portad to get ages
    df_merged = pd.merge(df_final, df_portad[["folio", "edad"]], on="folio", how="left")

    # Calculate overall average age
    overall_avg_age = df_merged["edad"].mean()

    # Compute average age per state
    state_age = (
        df_merged.groupby("ent")
        .agg(
            household_count=("folio", "nunique"),
            average_age=("edad", "mean")
        )
        .reset_index()
    )

    # Filter states with at least 40 households
    state_filtered = state_age[state_age["household_count"] >= 40]

    # Keep only states where average age is below overall average age
    result_states = state_filtered[state_filtered["average_age"] < overall_avg_age]

    # Order from lowest to highest average age
    result_states_sorted = result_states.sort_values(by="average_age", ascending=True)

    # Prepare final output
    output = result_states_sorted[["ent", "household_count", "average_age"]]
    output = output.rename(columns={
        "ent": "state_code",
        "household_count": "num_households",
        "average_age": "avg_age"
    })

    return output.reset_index(drop=True)