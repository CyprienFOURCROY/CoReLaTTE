def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    ah = tables["ii_ah"]

    # Filter for Oaxaca (ent == 20)
    oaxaca_portad = portad[portad["ent"] == 20]

    # Filter for adults (edad >= 18)
    adults = oaxaca_portad[oaxaca_portad["edad"] >= 18]

    # Filter for households where at least one member owns a motor vehicle
    # First, get household IDs with motor vehicle ownership
    ah_motor_vehicle = ah[ah["ah03d"] == 1]
    households_with_vehicle = ah_motor_vehicle["folio"].unique()

    # Filter adults in households with at least one member owning a motor vehicle
    adults_with_vehicle = adults[adults["folio"].isin(households_with_vehicle)]

    # Filter for households that report feeling very safe or safe at home (vlh04 == 1 or 2)
    households_safe = vlh[vlh["vlh04"].isin([1, 2])]["folio"].unique()

    # Filter adults living in households that feel very safe or safe
    adults_safe = adults_with_vehicle[adults_with_vehicle["folio"].isin(households_safe)]

    # Calculate the group's average age
    avg_age = adults_safe["edad"].mean()

    # Filter for adults older than this group's average age
    older_adults = adults_safe[adults_safe["edad"] > avg_age]

    # Filter for households that have experienced a forced entry/robbery since 2005
    households_robbed_since_2005 = vlh[
        (vlh["vlh12a"] == 1) | (vlh["vlh12a_b"] == 2)
    ]["folio"].unique()

    # Final selection: older adults in households robbed since 2005
    result = older_adults[older_adults["folio"].isin(households_robbed_since_2005)]

    # Return the count as a DataFrame
    count = len(result)
    return pd.DataFrame({"count": [count]})