import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_inr = tables["ii_inr"].copy()

    # Household-level state and adult presence
    df_portad["is_adult"] = df_portad["edad"] >= 18
    hh = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), has_adult=("is_adult", "max"))
    )

    # Household-level ownership of poultry
    own = (
        df_ah.assign(own_poultry=df_ah["ah03m"] == 1)
        .groupby("folio", as_index=False)["own_poultry"]
        .max()
    )

    # Household-level dairy production/sales in last 12 months
    dairy = (
        df_inr.assign(dairy=df_inr["inr02a"] == 1)
        .groupby("folio", as_index=False)["dairy"]
        .max()
    )

    # Merge all
    m = (
        hh.merge(own, on="folio", how="left")
        .merge(dairy, on="folio", how="left")
    )
    m["own_poultry"] = m["own_poultry"].fillna(False)
    m["dairy"] = m["dairy"].fillna(False)

    # Filter: households with at least one adult and that own poultry
    base = m[(m["has_adult"]) & (m["own_poultry"])].copy()

    # Aggregate per state
    result = (
        base.groupby("ent")
        .agg(
            households_18plus_own_poultry=("folio", "nunique"),
            households_18plus_own_poultry_dairy=("dairy", "sum"),
        )
        .reset_index()
    )

    return result