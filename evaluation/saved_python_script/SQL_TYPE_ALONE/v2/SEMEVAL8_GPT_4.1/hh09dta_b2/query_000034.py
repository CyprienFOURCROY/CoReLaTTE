def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]

    # 1. Households that own/share a non-ag business (nna01 == 1)
    nna = df_nna[df_nna["nna01"] == 1.0][["folio"]]

    # 2. Received Liconsa milk in last 12 months (in03a == 1)
    in_liconsa = df_in[df_in["in03a"] == 1.0][["folio"]]

    # 3. Did NOT receive Pronjag (in03b == 3)
    in_no_pronjag = df_in[df_in["in03b"] == 3.0][["folio"]]

    # 4. Participated in and received income from Other Government Program (in01a10_1 == 1)
    in_other_gov = df_in[df_in["in01a10_1"] == 1.0][["folio", "in01a10_2", "in02a10"]]

    # 5. Merge all above filters
    merged = nna.merge(in_liconsa, on="folio") \
                .merge(in_no_pronjag, on="folio") \
                .merge(in_other_gov, on="folio")

    # 6. Compute overall average of directly received amount from Other Government Program (in02a10)
    # Only consider those with non-null in02a10
    valid_in02a10 = merged[~merged["in02a10"].isnull()]
    avg_in02a10 = valid_in02a10["in02a10"].mean()

    # 7. Keep only those with in02a10 > avg_in02a10
    filtered = valid_in02a10[valid_in02a10["in02a10"] > avg_in02a10].copy()

    # 8. Get state for each household
    filtered = filtered.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # 9. For each household, check if they paid any money on debts/loans in last 12 months
    # crh03_1 == 1 means paid, crh03_2 is the amount (should be > 0)
    crh_paid = df_crh[df_crh["crh03_1"] == 1.0][["folio"]]
    filtered["paid_on_debts"] = filtered["folio"].isin(crh_paid["folio"])

    # 10. Group by state and count
    result = filtered.groupby("ent").agg(
        total_households=("folio", "nunique"),
        households_paid_on_debts=("paid_on_debts", "sum")
    ).reset_index().rename(columns={"ent": "state"})

    return result