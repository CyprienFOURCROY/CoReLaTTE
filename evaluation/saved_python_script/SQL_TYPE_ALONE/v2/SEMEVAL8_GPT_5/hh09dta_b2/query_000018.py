import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_nna = tables["ii_nna"]

    # Households in Oaxaca with at least one adult (based on interviewed age)
    hh_oax_adult = df_portad.loc[
        (df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18.0),
        ["folio"]
    ]

    # Households that produced/sold eggs in last 12 months
    hh_eggs = df_inr.loc[df_inr["inr02d"] == 1.0, ["folio"]]

    # Households where a member owns/shares a non-ag business, along with the number of such businesses
    hh_nonag = df_nna.loc[df_nna["nna01"] == 1.0, ["folio", "nna02"]]

    # Combine filters
    merged = hh_oax_adult.merge(hh_eggs, on="folio", how="inner").merge(hh_nonag, on="folio", how="inner")

    avg_businesses = merged["nna02"].mean()

    return pd.DataFrame({"average_non_ag_businesses": [avg_businesses]})