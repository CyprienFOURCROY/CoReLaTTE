def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    ah = tables["ii_ah"]

    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]

    # Filter households that own/share a non-ag business (nna01 == 1)
    nna_sharing = nna[nna["nna01"] == 1]

    # Merge to get households in Oaxaca that own/share non-ag business
    households_in_oaxaca_nna = pd.merge(
        oaxaca_households,
        nna_sharing[["folio"]],
        on="folio",
        how="inner"
    )

    # Merge with household members data (ah) on folio
    household_members = pd.merge(
        households_in_oaxaca_nna,
        ah,
        on="folio",
        how="inner"
    )

    # Filter for adult members (edad >= 18)
    adults = household_members[household_members["edad"] >= 18]

    # Group by household (folio) to count number of adults per household
    adults_count = adults.groupby("folio").size().reset_index(name="adult_count")

    # Merge back to get household info with adult counts
    household_info = pd.merge(
        households_in_oaxaca_nna,
        adults_count,
        on="folio",
        how="left"
    )

    # Fill NaN adult counts with 0 (households with no adults >=18)
    household_info["adult_count"] = household_info["adult_count"].fillna(0)

    # Determine if household owns/shares a domestic appliance (ah03g == 1)
    # Merge with ah to get ah03g status
    household_ah = pd.merge(
        household_info,
        ah[["folio", "ls", "ah03g"]],
        on=["folio", "ls"],
        how="left"
    )

    # For each household, check if at least one member owns a domestic appliance
    household_appliance = household_ah.groupby("folio")["ah03g"].apply(
        lambda x: (x == 1).any()
    ).reset_index(name="has_domestic_appliance")

    # Merge with adult counts
    final_df = pd.merge(
        household_appliance,
        household_info[["folio", "adult_count"]],
        on="folio",
        how="left"
    )

    # Group by whether household has domestic appliance ownership
    result = final_df.groupby("has_domestic_appliance").agg(
        average_adults=("adult_count", "mean"),
        household_count=("folio", "nunique")
    ).reset_index()

    # Map boolean to string for clarity (optional)
    result["has_domestic_appliance"] = result["has_domestic_appliance"].map({True: "Yes", False: "No"})

    return result