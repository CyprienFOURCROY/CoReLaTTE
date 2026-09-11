def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    
    # Filter households in Oaxaca that reported receiving Liconsa milk in the last 12 months
    # in 'in01a2_1' column: 1 means participated and received income, 8 means DK
    oaxaca_mask = (
        (df_in["in01a2_1"] == 1)  # Participated and received income
    )
    df_liconsa = df_in[oaxaca_mask][["folio"]]
    
    # Merge with portad to get household info
    df_households = pd.merge(df_liconsa, df_portad, on="folio", how="inner")
    
    # Calculate overall average age of household members in Oaxaca households with Liconsa
    overall_avg_age = df_households["edad"].mean()
    
    # Filter households in Oaxaca with Liconsa and household average age above overall average
    # First, compute household average age
    household_avg_age = (
        df_portad[df_portad["folio"].isin(df_households["folio"])]
        .groupby("folio")["edad"]
        .mean()
        .reset_index()
    )
    # Keep only households with average age above overall average
    households_above_avg = household_avg_age[household_avg_age["edad"] > overall_avg_age]
    
    # Get the list of folios meeting the age criterion
    folios_filtered = households_above_avg["folio"]
    
    # Filter the households in these folios
    df_filtered = df_households[df_households["folio"].isin(folios_filtered)]
    
    # Merge with 'ii_ah' to get electronic devices ownership info
    df_ah_filtered = pd.merge(df_filtered, df_ah[["folio", "ah04e_1"]], on="folio", how="left")
    
    # Replace NaN with 0 for 'ah04e_1' (no electronic devices reported)
    df_ah_filtered["ah04e_1"] = df_ah_filtered["ah04e_1"].fillna(0)
    
    # Calculate the total value of electronic devices for each household
    total_value_electronic_devices = df_ah_filtered["ah04e_1"]
    
    # Calculate the mean total value
    avg_total_value = total_value_electronic_devices.mean()
    
    # Count the number of households meeting the criteria
    count_households = len(df_ah_filtered)
    
    # Return as DataFrame
    return pd.DataFrame(
        {
            "average_total_value_electronic_devices": [avg_total_value],
            "household_count": [count_households]
        }
    )