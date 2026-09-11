import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "edad"]].copy()
    folios_age = (
        df_portad.loc[(df_portad["edad"] >= 18) & (df_portad["edad"] <= 29), "folio"]
        .dropna()
        .unique()
    )

    df_se = tables["ii_se"][["folio", "se01a", "se01b", "se01c", "se01d", "se01e", "se01f"]].copy()
    shock_cols = ["se01a", "se01b", "se01c", "se01d", "se01e", "se01f"]
    folios_shock = (
        df_se.loc[(df_se[shock_cols] == 1).any(axis=1), "folio"]
        .dropna()
        .unique()
    )

    df_vlh = tables["ii_vlh"][["folio", "vlh18a"]].copy()
    folios_breakin = (
        df_vlh.loc[df_vlh["vlh18a"].fillna(0) > 0, "folio"]
        .dropna()
        .unique()
    )

    final_folios = set(folios_age) & set(folios_shock) & set(folios_breakin)
    final = pd.DataFrame({"folio": list(final_folios)})

    df_nna = tables["ii_nna"][["folio", "nna01", "nna02"]].copy()
    df_nna["nna02_filled"] = df_nna["nna02"]
    df_nna.loc[df_nna["nna01"] == 2, "nna02_filled"] = 0

    merged = final.merge(df_nna[["folio", "nna02_filled"]], on="folio", how="left")
    avg_val = merged["nna02_filled"].mean() if not merged.empty else float("nan")

    return pd.DataFrame({"average_non_ag_businesses_12m": [avg_val]})