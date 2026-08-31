import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_in = tables["ii_in"]

    # Oaxaca households (ent == 20)
    oax_folios = (
        df_portad.loc[df_portad["ent"] == 20.0, "folio"]
        .dropna()
        .drop_duplicates()
    )
    oax_df = pd.DataFrame({"folio": oax_folios})

    # Oaxaca debts (crh)
    crh_cols = ["folio", "crh04_1", "crh04_2"]
    crh_oax = oax_df.merge(df_crh[crh_cols], on="folio", how="left")

    # Oaxaca average debt (only valid value rows)
    mask_valid_debt = (crh_oax["crh04_1"] == 1.0) & crh_oax["crh04_2"].notna()
    avg_debt = crh_oax.loc[mask_valid_debt, "crh04_2"].mean()

    # If average cannot be computed, return empty
    if pd.isna(avg_debt):
        return pd.DataFrame({"folio": [], "debt_amount": [], "received_amount": []})

    # Oaxaca recipients with positive amount directly from Other Government Program
    in_cols = ["folio", "in02a10"]
    in_oax = oax_df.merge(df_in[in_cols], on="folio", how="left")
    recipients = in_oax.loc[in_oax["in02a10"] > 0]

    # Merge debts for recipients
    rec_with_debt = recipients.merge(df_crh[crh_cols], on="folio", how="left")

    # Filter those with valid debt above Oaxaca average
    valid_rec = rec_with_debt[
        (rec_with_debt["crh04_1"] == 1.0)
        & rec_with_debt["crh04_2"].notna()
        & (rec_with_debt["crh04_2"] > avg_debt)
    ]

    result = valid_rec[["folio", "crh04_2", "in02a10"]].rename(
        columns={"crh04_2": "debt_amount", "in02a10": "received_amount"}
    ).drop_duplicates(subset=["folio"])

    result = result.sort_values(by="debt_amount", ascending=False).reset_index(drop=True)

    return result