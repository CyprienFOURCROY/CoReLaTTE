import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Households that reported a value for total debts + interests
    df_crh_cond = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())]
    debts_set = set(df_crh_cond["folio"].dropna().astype(str).unique())

    # Households with at least one member who owns an electronic device
    df_ah_elec = df_ah[df_ah["ah03e"] == 1.0]
    elec_set = set(df_ah_elec["folio"].dropna().astype(str).unique())

    # Intersection of qualifying households
    qual_folios = debts_set.intersection(elec_set)

    # Map household to state
    f2e = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["folio", "ent"])
        .drop_duplicates(subset=["folio"])
    )

    # All states present
    all_states_df = pd.DataFrame({"ent": f2e["ent"].unique()})

    # Counts per state for qualifying households
    df_qual = f2e[f2e["folio"].astype(str).isin(qual_folios)]
    counts = df_qual.groupby("ent", as_index=False).agg(household_count=("folio", "nunique"))

    # Ensure all states included with zero where applicable
    counts_full = all_states_df.merge(counts, on="ent", how="left")
    counts_full["household_count"] = counts_full["household_count"].fillna(0).astype(int)

    # Average across states
    avg_count = counts_full["household_count"].mean()

    # States with counts >= average
    result = counts_full[counts_full["household_count"] >= avg_count].copy()
    result = result.sort_values(["household_count", "ent"], ascending=[False, True]).reset_index(drop=True)
    return result