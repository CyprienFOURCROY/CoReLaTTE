import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_crh = tables["ii_crh"].copy()

    # Households in Oaxaca (ent == 20)
    hh_oax = (
        df_portad.loc[:, ["folio", "ent"]]
        .dropna(subset=["folio"])
        .groupby("folio", as_index=False)["ent"]
        .first()
    )
    hh_oax = hh_oax[hh_oax["ent"] == 20.0][["folio"]]

    # Households with at least one member owning motor vehicle and at least one owning financial assets/afores
    ah_grp = (
        df_ah.loc[:, ["folio", "ah03d", "ah03h"]]
        .groupby("folio")
        .agg(
            has_vehicle=("ah03d", lambda s: (s == 1.0).any()),
            has_fin_assets=("ah03h", lambda s: (s == 1.0).any()),
        )
        .reset_index()
    )
    eligible = ah_grp[(ah_grp["has_vehicle"]) & (ah_grp["has_fin_assets"])][["folio"]]

    # Target households: Oaxaca + eligible by assets
    target_hh = hh_oax.merge(eligible, on="folio", how="inner")

    # Get total debts + interests (crh04_2)
    crh_vals = df_crh.loc[:, ["folio", "crh04_1", "crh04_2"]].drop_duplicates(subset=["folio"])
    crh_vals = crh_vals[(crh_vals["crh04_1"] == 1.0) | (crh_vals["crh04_2"].notna())][["folio", "crh04_2"]]

    merged = target_hh.merge(crh_vals, on="folio", how="left")

    avg_val = merged["crh04_2"].mean(skipna=True)

    return pd.DataFrame({"average_total_debts_plus_interest_pesos": [avg_val]})