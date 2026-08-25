import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_su = tables["ii_su"]

    # Households that use a plot/land for cultivation
    su_mask = df_su["su01"] == 1.0
    folios_su = set(df_su.loc[su_mask, "folio"])

    # Households that reported a death in last 5 years
    death_mask = df_se["se01a"] == 1.0

    # Households that took some coping action (exclude "did nothing" and "DK")
    action_cols_codes = {
        "se05_1a": 1.0,  # Borrowed
        "se05_1b": 2.0,  # Sold any asset
        "se05_1c": 3.0,  # Worked more hours
        "se05_1d": 4.0,  # Worked/developed new activity
        "se05_1e": 5.0,  # Additional job
        "se05_1f": 6.0,  # Left school
        "se05_1g": 7.0,  # Began/sold business
        "se05_1i": 10.0, # Saved
        "se05_1j": 11.0, # Received help family/friends
        "se05_1l": 8.0,  # Other
    }
    action_mask = pd.Series(False, index=df_se.index)
    for col, code in action_cols_codes.items():
        action_mask = action_mask | (df_se[col] == code)

    se_mask = death_mask & action_mask
    folios_se = set(df_se.loc[se_mask, "folio"])

    # Intersection of households meeting all criteria
    qualifying_folios = folios_su.intersection(folios_se)

    # Count individuals in those households by state
    df_filtered = df_portad[df_portad["folio"].isin(qualifying_folios)]
    result = (
        df_filtered.groupby("ent")
        .size()
        .reset_index(name="individuals")
        .sort_values("individuals", ascending=False)
        .reset_index(drop=True)
    )
    return result