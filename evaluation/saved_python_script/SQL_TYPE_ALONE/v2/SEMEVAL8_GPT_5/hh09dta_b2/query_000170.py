import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]

    # Oaxaca households with at least one adult (18+)
    oax_adult_folios = (
        df_portad.loc[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18.0), "folio"]
        .dropna()
        .unique()
    )
    oax_adult_folios_set = set(oax_adult_folios)

    # Aggregate asset info at household level
    ah_oax = df_ah[df_ah["folio"].isin(oax_adult_folios_set)].copy()
    if ah_oax.empty:
        return pd.DataFrame({"count": [0]})

    ah_grouped = (
        ah_oax.groupby("folio", as_index=False)
        .agg(
            ah03e=("ah03e", "min"),  # 1 yes, 3 no; min favors 1 if any yes
            ah04e_2=("ah04e_2", "max")  # take a single reported value if duplicated
        )
    )

    # Average value among Oaxaca households with adult that own devices and have reported values
    mask_avg = (ah_grouped["ah03e"] == 1.0) & (ah_grouped["ah04e_2"].notna())
    if not mask_avg.any():
        return pd.DataFrame({"count": [0]})
    avg_val = ah_grouped.loc[mask_avg, "ah04e_2"].mean()

    # Crafts production/sales in last 12 months at household level
    inr_grouped = df_inr.groupby("folio", as_index=False).agg(inr02f=("inr02f", "min"))

    # Candidate households: Oaxaca with adult, produced/sold crafts, have reported electronic device value
    candidates = (
        inr_grouped.loc[inr_grouped["inr02f"] == 1.0, ["folio"]]
        .merge(ah_grouped[["folio", "ah04e_2"]], on="folio", how="left")
    )
    # Restrict to Oaxaca adult households
    candidates = candidates[candidates["folio"].isin(oax_adult_folios_set)]
    # With reported value and above average
    count = int((candidates["ah04e_2"].notna()) & (candidates["ah04e_2"] > avg_val)).sum()

    return pd.DataFrame({"count": [count]})