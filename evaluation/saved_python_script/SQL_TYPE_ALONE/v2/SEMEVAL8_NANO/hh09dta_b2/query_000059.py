def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    ah = tables["ii_ah"]
    su = tables["ii_su"]
    inr = tables["ii_inr"]

    # Filter households in Oaxaca (ent == 15)
    oaxaca_households = portad[portad["ent"] == 15]

    # Filter households that reported producing or selling eggs in last 12 months (inr02d == 1)
    egg_producers = inr[inr["inr02d"] == 1]
    households_with_eggs = egg_producers[egg_producers["folio"].isin(oaxaca_households["folio"])]

    # Filter households that have at least one member who owns poultry (ah03m == 1)
    ah_poultry = ah[ah["ah03m"] == 1]
    households_with_poultry = ah_poultry[ah_poultry["folio"].isin(households_with_eggs["folio"])]

    # For these households, compute household maximum interviewed age (max of 'edad' per household)
    portad_eggs_poultry = portad[portad["folio"].isin(households_with_poultry["folio"])]
    household_max_age = portad_eggs_poultry.groupby("folio")["edad"].max()

    # Calculate overall average of household maximum ages
    overall_avg_max_age = household_max_age.mean()

    # Filter households where household max age >= overall average
    households_meeting_age_criteria = household_max_age[household_max_age >= overall_avg_max_age].index

    # Count how many of these households are in Oaxaca (already filtered)
    result_count = len(households_meeting_age_criteria)

    return pd.DataFrame(
        {"households_count": [result_count]}
    )