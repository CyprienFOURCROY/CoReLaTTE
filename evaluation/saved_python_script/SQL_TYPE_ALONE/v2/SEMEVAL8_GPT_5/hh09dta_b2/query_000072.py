import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # One record per household with state
    hh_state = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])

    # Merge with household safety and break-ins since 2005
    hh_vlh = hh_state.merge(df_vlh[["folio", "vlh04", "vlh18a"]], on="folio", how="inner")

    # Unsafe households in Oaxaca (ent == 20), vlh04 in {3: Unsafe, 4: Very unsafe}
    ox_unsafe_hh = hh_vlh[(hh_vlh["ent"] == 20.0) & (hh_vlh["vlh04"].isin([3.0, 4.0]))]

    # Oaxaca average break-ins since 2005 among unsafe households
    avg_breakins = ox_unsafe_hh["vlh18a"].mean()

    # Households above the Oaxaca average
    hh_above_avg = ox_unsafe_hh[ox_unsafe_hh["vlh18a"] > avg_breakins][["folio", "vlh04", "vlh18a"]]

    # Adults (18+) in Oaxaca living in those households
    adults_ox = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18.0)]
    result = adults_ox.merge(hh_above_avg, on="folio", how="inner")

    result = result[["ent", "folio", "ls", "edad", "vlh04", "vlh18a"]].sort_values(["folio", "ls"]).reset_index(drop=True)
    return result