import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Households in Oaxaca with at least one member aged 18+
    df_portad_oax = df_portad[df_portad["ent"] == 20.0]
    has_adult = (
        df_portad_oax.assign(is_adult=(df_portad_oax["edad"] >= 18))
        .groupby("folio", as_index=False)["is_adult"]
        .any()
    )
    has_adult_true = has_adult[has_adult["is_adult"]][["folio"]]

    # Households that reported a numeric value for total debts + interest
    df_crh_val = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())][["folio", "crh04_2"]]
    df_crh_val = df_crh_val.drop_duplicates(subset=["folio"])

    # SU group (use plot/land Yes/No)
    df_su_sub = df_su[["folio", "su01"]].drop_duplicates(subset=["folio"])

    # Merge filters
    merged = (
        has_adult_true
        .merge(df_crh_val, on="folio", how="inner")
        .merge(df_su_sub, on="folio", how="left")
    )

    # Keep only explicit Yes/No groups
    merged = merged[merged["su01"].isin([1.0, 3.0])]

    if merged.empty:
        return pd.DataFrame({"group": [], "average_total_debt": []})

    overall_avg = merged["crh04_2"].mean()

    grp = (
        merged.groupby("su01", as_index=False)["crh04_2"]
        .mean()
        .rename(columns={"crh04_2": "average_total_debt"})
    )
    grp["group"] = grp["su01"].map({1.0: "Yes", 3.0: "No"})

    result = grp[grp["average_total_debt"] > overall_avg].sort_values(
        "average_total_debt", ascending=False
    )[["group", "average_total_debt"]]

    return result