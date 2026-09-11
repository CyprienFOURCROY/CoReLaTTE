def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_in = tables["ii_in"]

    # 1. Households in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one member aged 18 or older
    df_adult = df_oaxaca[df_oaxaca["edad"] >= 18.0]
    folios_adult = df_adult["folio"].unique()

    # 3. Households that use a plot/land for sowing/farming (su01 == 1)
    df_su_oax = df_su[df_su["folio"].isin(folios_adult)]
    folios_land = df_su_oax[df_su_oax["su01"] == 1.0]["folio"].unique()

    # 4. Households that participated in and received income from Other Government Program (in01a10_1 == 1)
    df_in_oax = df_in[df_in["folio"].isin(folios_land)]
    cond_participate = df_in_oax["in01a10_1"] == 1.0
    # 5. With a positive directly received amount (in02a10 > 0)
    cond_positive = df_in_oax["in02a10"].notna() & (df_in_oax["in02a10"] > 0)
    folios_final = df_in_oax[cond_participate & cond_positive]["folio"].unique()

    count = len(folios_final)
    return pd.DataFrame({"household_count": [count]})