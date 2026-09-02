import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()

    # Identify households by non-ag business ownership status
    folios_yes = set(df_nna.loc[df_nna["nna01"] == 1.0, "folio"])
    folios_no = set(df_nna.loc[df_nna["nna01"] == 2.0, "folio"])

    # Compute average age among individuals in "no" households
    avg_age_no = (
        df_portad.loc[df_portad["folio"].isin(folios_no), "edad"]
        .dropna()
        .mean()
    )

    # If average is NaN (no eligible ages), return empty result
    if pd.isna(avg_age_no):
        return pd.DataFrame({"folio": pd.Series(dtype="object"),
                             "ls": pd.Series(dtype="object"),
                             "edad": pd.Series(dtype="float64")})

    # Select individuals in "yes" households older than the computed average
    result = df_portad.loc[
        (df_portad["folio"].isin(folios_yes)) &
        (df_portad["edad"].notna()) &
        (df_portad["edad"] > avg_age_no),
        ["folio", "ls", "edad"]
    ].copy()

    return result.reset_index(drop=True)