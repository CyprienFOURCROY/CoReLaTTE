def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Filter Oaxaca households
    df_portad_oax = df_portad[df_portad["ent"] == 20.0]

    # Merge with vlh to get 'vlh04' (feel safe at home)
    df_merged = df_portad_oax.merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")

    # Only keep valid answers to 'vlh04' (1,2,3,4)
    valid_vlh04 = [1.0, 2.0, 3.0, 4.0]
    df_merged = df_merged[df_merged["vlh04"].isin(valid_vlh04)]

    # Only adults (age 18+)
    df_merged_adults = df_merged[df_merged["edad"] >= 18]

    # Count adults per household per vlh04
    adults_per_household = (
        df_merged_adults.groupby(["folio", "vlh04"], as_index=False)
        .size()
        .rename(columns={"size": "num_adults"})
    )

    # Average number of adults per household for each vlh04
    avg_adults = (
        adults_per_household.groupby("vlh04")["num_adults"]
        .mean()
        .reset_index()
        .rename(columns={"vlh04": "feel_safe_at_home", "num_adults": "avg_num_adults"})
    )

    # Map codes to labels
    code_to_label = {
        1.0: "very safe",
        2.0: "safe",
        3.0: "unsafe",
        4.0: "very unsafe"
    }
    avg_adults["feel_safe_at_home"] = avg_adults["feel_safe_at_home"].map(code_to_label)

    return avg_adults[["feel_safe_at_home", "avg_num_adults"]]