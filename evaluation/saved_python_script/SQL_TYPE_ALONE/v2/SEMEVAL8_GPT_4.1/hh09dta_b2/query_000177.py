def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_in = tables["ii_in"]

    # Merge all tables on 'folio'
    df = df_portad.merge(df_crh, on="folio", how="inner").merge(df_in, on="folio", how="inner")

    # Filter: reported a numeric value for total debts and interests (crh04_1 == 1 and crh04_2 > 0)
    mask_debt = (df["crh04_1"] == 1) & df["crh04_2"].notna() & (df["crh04_2"] > 0)

    # Filter: received a positive direct amount from Other Government Program (in02a10 > 0 and notna)
    mask_prog = df["in02a10"].notna() & (df["in02a10"] > 0)

    # Apply both filters
    df_valid = df[mask_debt & mask_prog].copy()

    # Oaxaca ent == 20.0
    mask_oaxaca = df_valid["ent"] == 20.0
    mask_other = df_valid["ent"] != 20.0

    # Compute average in02a10 among other states
    avg_other_prog = df_valid.loc[mask_other, "in02a10"].mean()

    # Select Oaxaca households with in02a10 >= avg_other_prog
    df_result = df_valid.loc[
        mask_oaxaca & (df_valid["in02a10"] >= avg_other_prog),
        ["folio", "crh04_2", "in02a10"]
    ].rename(columns={
        "folio": "Household ID",
        "crh04_2": "Total debts+interests (pesos)",
        "in02a10": "Received amount (Other Gov Program)"
    })

    df_result = df_result.reset_index(drop=True)
    return df_result