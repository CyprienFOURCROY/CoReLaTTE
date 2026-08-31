import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_crh = tables["ii_crh"]

    # Households in Oaxaca (ent == 20)
    hh_oaxaca = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # Merge with events and credit/debt info
    merged = (
        hh_oaxaca.merge(df_se[["folio", "se01b"]], on="folio", how="left")
        .merge(df_crh[["folio", "crh04_2"]], on="folio", how="left")
    )

    # Filter: reported disease/accident/hospitalization (se01b == 1) and recorded peso value for total debts + interests
    subset = merged[(merged["se01b"] == 1.0) & (merged["crh04_2"].notna())]

    avg_value = subset["crh04_2"].mean()
    count_above = int((subset["crh04_2"] > avg_value).sum())

    return pd.DataFrame({"households_above_average": [count_above]})