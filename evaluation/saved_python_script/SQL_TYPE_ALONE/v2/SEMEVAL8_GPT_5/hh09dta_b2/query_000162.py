import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()

    merged = pd.merge(df_portad, df_nna, on="folio", how="inner")

    mask_oax_no = (merged["ent"] == 20) & (merged["nna01"] == 2.0)
    avg_age_no_business = merged.loc[mask_oax_no, "edad"].mean()

    if pd.isna(avg_age_no_business):
        return pd.DataFrame(columns=["folio", "ls", "edad"])

    mask_oax_yes = (merged["ent"] == 20) & (merged["nna01"] == 1.0) & (merged["edad"] >= avg_age_no_business)
    result = merged.loc[mask_oax_yes, ["folio", "ls", "edad"]].copy()

    return result.sort_values(by=["folio", "ls"]).reset_index(drop=True)