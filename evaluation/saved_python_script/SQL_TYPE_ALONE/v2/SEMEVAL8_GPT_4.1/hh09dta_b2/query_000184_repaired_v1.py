def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]

    # 1. Households where a member owns/shares a non-ag business (nna01 == 1)
    nna_own = df_nna[df_nna["nna01"] == 1][["folio"]].drop_duplicates()

    # 2. Households that reported both borrowing and paying on debts in last 12 months
    # crh02_1: 1=Value (i.e., borrowed), 2=Did not incur debts, 8=DK
    # crh03_1: 1=Value (paid), 2=Did not pay, 3=Do not have debts, 8=DK
    # We want households that borrowed (crh02_1==1) and paid (crh03_1==1)
    crh_borrowed_paid = df_crh[
        (df_crh["crh02_1"] == 1) & (df_crh["crh03_1"] == 1)
    ][["folio", "crh02_2", "crh03_2"]].copy()

    # 3. Compute average borrowed amount among indebted households (crh02_1==1)
    avg_borrowed = df_crh.loc[df_crh["crh02_1"] == 1, "crh02_2"].dropna().mean()

    # 4. Filter households where paid > borrowed and paid > avg_borrowed
    crh_borrowed_paid = crh_borrowed_paid.dropna(subset=["crh02_2", "crh03_2"])
    crh_borrowed_paid = crh_borrowed_paid[
        (crh_borrowed_paid["crh03_2"] > crh_borrowed_paid["crh02_2"]) &
        (crh_borrowed_paid["crh03_2"] > avg_borrowed)
    ]

    # 5. Merge with nna_own to get only those with non-ag business
    eligible_folios = pd.merge(nna_own, crh_borrowed_paid[["folio"]], on="folio", how="inner")

    # 6. Merge with ii_portad to get state (ent)
    # Each folio may appear multiple times in ii_portad (one per individual), but we want unique households
    df_households = df_portad[["folio", "ent"]].drop_duplicates()
    eligible_households = pd.merge(eligible_folios, df_households, on="folio", how="left")

    # 7. Rank states by number of such households
    result = (
        eligible_households.groupby("ent")
        .agg(num_households=("folio", "nunique"))
        .reset_index()
        .sort_values("num_households", ascending=False)
    )

    # Optional: Map state codes to names if desired (not required by instructions)
    return result