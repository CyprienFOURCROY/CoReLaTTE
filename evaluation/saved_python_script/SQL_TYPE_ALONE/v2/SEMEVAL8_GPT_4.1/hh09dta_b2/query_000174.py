def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_in = tables["ii_in"]

    # Households with at least one member aged 60 or older
    hh_60plus = set(df_portad.loc[df_portad["edad"] >= 60, "folio"])
    # Households with at least one member younger than 15
    hh_lt15 = set(df_portad.loc[df_portad["edad"] < 15, "folio"])
    # Households with both
    hh_both_ages = hh_60plus & hh_lt15

    # Households with illness/accident/hospitalization in last 5 years (se01b == 1)
    hh_illness = set(df_se.loc[df_se["se01b"] == 1, "folio"])

    # Households that received income from Other Government Program in last 12 months
    # in01a10_1 == 1 (participates and received income) and in01a10_2 is not null and > 0
    cond_income = (df_in["in01a10_1"] == 1) & (df_in["in01a10_2"].notnull()) & (df_in["in01a10_2"] > 0)
    hh_income = set(df_in.loc[cond_income, "folio"])

    # Intersection of all conditions
    hh_final = hh_both_ages & hh_illness & hh_income

    return pd.DataFrame({"households_count": [len(hh_final)]})