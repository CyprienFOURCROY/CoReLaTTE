import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]

    # Identify households with at least one adult (18+)
    p = df_portad[["folio", "ent", "edad"]].copy()
    p["has_adult"] = p["edad"] >= 18
    hh_adult = (
        p.groupby("folio", as_index=False)
         .agg(ent=("ent", "first"), has_adult=("has_adult", "max"))
    )
    hh_adult = hh_adult[hh_adult["has_adult"]].copy()

    # Determine eligible states (at least 50 adult-households)
    state_adult_counts = hh_adult.groupby("ent").size()
    eligible_states = set(state_adult_counts[state_adult_counts >= 50].index.tolist())

    # Household-level ownership of electronic device (any member says yes)
    ah = df_ah[["folio", "ah03e"]].copy()
    ah["has_elec"] = ah["ah03e"] == 1.0
    hh_elec = ah.groupby("folio", as_index=False)["has_elec"].max()

    # Merge and filter to eligible states
    merged = hh_adult.merge(hh_elec, on="folio", how="left")
    merged["has_elec"] = merged["has_elec"].fillna(False)
    merged = merged[merged["ent"].isin(eligible_states)]

    # Count households owning electronic device per state
    result = (
        merged.groupby("ent", as_index=False)["has_elec"]
        .sum()
        .rename(columns={"has_elec": "households_own_electronic_device"})
        .sort_values(["households_own_electronic_device", "ent"], ascending=[False, True])
        .reset_index(drop=True)
    )

    # Cast ent to integer if possible
    try:
        result["ent"] = result["ent"].astype("Int64")
    except Exception:
        pass

    return result