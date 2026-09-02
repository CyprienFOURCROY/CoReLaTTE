import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Households in Oaxaca
    portad_oax = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # Households that own an electronic device
    ah_elec = df_ah[df_ah["ah03e"] == 1.0][["folio"]].drop_duplicates()

    # Households that reported owing money and made payments with known value
    crh_paid = df_crh[
        (df_crh["crh02_1"] == 1.0) &
        (df_crh["crh03_1"] == 1.0) &
        (df_crh["crh03_2"].notna())
    ][["folio", "crh03_2"]].drop_duplicates()

    # Merge filters: Oaxaca + electronic device + paid
    merged = (
        crh_paid
        .merge(portad_oax, on="folio", how="inner")
        .merge(ah_elec, on="folio", how="inner")
    )

    if merged.empty:
        return pd.DataFrame(columns=["folio", "amount_paid_pesos"])

    avg_paid = merged["crh03_2"].mean()

    result = (
        merged[merged["crh03_2"] > avg_paid]
        .sort_values("crh03_2", ascending=False)
        .loc[:, ["folio", "crh03_2"]]
        .rename(columns={"crh03_2": "amount_paid_pesos"})
        .reset_index(drop=True)
    )

    return result