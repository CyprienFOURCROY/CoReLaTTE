def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]
    df_crh = tables["ii_crh"]

    # 1. Compute household size for each household
    hh_size = df_portad.groupby("folio").size().rename("hh_size").reset_index()

    # 2. Compute overall average household size
    avg_hh_size = hh_size["hh_size"].mean()

    # 3. Households larger than average
    large_hh = hh_size[hh_size["hh_size"] > avg_hh_size]["folio"]

    # 4. Households with at least one member who owns a motor vehicle (ah03d == 1)
    owns_vehicle = df_ah[df_ah["ah03d"] == 1.0]["folio"].unique()

    # 5. Households where at least one member reports feeling very safe at home (vlh04 == 1)
    very_safe = df_vlh[df_vlh["vlh04"] == 1.0]["folio"].unique()

    # 6. Intersection of all three criteria
    eligible_folios = set(large_hh) & set(owns_vehicle) & set(very_safe)

    # 7. Get total debt + interest (crh04_2) for these households
    df_crh_sel = df_crh[df_crh["folio"].isin(eligible_folios)]

    # Only consider rows where crh04_2 is not null and positive
    debts = df_crh_sel["crh04_2"]
    avg_debt = debts[debts.notnull() & (debts > 0)].mean()

    return pd.DataFrame({"average_total_debt_plus_interest": [avg_debt]})