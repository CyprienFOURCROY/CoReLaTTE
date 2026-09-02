import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["edad", "ent", "folio"]].copy()
    # Overall average age across all individuals
    overall_avg_age = df_portad["edad"].mean()
    # Average age by state
    avg_age_by_state = df_portad.groupby("ent", dropna=True)["edad"].mean()
    # States with above-overall average age
    valid_states = avg_age_by_state[avg_age_by_state > overall_avg_age].index

    # Households located in valid states
    hh_in_valid_states = set(
        df_portad[df_portad["ent"].isin(valid_states)]["folio"].dropna().unique()
    )

    # Households that lost total crop (se01e == 1)
    df_se = tables["ii_se"][["folio", "se01e"]]
    hh_lost_crop = set(df_se.loc[df_se["se01e"] == 1.0, "folio"].dropna().unique())

    # Households that own/share a non-ag business (nna01 == 1)
    df_nna = tables["ii_nna"][["folio", "nna01"]]
    hh_nonag = set(df_nna.loc[df_nna["nna01"] == 1.0, "folio"].dropna().unique())

    # Intersection
    qualifying_households = hh_in_valid_states & hh_lost_crop & hh_nonag
    count = len(qualifying_households)

    return pd.DataFrame({"households_count": [count]})