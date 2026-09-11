def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_nna = tables["ii_nna"]
    
    # Filter households where a member owns/shares a non-agricultural business
    nna_owned = df_nna[df_nna["nna01"] == 1][["folio"]]
    
    # Filter households that participated in and received income from "Other Government Program"
    in_filtered = df_in[
        (df_in["folio"].isin(nna_owned["folio"])) &
        (df_in["in01a10_1"] == 1)  # Participated and received income
    ][["folio", "in02a10"]]  # Amount received directly from the program
    
    # Calculate the mean amount received directly from the program for this group
    mean_amount = in_filtered["in02a10"].mean()
    
    # Select households with amount greater than the group mean
    high_receivers = in_filtered[in_filtered["in02a10"] > mean_amount]
    
    # Order from highest to lowest
    result = high_receivers.sort_values(by="in02a10", ascending=False)[["folio", "in02a10"]]
    
    # Rename columns for clarity
    result = result.rename(columns={"in02a10": "AmountReceived"})
    
    return result.reset_index(drop=True)