import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()
    df_ah = tables["ii_ah"].copy()

    # Egg-selling households
    egg_hhs = set(df_inr.loc[df_inr["inr02d"] == 1.0, "folio"].dropna().unique())

    # Household max interviewed age
    hh_max = (
        df_portad.groupby("folio", as_index=False)["edad"]
        .max()
        .rename(columns={"edad": "hh_max_age"})
    )

    # Overall average of household max ages among egg-selling households
    p_egg = hh_max[hh_max["folio"].isin(egg_hhs)].dropna(subset=["hh_max_age"])
    overall_avg = p_egg["hh_max_age"].mean()

    # Oaxaca households (ent == 20)
    ent_by_folio = (
        df_portad.dropna(subset=["ent"])
        .groupby("folio", as_index=False)["ent"]
        .first()
    )
    oax_hhs = set(ent_by_folio.loc[ent_by_folio["ent"] == 20.0, "folio"].unique())

    # Households with at least one member who owns poultry
    poultry_hhs = set(df_ah.loc[df_ah["ah03m"] == 1.0, "folio"].dropna().unique())

    # Target households: Oaxaca ∩ egg-selling ∩ poultry owners
    target_hhs = egg_hhs.intersection(oax_hhs).intersection(poultry_hhs)

    # Count those with hh_max_age >= overall_avg
    target_max = hh_max[hh_max["folio"].isin(target_hhs)].dropna(subset=["hh_max_age"])
    count = int((target_max["hh_max_age"] >= overall_avg).sum())

    return pd.DataFrame({"household_count": [count]})