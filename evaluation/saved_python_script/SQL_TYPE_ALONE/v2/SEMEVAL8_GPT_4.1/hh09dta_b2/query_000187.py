def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"]
    df_in = tables["ii_in"]

    # Households where a member uses land for farming (su01 == 1)
    farming_households = df_su[df_su["su01"] == 1][["folio"]]

    # Households that participated in an Other Government Program in the last 12 months (in01a10_1 == 1)
    # and received a positive direct payment (in02a10 > 0)
    df_in_filtered = df_in[
        (df_in["in01a10_1"] == 1) &
        (df_in["in02a10"].notna()) &
        (df_in["in02a10"] > 0)
    ][["folio", "in02a10"]]

    # Merge to get only those households that use land for farming
    merged = pd.merge(farming_households, df_in_filtered, on="folio", how="inner")

    # Calculate the average amount received for this group
    avg_amount = merged["in02a10"].mean()

    # Select households with amount greater than the average
    result = merged[merged["in02a10"] > avg_amount].copy()

    # Rename columns for clarity
    result = result.rename(columns={"folio": "Household ID", "in02a10": "Amount Received"})

    # Reset index for clean output
    result = result.reset_index(drop=True)

    return result[["Household ID", "Amount Received"]]