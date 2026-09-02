def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Step 1: Households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # Step 2: Households that own an electronic device (ah03e == 1)
    owns_electronic = df_ah[df_ah["ah03e"] == 1.0][["folio"]].drop_duplicates()

    # Step 3: Households that reported owing money on credit/loans and making payments in last 12 months
    # crh02_1 == 1 (Value) means they owed money
    # crh03_1 == 1 (Value) means they made payments
    # crh03_2 is the amount paid
    crh_valid = df_crh[
        (df_crh["crh02_1"] == 1.0) &
        (df_crh["crh03_1"] == 1.0) &
        (~df_crh["crh03_2"].isna())
    ][["folio", "crh03_2"]]

    # Step 4: Intersection of all conditions
    merged = (
        oaxaca_households
        .merge(owns_electronic, on="folio")
        .merge(crh_valid, on="folio")
    )

    # Step 5: Compute average amount paid
    avg_paid = merged["crh03_2"].mean()

    # Step 6: Filter households that paid more than the average
    result = merged[merged["crh03_2"] > avg_paid].copy()

    # Step 7: Sort from highest to lowest
    result = result.sort_values("crh03_2", ascending=False)

    # Step 8: Return household IDs and amount paid
    return result[["folio", "crh03_2"]].rename(columns={"folio": "household_id", "crh03_2": "amount_paid"}).reset_index(drop=True)