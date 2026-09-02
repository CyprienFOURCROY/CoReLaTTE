def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]
    
    # Filter for Oaxaca (ent == 15)
    oaxaca_portad = df_portad[df_portad["ent"] == 15]
    oaxaca_in = df_in[df_in["folio"].isin(oaxaca_portad["folio"])]
    oaxaca_vlh = df_vlh[df_vlh["folio"].isin(oaxaca_portad["folio"])]
    
    # Filter households with amount > 0 from "Other Government Program" (in02a10)
    households_with_program = oaxaca_in[oaxaca_in["in02a10"] > 0]
    
    # Find households with at least one member aged 18+ older than Oaxaca's average adult age
    # Calculate Oaxaca's average age
    avg_age_oaxaca = oaxaca_portad["edad"].mean()
    
    # For each household, check if any member aged 18+ and older than avg_age_oaxaca
    household_age_filter = (
        oaxaca_portad[
            (oaxaca_portad["edad"] >= 18) & (oaxaca_portad["edad"] > avg_age_oaxaca)
        ][["folio"]]
        .drop_duplicates()
    )
    
    # Keep only households that satisfy the age condition
    households_meet_age = households_with_program[
        households_with_program["folio"].isin(household_age_filter["folio"])
    ]
    
    # Merge with vlh to get 'vlh04' (feel safe at home)
    merged = households_meet_age.merge(
        oaxaca_vlh[["folio", "vlh04"]],
        on="folio",
        how="left"
    )
    
    # Calculate average 'vlh04' and average amount received from the program
    avg_vlh04 = merged["vlh04"].mean()
    avg_amount = merged["in02a10"].mean()
    count_households = len(merged)
    
    return pd.DataFrame({
        "average_feel_safe": [avg_vlh04],
        "average_amount": [avg_amount],
        "household_count": [count_households]
    })