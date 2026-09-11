import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_su = tables["ii_su"]

    # Households in Oaxaca with at least one member aged 18+
    adult_oax = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)]
    folios_adult_oax = set(adult_oax["folio"].dropna().unique())

    # Households that use a plot/land for sowing/farming
    su_use = df_su[df_su["su01"] == 1.0]
    folios_su = set(su_use["folio"].dropna().unique())

    # Households that participated and received income from Other Government Program
    # and have a positive directly received amount
    in_prog = df_in[(df_in["in01a10_1"] == 1.0) & (df_in["in02a10"] > 0)]
    folios_in = set(in_prog["folio"].dropna().unique())

    final_folios = folios_adult_oax & folios_su & folios_in
    count = len(final_folios)

    return pd.DataFrame({"households_count": [count]})