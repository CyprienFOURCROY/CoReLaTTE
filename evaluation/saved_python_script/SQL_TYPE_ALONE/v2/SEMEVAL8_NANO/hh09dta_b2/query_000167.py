def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]
    df_su = tables["ii_su"]

    # Filter households that received Liconsa milk in the last 12 months
    df_liconsa = df_in[df_in["in03a"] == 1][["folio"]]

    # Merge with portad to get individual data
    merged_portad = pd.merge(df_portad, df_liconsa, on="folio", how="inner")

    # Merge with vlh to get household safety perception
    merged_vlh = pd.merge(merged_portad, df_vlh, on="folio", how="left")

    # Filter individuals living in households that feel unsafe or very unsafe (vlh04 == 3 or 4)
    unsafe_households = merged_vlh[merged_vlh["vlh04"].isin([3, 4])]

    # Calculate overall average age of individuals in Liconsa-receiving households
    ages = merged_portad["edad"]
    overall_avg_age = ages.mean()

    # Filter individuals older than the overall average age
    result = unsafe_households[unsafe_households["edad"] > overall_avg_age]

    # Select relevant columns to return
    return result[["folio", "edad"]]