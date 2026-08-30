import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_ah = tables["ii_ah"].copy()

    # Households in Oaxaca with at least one interviewed aged 30–60
    mask_ent = df_portad["ent"] == 20
    mask_age = df_portad["edad"].ge(30) & df_portad["edad"].le(60)
    hh_oax_age = df_portad.loc[mask_ent & mask_age, ["folio"]].dropna().drop_duplicates()

    # Households that received a positive amount from the Other Government Program
    hh_prog = df_in.loc[df_in["in02a10"].fillna(0) > 0, ["folio"]].dropna().drop_duplicates()

    # Electronic device value recorded for individual 2
    ah_ls2 = (
        df_ah.loc[df_ah["ls"] == 2, ["folio", "ah04e_2"]]
        .dropna(subset=["folio"])
        .groupby("folio", as_index=False, dropna=False)["ah04e_2"]
        .max()
    )

    # Merge criteria: Oaxaca + age condition + positive program + has ls==2 electronic value
    eligible = (
        hh_oax_age.merge(hh_prog, on="folio", how="inner")
        .merge(ah_ls2, on="folio", how="inner")
    )

    # Compute Oaxaca average electronic device value for this group (drop NaNs)
    oax_avg = eligible["ah04e_2"].dropna().mean()

    # Top 10 households with value > Oaxaca average
    result = (
        eligible.loc[eligible["ah04e_2"] > oax_avg, ["folio", "ah04e_2"]]
        .sort_values("ah04e_2", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    return result