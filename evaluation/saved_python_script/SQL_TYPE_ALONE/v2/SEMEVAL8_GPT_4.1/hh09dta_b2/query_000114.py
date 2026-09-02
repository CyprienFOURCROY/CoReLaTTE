def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Step 1: Households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio", "edad"]]

    # Step 2: At least one adult (edad >= 18) in household that uses a plot for farming (su01 == 1)
    # Merge portad and su on folio
    merged = oaxaca_households.merge(df_su[["folio", "su01"]], on="folio", how="left")
    # Only households with at least one adult and su01 == 1
    adults = merged[(merged["edad"] >= 18) & (merged["su01"] == 1.0)]
    # Get unique household IDs
    eligible_folios = adults["folio"].unique()

    # Step 3: From these households, get those with numeric values for both crh03_2 and crh04_2
    crh_subset = df_crh[
        df_crh["folio"].isin(eligible_folios)
    ][["folio", "crh03_2", "crh04_2"]].copy()
    crh_subset = crh_subset[
        crh_subset["crh03_2"].notna() & crh_subset["crh04_2"].notna()
    ]

    # Step 4: Compute average of crh04_2 in this group
    avg_total_debt = crh_subset["crh04_2"].mean()

    # Step 5: Filter to those with crh04_2 > average
    result = crh_subset[crh_subset["crh04_2"] > avg_total_debt].copy()

    # Step 6: Sort by crh04_2 descending
    result = result.sort_values("crh04_2", ascending=False)

    # Step 7: Return folio and crh04_2
    return result[["folio", "crh04_2"]].reset_index(drop=True)