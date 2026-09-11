def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_in = tables["ii_in"]

    # 1. Households with at least one member aged 60 or older
    aged60 = df_portad[df_portad["edad"] >= 60].groupby("folio", as_index=False).first()[["folio", "ent"]]

    # 2. Households that report owning electronic devices with a positive stated value
    # ah03e == 1 (owns electronic device), ah04e_2 > 0 (positive value)
    df_ah_elec = df_ah[(df_ah["ah03e"] == 1) & (df_ah["ah04e_2"].notnull()) & (df_ah["ah04e_2"] > 0)]
    # Get max value per household
    elec_max = df_ah_elec.groupby("folio", as_index=False)["ah04e_2"].max()

    # 3. Households that received a positive direct amount from an Other Government Program (in02a10 > 0)
    df_in_ogp = df_in[(df_in["in02a10"].notnull()) & (df_in["in02a10"] > 0)][["folio", "in02a10"]]

    # 4. Merge all filters: must be in all three
    eligible = aged60.merge(elec_max, on="folio").merge(df_in_ogp, on="folio")
    # Now eligible has columns: folio, ent, ah04e_2, in02a10

    # 5. By state (ent), compute average of the maximum reported value of electronic devices per household, and count households
    result = eligible.groupby("ent").agg(
        avg_max_electronic_value=("ah04e_2", "mean"),
        household_count=("folio", "count")
    ).reset_index()

    # Map state codes to names if desired, but not required by instructions
    return result