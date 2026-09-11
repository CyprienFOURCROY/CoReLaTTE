def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    crh = tables["ii_crh"]

    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20][["folio"]].drop_duplicates()

    # Filter households that own a motor vehicle (ah03d == 1)
    ah_motor_vehicles = ah[ah["ah03d"] == 1][["folio", "ah04d_2"]]
    # Keep only households with reported value for total debts and interests (ah04d_2 not null)
    ah_motor_vehicles = ah_motor_vehicles[ah_motor_vehicles["ah04d_2"].notna()]

    # Merge households in Oaxaca with those owning motor vehicles
    households_in_oaxaca_with_motor = pd.merge(
        oaxaca_households,
        ah_motor_vehicles,
        on="folio",
        how="inner"
    )

    # Merge with crh to get household info
    households_full = pd.merge(
        households_in_oaxaca_with_motor,
        crh[["folio", "crh04_2"]],
        on="folio",
        how="inner"
    )

    # Filter households that reported a value for total debts and interests (crh04_2 not null)
    households_full = households_full[households_full["crh04_2"].notna()]

    # Merge back with ah to get motor vehicle value
    ah_details = pd.merge(
        households_full[["folio"]],
        ah[["folio", "ah04d_2"]],
        on="folio",
        how="left"
    )

    # Filter households that reported a value for motor vehicle
    ah_details = ah_details[ah_details["ah04d_2"].notna()]

    # Calculate the mean of the motor vehicle value
    avg_value = ah_details["ah04d_2"].mean()

    return pd.DataFrame(
        {"average_motor_vehicle_value": [avg_value]}
    )