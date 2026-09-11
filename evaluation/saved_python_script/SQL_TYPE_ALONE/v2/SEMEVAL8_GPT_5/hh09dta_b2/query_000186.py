import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()
    df_su = tables["ii_su"].copy()

    # Households that use a plot/land
    su_use_land = df_su.loc[df_su["su01"] == 1.0, ["folio"]].drop_duplicates()

    # Households with reported total debts + interests value
    crh_debt = df_crh.loc[
        (df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna()),
        ["folio", "crh04_2"]
    ].drop_duplicates(subset=["folio"])

    # Merge to get target households
    hh = su_use_land.merge(crh_debt, on="folio", how="inner")

    # Attach state (ent) per household
    hh_ent = df_portad[["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates(subset=["folio"])
    hh = hh.merge(hh_ent, on="folio", how="left").dropna(subset=["ent"])
    hh["ent"] = hh["ent"].astype("Int64")

    if hh.empty:
        return pd.DataFrame(columns=["ent", "n_households", "avg_debt"])

    overall_avg = hh["crh04_2"].mean()

    res = (
        hh.groupby("ent", as_index=False)
          .agg(n_households=("folio", "nunique"), avg_debt=("crh04_2", "mean"))
    )

    res = res[(res["n_households"] >= 20) & (res["avg_debt"] > overall_avg)]
    res = res.sort_values(by="avg_debt", ascending=False).reset_index(drop=True)

    return res[["ent", "n_households", "avg_debt"]]