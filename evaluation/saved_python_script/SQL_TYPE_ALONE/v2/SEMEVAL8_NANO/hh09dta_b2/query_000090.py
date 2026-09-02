def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    in_df = tables["ii_in"]
    su_df = tables["ii_su"]
    ah_df = tables["ii_ah"]
    crh_df = tables["ii_crh"]

    # Filter households that owed money on credit/loans in last 12 months
    crh_filtered = crh_df[
        (crh_df["crh02_1"] == 1) | (crh_df["crh02_1"] == 2)
    ].copy()

    # Exclude households where 'crh02d' (which indicates debts) is '1' (value) or '8' (DK)
    crh_filtered = crh_filtered[
        ~crh_filtered["crh04_1"].isin([1]) | (crh_filtered["crh04_1"] == 8)
    ]

    # Merge crh with in to get household info
    households = crh_filtered[["folio"]].drop_duplicates()

    # Merge with portad to get 'ent' (state)
    households = households.merge(portad[["folio", "ent"]], on="folio", how="left")

    # Merge with in_df to get participation in Other Government Program (in03c_1)
    households_in = households.merge(in_df[["folio", "in03c_1"]], on="folio", how="left")

    # Filter households where no member participated in Other Government Program (in03c_1 == 3)
    households_no_gov = households_in[
        households_in["in03c_1"] == 3
    ].copy()

    # Merge with ah_df to get individual data
    ah_filtered = ah_df[["folio", "ls", "ah03e"]].copy()

    # Merge with households_no_gov to get relevant households
    merged = households_no_gov.merge(ah_filtered, on="folio", how="left")

    # Filter individuals who own electronic devices (ah03e == 1)
    owners = merged[merged["ah03e"] == 1]

    # Count number of household members owning electronic devices per household
    owners_count = owners.groupby("folio").agg(
        num_owners=pd.NamedAgg(column="ls", aggfunc="count")
    ).reset_index()

    # Merge back with households_no_gov to get all relevant households
    result_df = households_no_gov.merge(owners_count, on="folio", how="left")

    # Fill NaN with 0 for households with no owners
    result_df["num_owners"] = result_df["num_owners"].fillna(0)

    # Calculate average number of household members owning electronic devices
    avg_owners = result_df["num_owners"].mean()

    # Map 'ent' to state names for clarity
    state_map = {
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        9: "Distrito Federal",
        10: "Durango",
        11: "Guanajuato",
        12: "Guerrero",
        13: "Hidalgo",
        14: "Jalisco",
        15: "Estado de México",
        16: "Michoacán",
        17: "Morelos",
        18: "Nayarit",
        19: "Nuevo León",
        20: "Oaxaca",
        21: "Puebla",
        22: "Querétaro",
        25: "Sinaloa",
        26: "Sonora",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas"
    }

    # Prepare final output
    result = pd.DataFrame(
        {
            "state": [state_map.get(ent, "Unknown")],
            "average_number_of_household_members_owning_electronic_devices": [avg_owners]
        }
    )

    return result