def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]
    df_in = tables["ii_in"]

    # 1. Households with at least one member aged 60+
    aged_60 = df_portad[df_portad["edad"] >= 60]
    hh_aged_60 = set(aged_60["folio"])

    # 2. Households with at least one member with positive value of financial assets/afores
    # ah03h == 1 means owns financial assets/afores, ah04h_2 is the value
    owns_assets = df_ah[(df_ah["ah03h"] == 1) & (df_ah["ah04h_2"].notna()) & (df_ah["ah04h_2"] > 0)]
    hh_assets = set(owns_assets["folio"])

    # 3. Households whose total debts + interests are above the overall average
    # crh04_2 is the value in pesos
    debts = df_crh[df_crh["crh04_2"].notna()]
    avg_debt = debts["crh04_2"].mean()
    hh_high_debt = set(debts[debts["crh04_2"] > avg_debt]["folio"])

    # 4. Intersection: households meeting all three criteria
    eligible_hh = hh_aged_60 & hh_assets & hh_high_debt

    # 5. For these households, get their state
    hh_state = df_portad.drop_duplicates("folio")[["folio", "ent"]].set_index("folio")
    eligible_hh_state = hh_state.loc[list(eligible_hh)].reset_index()

    # 6. For these households, check if any received direct income from Other Government Program (in02a10 > 0)
    # in02a10 is the amount received directly
    in_eligible = df_in[df_in["folio"].isin(eligible_hh)]
    hh_gov_prog = set(in_eligible[in_eligible["in02a10"].notna() & (in_eligible["in02a10"] > 0)]["folio"])

    # 7. Group by state
    eligible_hh_state["received_gov_prog"] = eligible_hh_state["folio"].isin(hh_gov_prog)
    result = (
        eligible_hh_state.groupby("ent")
        .agg(
            households_with_criteria=("folio", "nunique"),
            households_received_gov_prog=("received_gov_prog", "sum")
        )
        .reset_index()
        .rename(columns={"ent": "state"})
    )

    return result