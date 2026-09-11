import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]

    # Households that report owning an electronic device (ah03e == 1)
    device_hh_folios = df_ah.loc[df_ah["ah03e"] == 1.0, "folio"].dropna().unique()

    # Individuals living in those households
    dfp = df_portad[df_portad["folio"].isin(device_hh_folios)].copy()

    # Count 18–24-year-olds and total individuals per state
    dfp["is1824"] = (dfp["edad"] >= 18) & (dfp["edad"] <= 24)
    grp = (
        dfp.groupby("ent", as_index=False)
        .agg(
            count_18_24=("is1824", "sum"),
            total_in_device_households=("folio", "size"),
        )
    )

    # Average 18–24 count across states
    avg_1824 = grp["count_18_24"].mean()

    # States above average, ranked by 18–24 count
    res = grp[grp["count_18_24"] > avg_1824].copy()
    if not res.empty:
        res = res.sort_values(by="count_18_24", ascending=False)
        # Cast state code to integer
        res["ent"] = res["ent"].astype("int64")

    return res