import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "edad"]].drop_duplicates(subset=["folio"])
    df_se = tables["ii_se"][["folio", "se01a"]].drop_duplicates(subset=["folio"])
    df_ah = tables["ii_ah"][["folio", "ah04f_2"]].drop_duplicates(subset=["folio"])

    # Households with at least one member aged 60+ (interpreted as interviewed person aged 60+)
    hh_age60 = set(df_portad.loc[df_portad["edad"] >= 60, "folio"])

    # Households reporting a member’s death in the last five years
    hh_death = set(df_se.loc[df_se["se01a"] == 1.0, "folio"])

    # Compute overall average value of washing machine/stove assets (exclude NaN)
    overall_avg = df_ah["ah04f_2"].mean(skipna=True)

    # Households with total value above overall average
    hh_above_avg = set(df_ah.loc[df_ah["ah04f_2"] > overall_avg, "folio"])

    # Intersection of all three conditions
    eligible_hh = hh_age60.intersection(hh_death).intersection(hh_above_avg)

    return pd.DataFrame({"num_households": [len(eligible_hh)]})