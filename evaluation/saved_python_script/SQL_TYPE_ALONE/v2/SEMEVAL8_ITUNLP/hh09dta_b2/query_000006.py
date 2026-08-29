import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Oaxaca individuals
    oax_ind = df_portad[df_portad["ent"] == 20]

    # Compute Oaxaca average adult age (18+)
    oax_adults = oax_ind[oax_ind["edad"] >= 18]
    avg_adult_age = oax_adults["edad"].mean()

    # Households with at least one adult older than Oaxaca's average adult age
    older_adult_hh = oax_ind[(oax_ind["edad"] >= 18) & (oax_ind["edad"] > avg_adult_age)]
    hh_with_older_adult = set(older_adult_hh["folio"].dropna().unique())

    # Households in Oaxaca
    oax_households = set(oax_ind["folio"].dropna().unique())

    # Filter households that received positive amount from Other Government Program
    df_in_oax = df_in[df_in["folio"].isin(oax_households)]
    df_in_pos = df_in_oax[df_in_oax["in02a10"] > 0]

    # Intersect with households having at least one older adult
    df_target = df_in_pos[df_in_pos["folio"].isin(hh_with_older_adult)]

    # Merge with safety perception
    df_merged = df_target.merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")

    avg_vlh04 = df_merged["vlh04"].mean()
    avg_in02a10 = df_merged["in02a10"].mean()
    num_households = df_merged["folio"].nunique()

    return pd.DataFrame(
        {
            "avg_vlh04": [avg_vlh04],
            "avg_in02a10": [avg_in02a10],
            "num_households": [num_households],
        }
    )