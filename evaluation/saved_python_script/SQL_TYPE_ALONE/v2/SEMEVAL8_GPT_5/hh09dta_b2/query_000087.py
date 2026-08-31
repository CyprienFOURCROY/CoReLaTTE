import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]

    # Households with at least one member aged 65+
    elderly_folios = (
        df_portad.loc[df_portad["edad"] >= 65, ["folio"]]
        .drop_duplicates()
    )

    # Households that reported a value for total debts + interests
    crh_debts = df_crh.loc[(df_crh["crh04_1"] == 1) & (df_crh["crh04_2"].notna()), ["folio", "crh04_2"]]

    # Elderly households with reported debt value
    elderly_debts = elderly_folios.merge(crh_debts, on="folio", how="inner")

    # Average debt among elderly households with reported value
    avg_debt = elderly_debts["crh04_2"].mean()

    # Households that received a positive amount from Other Government Program
    ogp = df_in.loc[df_in["in02a10"] > 0, ["folio", "in02a10"]]

    # Merge and filter by debt greater than average
    result = (
        elderly_debts.merge(ogp, on="folio", how="inner")
        .loc[lambda d: d["crh04_2"] > avg_debt, ["folio", "crh04_2", "in02a10"]]
        .sort_values(by="crh04_2", ascending=False)
        .reset_index(drop=True)
    )

    return result