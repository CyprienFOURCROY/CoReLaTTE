import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01", "su231", "su233"]].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()

    avg_pesticide_no_plot = df_su.loc[df_su["su01"] == 3.0, "su233"].mean()

    if pd.isna(avg_pesticide_no_plot):
        return pd.DataFrame({"folio": pd.Series(dtype="object"),
                             "fertilizer_expense": pd.Series(dtype="float64")})

    merged = df_su.merge(df_nna, on="folio", how="inner")

    mask = (
        (merged["su01"] == 1.0) &
        (merged["nna01"] == 1.0) &
        (merged["su231"] > avg_pesticide_no_plot)
    )

    result = (
        merged.loc[mask, ["folio", "su231"]]
        .dropna(subset=["su231"])
        .sort_values("su231", ascending=False)
        .drop_duplicates(subset=["folio"], keep="first")
        .rename(columns={"su231": "fertilizer_expense"})
        .reset_index(drop=True)
    )

    return result