def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_crh = tables["ii_crh"]

    # Adults aged 18 or older
    df_adults = df_portad[df_portad["edad"] >= 18]

    # Merge with ii_vlh on folio to get locality perception
    df_adults_vlh = df_adults.merge(
        df_vlh[["folio", "vlh01k"]],
        on="folio",
        how="left"
    )

    # Only those who "completely disagree" their locality is close (vlh01k == 4)
    df_adults_vlh = df_adults_vlh[df_adults_vlh["vlh01k"] == 4]

    # Merge with ii_crh on folio to get debts
    df_adults_vlh_crh = df_adults_vlh.merge(
        df_crh[["folio", "crh04c"]],
        on="folio",
        how="left"
    )

    # Only those with total debts + interests greater than $5,000 (crh04c == 2)
    df_final = df_adults_vlh_crh[df_adults_vlh_crh["crh04c"] == 2]

    # Group by state and count
    result = (
        df_final.groupby("ent")
        .size()
        .reset_index(name="num_adults")
        .sort_values("ent")
        .reset_index(drop=True)
    )

    return result