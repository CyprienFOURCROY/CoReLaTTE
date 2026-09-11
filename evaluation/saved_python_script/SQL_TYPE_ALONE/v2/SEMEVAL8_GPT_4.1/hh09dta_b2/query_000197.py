def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]

    # Step 1: Filter for Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # Step 2: Households that use a plot/land for farming (su01 == 1)
    df_su_land = df_su[df_su["su01"] == 1.0]

    # Step 3: Merge to get only Oaxaca households that use land
    df_ox_land = df_oaxaca.merge(df_su_land, on="folio", how="inner")

    # Step 4: Calculate average chemical fertilizer expense among ALL land-using households
    # (regardless of state)
    df_land_all = df_su[df_su["su01"] == 1.0]
    avg_fert = df_land_all["su231"].mean(skipna=True)

    # Step 5: Filter Oaxaca land-using households with fertilizer expense above average
    df_ox_land_above_avg = df_ox_land[df_ox_land["su231"] > avg_fert]

    # Step 6: Select and sort results
    result = df_ox_land_above_avg[["folio", "su231"]].dropna(subset=["su231"])
    result = result.sort_values("su231", ascending=False).reset_index(drop=True)
    result = result.rename(columns={"su231": "chemical_fertilizer_expense"})

    return result