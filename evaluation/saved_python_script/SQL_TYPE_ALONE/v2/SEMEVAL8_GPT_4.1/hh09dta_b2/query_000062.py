def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]

    # Step 1: Households that use land for farming (su01 == 1)
    farming_households = df_su[df_su["su01"] == 1]

    # Step 2: Households with positive seed expenses (su234 > 0)
    farming_with_seed_exp = farming_households[farming_households["su234"] > 0]

    # Step 3: Compute average seed expense among farming households with positive seed expenses
    avg_seed_exp = farming_with_seed_exp["su234"].mean()

    # Step 4: Households that own a motor vehicle (ah03d == 1)
    # ah03d is at the individual level, but we want households, so group by folio
    motor_vehicle_households = df_ah[df_ah["ah03d"] == 1]["folio"].unique()

    # Step 5: Households that use land for farming AND own a motor vehicle
    farming_and_motor = farming_households[farming_households["folio"].isin(motor_vehicle_households)]

    # Step 6: Among these, select those with seed expenses greater than the average
    result = farming_and_motor[
        (farming_and_motor["su234"] > avg_seed_exp)
    ][["folio", "su234"]].copy()

    # Step 7: Order from highest to lowest seed expense
    result = result.sort_values(by="su234", ascending=False).reset_index(drop=True)

    # Rename columns for clarity
    result = result.rename(columns={"su234": "seed_expense"})

    return result