def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]["folio"]
    
    # Filter households that received direct income from "in02a13" (Opciones Productivas)
    in_households = df_in[
        (df_in["folio"].isin(oaxaca_households)) &
        (df_in["in02a13"] == 1)
    ][["folio", "in02a13"]]
    
    # Filter out households with missing amount (NaN)
    in_households = in_households.dropna(subset=["in02a13"])
    
    # Calculate the overall average amount received among all recipients
    overall_avg = in_households["in02a13"].mean()
    
    # Select households with amount exceeding the overall average
    high_receivers = in_households[
        in_households["in02a13"] > overall_avg
    ][["folio", "in02a13"]]
    
    # Rename columns for clarity
    result = high_receivers.rename(columns={"in02a13": "amount_received"})
    
    return result.reset_index(drop=True)