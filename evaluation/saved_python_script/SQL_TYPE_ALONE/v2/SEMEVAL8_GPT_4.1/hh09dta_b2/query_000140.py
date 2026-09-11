def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]
    df_in = tables["ii_in"]

    # 1. Households that use land for farming: su01 == 1
    su_land = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # 2. Households that own a motor vehicle: ah03d == 1 for any member in the household
    ah_motor = df_ah[df_ah["ah03d"] == 1][["folio"]].drop_duplicates()

    # 3. Households with at least one member aged 60 or older
    portad_60 = df_portad[df_portad["edad"] >= 60][["folio"]].drop_duplicates()

    # Intersect all three sets of folios
    folios = set(su_land["folio"]) & set(ah_motor["folio"]) & set(portad_60["folio"])
    if not folios:
        return pd.DataFrame(columns=["ent", "avg_amount_other_gov_prog"])

    # 4. For these folios, get state (ent)
    eligible_portad = df_portad[df_portad["folio"].isin(folios)][["folio", "ent"]].drop_duplicates()

    # 5. For these folios, get amount received directly from Other Government Program: in02a10
    in_eligible = df_in[df_in["folio"].isin(folios)][["folio", "in02a10"]]

    # Merge to get state and amount
    merged = eligible_portad.merge(in_eligible, on="folio", how="left")

    # Only consider positive, non-null amounts
    merged = merged[merged["in02a10"].notnull() & (merged["in02a10"] > 0)]

    # Group by state and calculate average
    result = (
        merged.groupby("ent", as_index=False)["in02a10"]
        .mean()
        .rename(columns={"in02a10": "avg_amount_other_gov_prog"})
        .sort_values("avg_amount_other_gov_prog", ascending=True)
        .reset_index(drop=True)
    )

    return result