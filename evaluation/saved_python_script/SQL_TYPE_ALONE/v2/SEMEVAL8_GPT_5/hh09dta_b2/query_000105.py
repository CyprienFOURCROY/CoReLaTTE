import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]
    df_su = tables["ii_su"]

    # Oaxaca households
    oax_folios = df_portad.loc[df_portad["ent"] == 20.0, "folio"].dropna().unique()

    # Households that use a plot for farming
    su_farming = df_su.loc[df_su["su01"] == 1.0, ["folio"]].dropna()
    su_folios = su_farming["folio"].unique()

    # Intersection: Oaxaca + farming households
    scope_folios = pd.Index(oax_folios).intersection(pd.Index(su_folios))

    if len(scope_folios) == 0:
        return pd.DataFrame({"average_wm_stove_value": [float("nan")]})

    # Household-level total value of washing machine/stove
    wm = (
        df_ah[["folio", "ah04f_2"]]
        .copy()
        .dropna(subset=["folio"])
    )
    wm["ah04f_2"] = wm["ah04f_2"].fillna(0)
    wm_household = wm.groupby("folio", as_index=False)["ah04f_2"].sum().rename(columns={"ah04f_2": "wm_value"})

    # Base DataFrame for scoped households
    base = pd.DataFrame({"folio": scope_folios})

    # Merge with wm values and shocks
    base = base.merge(wm_household, on="folio", how="left")
    base["wm_value"] = base["wm_value"].fillna(0)

    se = df_se[["folio", "se01e"]].dropna(subset=["folio"])
    base = base.merge(se, on="folio", how="left")

    # Threshold: average wm value among those that did lose total crop (se01e == 1)
    lost_mask = base["se01e"] == 1.0
    threshold = base.loc[lost_mask, "wm_value"].mean()

    # Filter: did not lose (se01e == 3) and wm_value > threshold
    not_lost_mask = base["se01e"] == 3.0
    filtered = base.loc[not_lost_mask & (base["wm_value"] > threshold), "wm_value"]

    result = filtered.mean()

    return pd.DataFrame({"average_wm_stove_value": [result]})