import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].drop_duplicates(subset=["folio"])
    df_su = tables["ii_su"][["folio", "su01"]].drop_duplicates(subset=["folio"])
    df_nna = tables["ii_nna"][["folio", "nna01", "nna02"]].drop_duplicates(subset=["folio"])

    # Filter conditions:
    # - Own/share non-ag business (nna01 == 1)
    # - Valid number of businesses (nna02 not null)
    nna_filtered = df_nna[(df_nna["nna01"] == 1.0) & (df_nna["nna02"].notna())]
    # - Do not use any plot/land for farming (su01 == 3)
    su_filtered = df_su[df_su["su01"] == 3.0]

    # Merge across folio and attach state
    merged = nna_filtered.merge(su_filtered, on="folio", how="inner").merge(df_portad, on="folio", how="inner")

    if merged.empty:
        return pd.DataFrame(columns=["ent", "num_households"])

    grouped = (
        merged.groupby("ent", as_index=False)
        .agg(avg_nna02=("nna02", "mean"), num_households=("folio", "nunique"))
    )

    result = grouped[grouped["avg_nna02"] >= 1.5][["ent", "num_households"]].copy()
    if result.empty:
        return pd.DataFrame(columns=["ent", "num_households"])

    # Ensure state codes are integers (nullable) for readability
    result["ent"] = result["ent"].astype("Int64")
    result = result.sort_values(["ent"]).reset_index(drop=True)
    return result