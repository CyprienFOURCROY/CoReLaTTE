def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    ah = tables["ii_ah"]

    # Filter for Oaxaca (ent == 20)
    oaxaca_portad = portad[portad["ent"] == 20]

    # Filter for adults (edad >= 18)
    adults = oaxaca_portad[oaxaca_portad["edad"] >= 18]

    # Merge with household-level data from crh and ah using 'folio'
    crh_households = crh[["folio", "crh04d", "crh04d"]]
    ah_households = ah[["folio", "ah03d"]]

    # Merge all data on 'folio'
    merged = adults.merge(crh_households, on="folio", how="inner")
    merged = merged.merge(ah_households, on="folio", how="inner")

    # Filter households that own domestic appliances (ah03d == 1)
    has_appliances = merged[merged["ah03d"] == 1]

    # Filter households that do NOT own a motor vehicle (crh04d != 1)
    no_motor_vehicle = has_appliances[has_appliances["crh04d"] != 1]

    # Filter for households that reported an amount paid (crh03_2 is not null and not DK)
    # crh03_2 is the amount paid in pesos
    reported_amount = no_motor_vehicle[
        (no_motor_vehicle["crh03_2"].notnull()) & (no_motor_vehicle["crh03_2"] != 8)
    ]

    # Calculate the average amount paid
    avg_amount = reported_amount["crh03_2"].mean()

    # Return as DataFrame
    return pd.DataFrame(
        {"average_amount_paid": [avg_amount]}
    )