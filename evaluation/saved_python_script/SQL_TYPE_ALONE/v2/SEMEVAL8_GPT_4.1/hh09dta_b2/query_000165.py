def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_crh = tables["ii_crh"]
    df_nna = tables["ii_nna"]

    # 1. Households that experienced a disease/accident/hospitalization in last 5 years
    # se01b == 1 (Yes)
    df_se_filt = df_se[df_se["se01b"] == 1]

    # 2. Households with at least one adult (age 18+)
    df_portad_adult = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = set(df_portad_adult["folio"].unique())

    # 3. Households with a value for total debts + interests (crh04_1 == 1 and crh04_2 not null)
    df_crh_debt = df_crh[(df_crh["crh04_1"] == 1) & (~df_crh["crh04_2"].isna())]
    hh_with_debt = set(df_crh_debt["folio"].unique())

    # 4. Intersection: households that meet all three criteria
    hh_eligible = set(df_se_filt["folio"]) & hh_with_adult & hh_with_debt

    # 5. Prepare merged DataFrame for eligible households
    # Get state info from portad (one row per household)
    df_portad_hh = df_portad.drop_duplicates(subset=["folio"])[["folio", "ent"]]
    # Get non-ag business info from nna (one row per household)
    df_nna_hh = df_nna.drop_duplicates(subset=["folio"])[["folio", "nna01"]]
    # Get debt info from crh (one row per household)
    df_crh_hh = df_crh_debt[["folio", "crh04_2"]].drop_duplicates(subset=["folio"])

    # Merge all info
    df_merged = (
        df_portad_hh[df_portad_hh["folio"].isin(hh_eligible)]
        .merge(df_nna_hh, on="folio", how="left")
        .merge(df_crh_hh, on="folio", how="left")
    )

    # 6. Compute overall average total debt
    overall_avg_debt = df_merged["crh04_2"].mean()

    # 7. Filter to households whose debt exceeds the overall average
    df_above_avg = df_merged[df_merged["crh04_2"] > overall_avg_debt]

    # 8. Group by state and non-ag business ownership, aggregate
    # For nna01: 1=Yes, 2=No, nan=missing
    result = (
        df_above_avg
        .groupby(["ent", "nna01"], dropna=False)
        .agg(
            average_total_debt=("crh04_2", "mean"),
            num_households=("folio", "count")
        )
        .reset_index()
        .rename(columns={"ent": "state", "nna01": "owns_nonag_business"})
    )

    return result