def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_se = tables["ii_se"]

    # 1. Find households that received Liconsa milk in the last 12 months
    # in03a == 1 means Yes
    liconsa_households = df_in[df_in["in03a"] == 1.0]["folio"].unique()

    # 2. For these households, count number of adults (age >= 18)
    df_liconsa_portad = df_portad[df_portad["folio"].isin(liconsa_households)]
    df_liconsa_portad_adults = df_liconsa_portad[df_liconsa_portad["edad"] >= 18]
    adults_per_household = df_liconsa_portad_adults.groupby("folio").size()
    avg_adults_liconsa = adults_per_household.mean()

    # 3. For all households, count number of adults (age >= 18)
    df_portad_adults = df_portad[df_portad["edad"] >= 18]
    adults_per_household_all = df_portad_adults.groupby("folio").size()

    # 4. Households with more adults than the average among Liconsa households
    households_more_adults = adults_per_household_all[adults_per_household_all > avg_adults_liconsa].index

    # 5. Households that received Other Government Program with a positive amount
    # in01a10_1 == 1 means received income, in02a10 > 0
    df_in_ogp = df_in[(df_in["in01a10_1"] == 1.0) & (df_in["in02a10"] > 0)]
    ogp_households = df_in_ogp["folio"].unique()

    # 6. Households that experienced illness/accident/hospitalization in last 5 years (se01b == 1)
    df_se_ill = df_se[df_se["se01b"] == 1.0]
    ill_households = df_se_ill["folio"].unique()

    # 7. Intersection: households that meet all three criteria
    eligible_households = set(ogp_households) & set(ill_households) & set(households_more_adults)

    # 8. For these households, get state and amount received directly from Other Government Program
    df_eligible_in = df_in[(df_in["folio"].isin(eligible_households))]
    df_eligible_portad = df_portad[df_portad["folio"].isin(eligible_households)]

    # For each household, get state (ent) and in02a10 (amount)
    # Use only one row per household for in02a10 (since it's household-level)
    df_eligible_in_ogp = df_eligible_in.drop_duplicates(subset=["folio"])[["folio", "in02a10"]]
    df_eligible_portad_state = df_eligible_portad.drop_duplicates(subset=["folio"])[["folio", "ent"]]

    df_merge = df_eligible_in_ogp.merge(df_eligible_portad_state, on="folio", how="inner")

    # Group by state and calculate average amount
    result = (
        df_merge.groupby("ent", as_index=False)["in02a10"]
        .mean()
        .rename(columns={"ent": "state", "in02a10": "avg_amount_received"})
        .sort_values("avg_amount_received", ascending=False)
        .reset_index(drop=True)
    )

    return result