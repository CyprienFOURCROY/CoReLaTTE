import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_crh = tables["ii_crh"].copy()

    # Households in Oaxaca with at least one adult (18+)
    portad_oax = df_portad[df_portad["ent"] == 20.0]
    hh_has_adult = (
        portad_oax.groupby("folio")["edad"]
        .apply(lambda s: (s >= 18).any())
        .reset_index(name="has_adult")
    )
    oax_hh_adult = hh_has_adult[hh_has_adult["has_adult"]]

    # Households that own domestic appliances but not a motor vehicle
    ah_agg = (
        df_ah.assign(
            own_domestic=(df_ah["ah03g"] == 1.0),
            own_motor=(df_ah["ah03d"] == 1.0),
        )
        .groupby("folio")
        .agg(own_domestic=("own_domestic", "any"), own_motor=("own_motor", "any"))
        .reset_index()
    )
    hh_assets = ah_agg[(ah_agg["own_domestic"]) & (~ah_agg["own_motor"])][["folio"]]

    # Households that reported an amount paid (value provided)
    crh_paid = df_crh[(df_crh["crh03_1"] == 1.0) & (df_crh["crh03_2"].notna())][
        ["folio", "crh03_2"]
    ]

    # Merge all conditions
    target_hh = (
        oax_hh_adult[["folio"]]
        .merge(hh_assets, on="folio", how="inner")
        .merge(crh_paid, on="folio", how="inner")
    )

    avg_amount = target_hh["crh03_2"].mean()

    return pd.DataFrame({"average_amount_paid": [avg_amount]})