def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]
    df_in = tables["ii_in"]
    df_su = tables["ii_su"]
    df_in_en = tables["ii_in_enriched"]
    df_nna_en = tables["ii_nna_enriched"]
    df_su_en = tables["ii_su_enriched"]

    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20][["folio"]].drop_duplicates()

    # Filter households with at least one member aged 18 or older
    adults = df_portad[df_portad["edad"] >= 18][["folio"]].drop_duplicates()
    households_with_adults = pd.merge(oaxaca_households, adults, on="folio", how="inner")

    # Filter households that use a plot of land for farming (su01 == 1)
    su_farming = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Filter households that participated in and received income from "Other Government Program" in last 12 months
    # First, get households with participation in the program
    in_participation = df_in_en[
        (df_in_en["in01a10_1"] == 1) | (df_in_en["in01a10_1"] == 2)
    ][["folio"]].drop_duplicates()

    # Then, filter those with positive directly received amount (in02a10 > 0)
    in_amounts = df_in_en[
        (df_in_en["folio"].isin(in_participation["folio"])) &
        (df_in_en["in02a10"] > 0)
    ][["folio"]].drop_duplicates()

    # Combine all filters
    filtered = households_with_adults[
        households_with_adults["folio"].isin(su_farming["folio"])
    ]
    filtered = filtered[
        filtered["folio"].isin(in_amounts["folio"])
    ]

    # Count households
    count = filtered["folio"].nunique()

    return pd.DataFrame({"household_count": [count]})