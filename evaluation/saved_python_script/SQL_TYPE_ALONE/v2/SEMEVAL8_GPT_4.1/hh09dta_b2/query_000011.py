def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Adults only
    df_portad_adults = df_portad[df_portad["edad"] >= 18]

    # Households that use a plot/land for farming (su01 == 1)
    df_su_farming = df_su[df_su["su01"] == 1]

    # Households with positive total debt including interest (crh04_2 > 0)
    df_crh_debt = df_crh[df_crh["crh04_2"] > 0]

    # Merge on folio to get only households that meet all criteria
    # First, get unique household IDs for adults
    adult_households = df_portad_adults[["folio", "ent"]].drop_duplicates()

    # Merge farming and debt on folio
    farming_debt = pd.merge(df_su_farming[["folio"]], df_crh_debt[["folio", "crh04_2"]], on="folio", how="inner")

    # Merge with adults to get state info and ensure only adult households
    merged = pd.merge(farming_debt, adult_households, on="folio", how="inner")

    # Group by state and aggregate
    result = (
        merged.groupby("ent")
        .agg(
            average_debt=("crh04_2", "mean"),
            household_count=("folio", "nunique")
        )
        .reset_index()
    )

    # Sort by average_debt descending and get top 10
    result = result.sort_values("average_debt", ascending=False).head(10)

    # Rename ent to state for clarity
    result = result.rename(columns={"ent": "state"})

    # Reset index for clean output
    result = result.reset_index(drop=True)

    return result