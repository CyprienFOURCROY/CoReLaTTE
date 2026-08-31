import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]

    # Households with a positive reported value for electronic devices
    folios_with_value = df_ah.loc[df_ah["ah04e_2"].fillna(0) > 0, "folio"].dropna().unique()

    # Household size (number of unique members per household)
    hh_size = (
        df_portad.dropna(subset=["folio"])
        .groupby("folio")["ls"]
        .nunique()
        .reset_index(name="hh_members")
    )

    # Filter to households with positive electronic device value
    filtered = hh_size[hh_size["folio"].isin(folios_with_value)]

    avg_members = filtered["hh_members"].mean()

    return pd.DataFrame({"average_household_members": [avg_members]})