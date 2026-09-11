import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "edad"]].copy()
    df_se = tables["ii_se"][["folio", "se01b"]].copy()
    df_in = tables["ii_in"][["folio", "in01a10_1"]].copy()

    # Age conditions per household
    hh_age = (
        df_portad.groupby("folio").agg(
            has_old=("edad", lambda s: (s >= 60).any()),
            has_young=("edad", lambda s: (s < 15).any()),
        )
        .reset_index()
    )
    hh_age_cond = hh_age.loc[hh_age["has_old"] & hh_age["has_young"], ["folio"]]

    # Household illness/accident/hospitalization in last five years
    se_cond = df_se.loc[df_se["se01b"] == 1, ["folio"]].drop_duplicates()

    # Received income from Other Government Program in last 12 months
    in_cond = df_in.loc[df_in["in01a10_1"] == 1, ["folio"]].drop_duplicates()

    # Intersection of conditions
    res = hh_age_cond.merge(se_cond, on="folio", how="inner").merge(in_cond, on="folio", how="inner")

    count = res["folio"].nunique()

    return pd.DataFrame({"households_count": [count]})