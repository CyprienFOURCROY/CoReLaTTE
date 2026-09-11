import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"].copy()
    df_in = tables["ii_in"].copy()
    df_nna = tables["ii_nna"].copy()

    # Oaxaca households with at least one member aged 60+
    df_portad_oax = df_portad.loc[(df_portad["ent"] == 20.0) & (df_portad["edad"].notna()), ["folio", "edad"]]
    if df_portad_oax.empty:
        return pd.DataFrame(columns=["folio", "avg_direct_receipts"])
    df_age = df_portad_oax.groupby("folio", as_index=False)["edad"].max().rename(columns={"edad": "max_age"})
    df_age60 = df_age.loc[df_age["max_age"] >= 60.0, ["folio"]]

    # Use land for farming
    df_su_use = df_su.loc[df_su["su01"] == 1.0, ["folio"]].drop_duplicates()

    # Own/share a non-ag business
    df_nna_own = df_nna.loc[df_nna["nna01"] == 1.0, ["folio"]].drop_duplicates()

    # Reported receiving income from Other Government Program and have direct receipts amount
    df_in_receipts = df_in.loc[df_in["in01a10_1"] == 1.0, ["folio", "in02a10"]]
    df_in_receipts = df_in_receipts.loc[df_in_receipts["in02a10"].notna()]
    if df_in_receipts.empty:
        return pd.DataFrame(columns=["folio", "avg_direct_receipts"])
    df_in_grouped = df_in_receipts.groupby("folio", as_index=False)["in02a10"].mean().rename(columns={"in02a10": "avg_direct_receipts"})

    # Merge all conditions
    merged = (
        df_in_grouped
        .merge(df_su_use, on="folio", how="inner")
        .merge(df_nna_own, on="folio", how="inner")
        .merge(df_age60, on="folio", how="inner")
    )

    if merged.empty:
        return pd.DataFrame(columns=["folio", "avg_direct_receipts"])

    overall_avg = merged["avg_direct_receipts"].mean()
    result = merged.loc[merged["avg_direct_receipts"] > overall_avg, ["folio", "avg_direct_receipts"]]
    result = result.sort_values(by="avg_direct_receipts", ascending=False).reset_index(drop=True)

    return result