import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_se = tables["ii_se"].copy()
    df_ah = tables["ii_ah"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Oaxaca households with at least one adult (>=18)
    df_p = df_portad[["folio", "ent", "edad"]].dropna(subset=["folio"])
    df_p_oxa = df_p[df_p["ent"] == 20.0].copy()
    df_p_oxa["is_adult"] = df_p_oxa["edad"] >= 18
    adult_oxa = df_p_oxa.groupby("folio", as_index=False)["is_adult"].max()
    adult_oxa = adult_oxa[adult_oxa["is_adult"]]

    # Households with death in last five years
    df_se_death = df_se[df_se["se01a"] == 1.0][["folio"]].dropna(subset=["folio"]).drop_duplicates()

    # Eligible households: Oaxaca + at least one adult + death in last five years
    eligible = adult_oxa[["folio"]].merge(df_se_death, on="folio", how="inner").drop_duplicates()

    # Device ownership at household level: any member owns electronic device
    df_dev = df_ah[["folio", "ah03e"]].dropna(subset=["folio"]).copy()
    df_dev["has_elec"] = df_dev["ah03e"] == 1.0
    dev_by_folio = df_dev.groupby("folio", as_index=False)["has_elec"].any()

    # Robbery entries since 2005
    df_v = df_vlh[["folio", "vlh18a"]].dropna(subset=["folio"]).copy()

    # Merge all
    res = (
        eligible.merge(df_v, on="folio", how="left")
        .merge(dev_by_folio, on="folio", how="left")
    )
    res["has_elec"] = res["has_elec"].fillna(False)

    overall_avg = res["vlh18a"].mean()

    if pd.isna(overall_avg):
        return pd.DataFrame({"device_group": pd.Series(dtype=object), "households": pd.Series(dtype="int64")})

    group_stats = (
        res.groupby("has_elec", as_index=False)
        .agg(
            avg_vlh18a=("vlh18a", "mean"),
            households_in_group=("folio", "nunique"),
        )
    )
    group_stats["overall_avg"] = overall_avg
    group_stats["device_group"] = group_stats["has_elec"].map({True: "any", False: "none"})

    filtered = group_stats[
        (group_stats["avg_vlh18a"].notna()) & (group_stats["avg_vlh18a"] >= group_stats["overall_avg"])
    ]

    out = filtered[["device_group", "households_in_group"]].rename(columns={"households_in_group": "households"}).reset_index(drop=True)

    return out