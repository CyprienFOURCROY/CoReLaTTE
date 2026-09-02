def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]

    # Merge household info with assets ownership
    df = df_portad.merge(df_ah, on=["folio"], how="inner")

    # Filter households that use land for farming and own poultry
    mask_land = df["su01"] == 1
    mask_poultry = df["ah03m"] == 1
    df_filtered = df[mask_land & mask_poultry]

    # Group by state (ent)
    group = df_filtered.groupby("ent").agg(
        household_count=pd.NamedAgg(column="folio", aggfunc="count"),
        mean_age=pd.NamedAgg(column="edad", aggfunc="mean")
    ).reset_index()

    # Overall average age across all such households
    overall_avg_age = df_filtered["edad"].mean()

    # Filter states with at least 25 households
    group_filtered = group[group["household_count"] >= 25]

    # Further filter states with mean age above overall average
    result = group_filtered[group_filtered["mean_age"] > overall_avg_age]

    # Rank states from highest to lowest mean age
    result_sorted = result.sort_values(by="mean_age", ascending=False).reset_index(drop=True)

    # Select relevant columns
    result_final = result_sorted[["ent", "household_count", "mean_age"]]

    # Rename 'ent' to 'state' for clarity
    result_final = result_final.rename(columns={"ent": "state"})

    return result_final