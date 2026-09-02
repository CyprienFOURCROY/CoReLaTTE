def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]
    df_in = tables["ii_in"]

    # Households where at least one member owns/shares non-ag business (nna01 == 1)
    nna_mask = df_nna["nna01"] == 1.0
    nna_folios = set(df_nna.loc[nna_mask, "folio"])

    # Households where household uses a plot/land for farming (su01 == 1)
    su_mask = df_su["su01"] == 1.0
    su_folios = set(df_su.loc[su_mask, "folio"])

    # Intersection: households that satisfy both conditions
    eligible_folios = nna_folios & su_folios

    # Filter ii_in for eligible households
    df_in_eligible = df_in[df_in["folio"].isin(eligible_folios)].copy()

    # Only positive direct payment from "Other Government Program" (in02a10 > 0)
    df_in_eligible = df_in_eligible[df_in_eligible["in02a10"].notna() & (df_in_eligible["in02a10"] > 0)]

    # Calculate average for such households
    avg_payment = df_in_eligible["in02a10"].mean()

    # Select those above the average
    df_above_avg = df_in_eligible[df_in_eligible["in02a10"] > avg_payment]

    # Prepare result: household ID and amount, sorted highest to lowest
    result = df_above_avg[["folio", "in02a10"]].sort_values("in02a10", ascending=False).reset_index(drop=True)
    result = result.rename(columns={"folio": "household_id", "in02a10": "amount_received"})

    return result