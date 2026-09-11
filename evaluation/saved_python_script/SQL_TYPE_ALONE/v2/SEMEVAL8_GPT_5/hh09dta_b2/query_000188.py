import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_portad["has_60plus"] = df_portad["edad"] >= 60

    hh_profile = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), has_60plus=("has_60plus", "any"))
    )

    df_se = tables["ii_se"][["folio", "se01a"]].copy()
    hh_with_death = df_se[df_se["se01a"] == 1][["folio"]].drop_duplicates()

    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()
    hh_with_debts_value = df_crh[
        (df_crh["crh04_1"] == 1) & (df_crh["crh04_2"].notna())
    ][["folio"]].drop_duplicates()

    target_hh = hh_with_death.merge(hh_with_debts_value, on="folio", how="inner")

    merged = target_hh.merge(hh_profile, on="folio", how="inner")
    merged = merged[merged["ent"].notna()]

    result = (
        merged.groupby("ent", as_index=False)
        .agg(
            households_with_60plus=("has_60plus", lambda s: int(s.sum())),
            total_households=("folio", "nunique"),
        )
        .sort_values("ent")
        .reset_index(drop=True)
    )

    result["households_with_60plus"] = result["households_with_60plus"].astype("int64")
    result["total_households"] = result["total_households"].astype("int64")

    return result