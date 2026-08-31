import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_se = tables["ii_se"][["folio", "se01a"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()

    oax_folios = (
        df_portad.loc[df_portad["ent"] == 20.0, "folio"]
        .dropna()
        .drop_duplicates()
    )

    se_yes = df_se[df_se["se01a"] == 1.0][["folio"]].dropna().drop_duplicates()
    su_yes = df_su[df_su["su01"] == 1.0][["folio"]].dropna().drop_duplicates()

    merged = se_yes.merge(su_yes, on="folio", how="inner")
    merged_oax = merged[merged["folio"].isin(oax_folios)]["folio"].drop_duplicates()

    count = int(merged_oax.nunique())

    return pd.DataFrame({"households_count": [count]})