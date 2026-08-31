import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]

    # Households with at least one adult (edad >= 18)
    port = df_portad[["folio", "edad"]].copy()
    port["is_adult"] = port["edad"] >= 18
    adult_households = port.groupby("folio", as_index=False)["is_adult"].max()

    # Households with positive reported value for electronic devices
    elec = df_ah[["folio", "ah04e_2"]].copy()
    elec_positive = elec[elec["ah04e_2"].notna() & (elec["ah04e_2"] > 0)]
    max_elec = elec_positive.groupby("folio", as_index=False)["ah04e_2"].max().rename(columns={"ah04e_2": "max_elec_value"})

    # Eligible households: at least one adult and positive electronic device value
    eligible = max_elec.merge(adult_households, on="folio", how="inner")
    eligible = eligible[eligible["is_adult"]].copy()

    # Death in last 5 years flag from ii_se
    se = df_se[["folio", "se01a"]].copy()
    se["death"] = se["se01a"] == 1
    death_households = se.groupby("folio", as_index=False)["death"].max()

    eligible = eligible.merge(death_households, on="folio", how="left")
    eligible["death"] = eligible["death"].fillna(False)

    overall_avg = eligible["max_elec_value"].mean()
    death_avg = eligible.loc[eligible["death"], "max_elec_value"].mean()

    if pd.isna(death_avg) or pd.isna(overall_avg):
        is_higher = pd.NA
    else:
        is_higher = bool(death_avg > overall_avg)

    return pd.DataFrame(
        {
            "avg_max_electronic_value_death_households": [death_avg],
            "avg_max_electronic_value_overall": [overall_avg],
            "is_death_avg_higher": [is_higher],
        }
    )