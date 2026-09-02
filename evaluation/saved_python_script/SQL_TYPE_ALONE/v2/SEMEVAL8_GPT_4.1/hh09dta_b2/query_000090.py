def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # 1. Households that owed money on credit/loans in the last 12 months
    # crh02_1 == 1 means "Value" (i.e., they incurred debts)
    df_crh_debt = df_crh[df_crh["crh02_1"] == 1.0][["folio"]].drop_duplicates()

    # 2. Households where NO member participated in Other Government Program
    # in01a10_1 == 3 means "None of the household members participate in the program"
    # For each household, all rows must have in01a10_1 == 3
    df_in_ogp = df_in[["folio", "in01a10_1"]].copy()
    # Find folios where all in01a10_1 == 3
    ogp_no_participation = (
        df_in_ogp.groupby("folio")["in01a10_1"]
        .apply(lambda x: (x == 3.0).all())
    )
    ogp_no_participation = ogp_no_participation[ogp_no_participation].index

    # 3. Filter households that meet both criteria
    eligible_folios = set(df_crh_debt["folio"]) & set(ogp_no_participation)

    # 4. For these households, count number of members who own electronic devices (ah03e == 1)
    df_ah_eligible = df_ah[df_ah["folio"].isin(eligible_folios)]
    df_ah_eligible = df_ah_eligible[df_ah_eligible["ah03e"] == 1.0]

    # 5. For each household, count number of members who own electronic devices
    hh_electronic_counts = (
        df_ah_eligible.groupby("folio").size().rename("num_owners").reset_index()
    )

    # 6. Get state for each household (from ii_portad, one row per folio)
    # Use only one row per folio (e.g., head or first member)
    df_portad_hh = df_portad.drop_duplicates("folio")[["folio", "ent"]]

    # 7. Merge counts with state
    merged = hh_electronic_counts.merge(df_portad_hh, on="folio", how="left")

    # 8. Group by state and calculate average number of members who own electronic devices
    result = (
        merged.groupby("ent")["num_owners"]
        .mean()
        .reset_index()
        .rename(columns={"ent": "state", "num_owners": "avg_num_owners_electronic_devices"})
    )

    return result