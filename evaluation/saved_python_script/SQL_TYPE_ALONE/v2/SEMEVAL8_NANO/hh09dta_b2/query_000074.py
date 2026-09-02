def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]
    df_ah_enriched = tables["ii_ah_enriched"]

    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20][["folio"]]

    # Merge with ii_inr to get production/selling info
    merged_inr = pd.merge(oaxaca_households, df_inr, on="folio", how="inner")

    # Filter households that produce/sell crafts (inr02f == 1)
    households_crafts = merged_inr[merged_inr["inr02f"] == 1][["folio"]]

    # Merge with ii_ah_enriched to get ownership info
    merged_ah = pd.merge(households_crafts, df_ah_enriched, on=["folio", "ls"], how="inner")

    # Filter households that own a motor vehicle (ah03d == 1)
    households_motor_vehicle = merged_ah[merged_ah["ah03d"] == 1][["folio"]]

    # Count unique households
    count_households = households_motor_vehicle["folio"].nunique()

    return pd.DataFrame({"count": [count_households]})