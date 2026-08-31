import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # Household-level electronics value
    elec_by_folio = (
        df_ah[["folio", "ah04e_2"]]
        .groupby("folio", as_index=False, dropna=False)["ah04e_2"]
        .max()
    )
    elec_by_folio = elec_by_folio.dropna(subset=["ah04e_2"])

    # Overall mean electronics value across households with available value
    overall_mean = elec_by_folio["ah04e_2"].mean()

    # Above-mean households
    elec_above_mean = elec_by_folio[elec_by_folio["ah04e_2"] > overall_mean].rename(columns={"ah04e_2": "elec_value"})

    # Households that use land for farming (su01 == 1)
    su_land = df_su.loc[df_su["su01"] == 1, ["folio"]].drop_duplicates()

    # Households with at least one robbery since 2005
    rob_house = (df_vlh.get("vlh12a_a") == 1) | (df_vlh.get("vlh12a_b") == 2)
    rob_biz = (df_vlh.get("vlh14a") == 1)
    rob_parcel = (df_vlh.get("vlh16a") == 1)
    rob_total = df_vlh.get("vlh18a").fillna(0) > 0
    rob_any = (rob_house.fillna(False)) | (rob_biz.fillna(False)) | (rob_parcel.fillna(False)) | rob_total

    rob_since_2005 = df_vlh.loc[rob_any, ["folio"]].drop_duplicates()

    # State per household
    ent_by_folio = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["ent"])
        .drop_duplicates(subset=["folio"])
    )

    # Merge filters
    df = (
        elec_above_mean.merge(su_land, on="folio", how="inner")
        .merge(rob_since_2005, on="folio", how="inner")
        .merge(ent_by_folio, on="folio", how="inner")
    )

    # Aggregate by state
    result = (
        df.groupby("ent", as_index=False)
        .agg(avg_electronics_value=("elec_value", "mean"), num_households=("folio", "nunique"))
        .sort_values(by="avg_electronics_value", ascending=False)
        .reset_index(drop=True)
    )

    # Ensure proper dtypes
    if "ent" in result.columns:
        try:
            result["ent"] = result["ent"].astype("Int64")
        except Exception:
            pass

    return result