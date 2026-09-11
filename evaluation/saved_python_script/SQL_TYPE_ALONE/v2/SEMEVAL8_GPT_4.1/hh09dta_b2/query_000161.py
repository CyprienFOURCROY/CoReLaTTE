def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]

    # Households with at least one resident aged 70 or older
    aged70 = df_portad[df_portad["edad"] >= 70].copy()
    hh_aged70 = set(aged70["folio"].unique())

    # Households that received '70 y más' benefit in last 12 months
    # in01a11_1: 1 = Participates and received income
    df_in_70ymas = df_in[df_in["in01a11_1"] == 1]
    hh_70ymas = set(df_in_70ymas["folio"].unique())

    # Households that feel unsafe or very unsafe at home (vlh04: 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]
    hh_unsafe = set(df_vlh_unsafe["folio"].unique())

    # Households that do NOT report knowing a family/friend kidnapped in last 12 months (vlh10c != 1)
    # Keep only those where vlh10c is not 1 (Yes)
    # If vlh10c is NaN or 3 (No), include
    df_vlh_no_kidnap = df_vlh[~(df_vlh["vlh10c"] == 1.0)]
    hh_no_kidnap = set(df_vlh_no_kidnap["folio"].unique())

    # Intersection of all conditions
    eligible_hh = hh_aged70 & hh_70ymas & hh_unsafe & hh_no_kidnap

    # Get state for each household
    df_portad_hh = df_portad.drop_duplicates("folio")[["folio", "ent"]]
    df_portad_hh = df_portad_hh[df_portad_hh["folio"].isin(eligible_hh)]

    # Count households per state
    result = (
        df_portad_hh.groupby("ent")
        .size()
        .reset_index(name="households")
    )

    # Only states with at least 10 such households
    result = result[result["households"] >= 10]

    # Sort from highest to lowest
    result = result.sort_values("households", ascending=False).reset_index(drop=True)

    # Convert ent to int for clarity
    result["ent"] = result["ent"].astype(int)

    return result