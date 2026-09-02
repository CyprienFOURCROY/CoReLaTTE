def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    se = tables["ii_se"]
    in_df = tables["ii_in"]
    ah = tables["ii_ah"]

    # Filter for Oaxaca (ent == 15)
    oaxaca_portad = portad[portad["ent"] == 15]

    # Merge portad with nna on 'folio'
    portad_nna = pd.merge(oaxaca_portad, nna, on="folio", how="inner")

    # Filter households that own/share non-agricultural business (nna01 == 1)
    households_with_business = portad_nna[portad_nna["nna01"] == 1]

    # Merge with se on 'folio'
    households_se = pd.merge(households_with_business, se, on="folio", how="inner")

    # Filter households where 'se01d' == 1 (lost viv/neg natural disaster in last 5 years)
    households_disaster = households_se[households_se["se01d"] == 1]

    # Merge with in on 'folio'
    households_in = pd.merge(households_disaster, in_df, on="folio", how="inner")

    # Filter households where 'in02a13_1' == 1 (received directly from Other Government Program)
    households_other_gov = households_in[households_in["in02a13_1"] == 1]

    # Merge with ah on 'folio'
    households_ah = pd.merge(households_other_gov, ah, on="folio", how="inner")

    # Filter for adults (edad >= 18)
    adults = households_ah[households_ah["edad"] >= 18]

    # Calculate average age of these adults
    avg_age = adults["edad"].mean()

    # Filter adults older than the average age
    older_adults = adults[adults["edad"] > avg_age]

    # Count unique adults (by 'folio' and 'ls') to avoid double counting
    unique_adults = older_adults.drop_duplicates(subset=["folio", "ls"])

    # Count number of such adults
    count_adults = len(unique_adults)

    return pd.DataFrame({"adults_older_than_avg": [count_adults]})