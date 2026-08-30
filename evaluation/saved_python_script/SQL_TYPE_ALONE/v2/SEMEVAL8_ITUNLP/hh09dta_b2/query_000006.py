import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Oaxaca adult average age (edad >= 18)
    mask_oax_adult = (df_portad["ent"] == 20) & (df_portad["edad"] >= 18)
    avg_adult_age = df_portad.loc[mask_oax_adult, "edad"].mean()

    # Households in Oaxaca with at least one adult older than Oaxaca's average adult age
    mask_oax_older = (df_portad["ent"] == 20) & (df_portad["edad"] >= 18) & (df_portad["edad"] > avg_adult_age)
    oax_older_folios = set(df_portad.loc[mask_oax_older, "folio"].dropna().unique())

    # Households that received positive amount from Other Government Program (in02a10 > 0)
    mask_prog_pos = df_in["in02a10"].notna() & (df_in["in02a10"] > 0)
    df_prog = df_in.loc[mask_prog_pos, ["folio", "in02a10"]]

    # Filter to Oaxaca households with adult older than average
    df_target = df_prog[df_prog["folio"].isin(oax_older_folios)]

    # Merge with vlh to get 'feel safe at home' score (vlh04)
    df_target = df_target.merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")

    avg_vlh04 = df_target["vlh04"].mean()
    avg_in02a10 = df_target["in02a10"].mean()
    n_households = df_target["folio"].nunique()

    return pd.DataFrame(
        {
            "avg_vlh04": [avg_vlh04],
            "avg_in02a10": [avg_in02a10],
            "n_households": [n_households],
        }
    )