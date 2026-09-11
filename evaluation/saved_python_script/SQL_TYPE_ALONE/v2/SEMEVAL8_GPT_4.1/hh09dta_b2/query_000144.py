def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_in = tables["ii_in"]

    # Step 1: Oaxaca households
    oaxaca_ent = 20.0
    df_oax = df_portad[df_portad["ent"] == oaxaca_ent][["folio"]].drop_duplicates()

    # Step 2: Households that feel very safe or safe at home (vlh04 == 1 or 2)
    df_vlh_oax = df_vlh[df_vlh["folio"].isin(df_oax["folio"])]
    df_safe = df_vlh_oax[df_vlh_oax["vlh04"].isin([1.0, 2.0])]

    # Step 3: Agree people are willing to help their neighbors (vlh01l == 1 or 2)
    df_help = df_safe[df_safe["vlh01l"].isin([1.0, 2.0])]

    # Step 4: Merge with income table for in02a10 (direct amount from Other Government Program)
    df_in_oax = df_in[df_in["folio"].isin(df_help["folio"])]
    # Only consider positive receipts
    df_in_oax_pos = df_in_oax[df_in_oax["in02a10"] > 0]

    # Step 5: Compute average among Oaxaca households with positive receipts
    avg_in02a10 = df_in_oax_pos["in02a10"].mean()

    # Step 6: Households that received above the average
    df_above_avg = df_in_oax_pos[df_in_oax_pos["in02a10"] > avg_in02a10]

    # Step 7: Only count unique households
    n_households = df_above_avg["folio"].nunique()

    return pd.DataFrame({"num_households": [n_households]})