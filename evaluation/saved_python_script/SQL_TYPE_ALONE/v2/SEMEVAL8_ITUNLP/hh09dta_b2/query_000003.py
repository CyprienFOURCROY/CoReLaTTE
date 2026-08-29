import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["edad", "ent", "folio"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()

    # Adults 18+
    adults = df_portad[df_portad["edad"] >= 18].dropna(subset=["folio", "ent"]).copy()
    adults["ent"] = adults["ent"].astype("Int64")

    # Households that use a plot of land for farming
    su = df_su.drop_duplicates(subset=["folio"])
    su = su[su["su01"] == 1.0]

    # Households with a positive amount of total debt (debts + interests)
    crh = df_crh.drop_duplicates(subset=["folio"])
    crh = crh[(crh["crh04_1"] == 1.0) & (crh["crh04_2"].notna()) & (crh["crh04_2"] > 0)]

    # Adult records in eligible households
    adults_eligible = adults.merge(su, on="folio", how="inner").merge(crh[["folio", "crh04_2"]], on="folio", how="inner")

    if adults_eligible.empty:
        return pd.DataFrame(columns=["ent", "avg_household_debt", "adult_records"])

    # Household-level dataset (one row per household) for averaging household debt
    hh_level = adults_eligible[["folio", "ent", "crh04_2"]].drop_duplicates(subset=["folio"])

    # Average household debt by state (household-level mean)
    avg_by_state = hh_level.groupby("ent", as_index=False)["crh04_2"].mean().rename(columns={"crh04_2": "avg_household_debt"})

    # Count of adult records contributing from those households by state
    adult_counts = adults_eligible.groupby("ent", as_index=False).size().rename(columns={"size": "adult_records"})

    # Merge and get top 10 states by average household debt
    result = avg_by_state.merge(adult_counts, on="ent", how="left")
    result = result.sort_values("avg_household_debt", ascending=False).head(10).reset_index(drop=True)

    return result