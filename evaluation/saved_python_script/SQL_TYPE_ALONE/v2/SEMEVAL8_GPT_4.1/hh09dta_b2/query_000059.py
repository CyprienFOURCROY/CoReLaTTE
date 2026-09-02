def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_ah = tables["ii_ah"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_folios = df_portad.loc[df_portad["ent"] == 20, "folio"].unique()

    # 2. Households that reported producing or selling eggs in last 12 months (inr02d == 1)
    egg_selling = df_inr[df_inr["inr02d"] == 1.0]["folio"].unique()

    # 3. Households with at least one member who owns poultry (ah03m == 1)
    poultry_owners = df_ah[df_ah["ah03m"] == 1.0]["folio"].unique()

    # 4. Intersection: Oaxaca & egg-selling & poultry-owning
    eligible_folios = set(oaxaca_folios) & set(egg_selling) & set(poultry_owners)

    # 5. For all egg-selling households (regardless of Oaxaca/poultry), get max interviewed age per household
    egg_selling_folios = set(egg_selling)
    portad_egg = df_portad[df_portad["folio"].isin(egg_selling_folios)]
    max_age_by_folio = portad_egg.groupby("folio")["edad"].max()
    overall_avg_max_age = max_age_by_folio.mean()

    # 6. For eligible households, get their max interviewed age
    portad_eligible = df_portad[df_portad["folio"].isin(eligible_folios)]
    max_age_eligible = portad_eligible.groupby("folio")["edad"].max()

    # 7. Count households with max interviewed age >= overall average
    count = (max_age_eligible >= overall_avg_max_age).sum()

    return pd.DataFrame({"household_count": [int(count)]})