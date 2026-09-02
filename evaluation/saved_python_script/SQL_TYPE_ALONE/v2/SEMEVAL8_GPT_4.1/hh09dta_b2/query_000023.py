def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_in = tables["ii_in"]

    # 1. Filter individuals in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Households that produced/sold meat in last 12 months (inr02c == 1)
    df_meat = df_inr[df_inr["inr02c"] == 1.0]

    # 3. Merge to get individuals in Oaxaca in households that produced/sold meat
    df_ox_meat = df_oaxaca.merge(df_meat[["folio"]], on="folio", how="inner")

    # 4. Merge with ii_in to get in02a10 (amount received from Other Government Program)
    df_ox_meat_in = df_ox_meat.merge(df_in[["folio", "in02a10"]], on="folio", how="left")

    # 5. Compute mean age for such individuals
    mean_age = df_ox_meat_in["edad"].mean()

    # 6. Compute mean in02a10 for such households (use only non-null, positive values)
    mean_in02a10 = df_ox_meat_in["in02a10"].dropna()
    if not mean_in02a10.empty:
        mean_in02a10_val = mean_in02a10.mean()
    else:
        mean_in02a10_val = np.nan

    # 7. Filter: age >= mean_age, in02a10 > mean_in02a10, in02a10 not null
    df_filtered = df_ox_meat_in[
        (df_ox_meat_in["edad"] >= mean_age) &
        (df_ox_meat_in["in02a10"].notnull()) &
        (df_ox_meat_in["in02a10"] > mean_in02a10_val)
    ]

    # 8. Sort by age descending, then by in02a10 descending
    df_sorted = df_filtered.sort_values(["edad", "in02a10"], ascending=[False, False])

    # 9. Select top 10
    df_top10 = df_sorted.head(10)

    # 10. Return required columns
    return df_top10[["folio", "ls", "edad", "in02a10"]].reset_index(drop=True)