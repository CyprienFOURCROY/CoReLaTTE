import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]

    # Person '01' in Oaxaca
    oax_head = df_portad.loc[
        (df_portad["ent"] == 20.0) & (df_portad["ls"] == "01"),
        ["folio", "edad"]
    ].drop_duplicates(subset=["folio"])

    # Households that reported producing/selling dairy in last 12 months
    dairy_hhs = df_inr.loc[df_inr["inr02a"] == 1.0, ["folio"]].dropna(subset=["folio"]).drop_duplicates()

    merged = oax_head.merge(dairy_hhs, on="folio", how="inner")

    avg_age = merged["edad"].mean()

    return pd.DataFrame({"average_age": [avg_age]})