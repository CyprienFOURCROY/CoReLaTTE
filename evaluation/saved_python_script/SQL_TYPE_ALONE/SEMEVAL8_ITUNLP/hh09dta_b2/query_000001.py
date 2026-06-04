import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Households that feel unsafe or very unsafe at home
    hh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]].drop_duplicates()

    # Households that received a positive amount directly from Other Government Program
    hh_other_gov = df_in[(df_in["in02a10"].notna()) & (df_in["in02a10"] > 0)][["folio"]].drop_duplicates()

    # Households satisfying both conditions
    hh_qualify = pd.merge(hh_unsafe, hh_other_gov, on="folio", how="inner")

    # Individuals living in qualifying households
    ind_qualify = pd.merge(df_portad, hh_qualify, on="folio", how="inner")
    ind_qualify = ind_qualify[ind_qualify["edad"].notna() & ind_qualify["ent"].notna()]

    if ind_qualify.empty:
        return pd.DataFrame(columns=["ent", "average_age", "n_individuals"])

    result = (
        ind_qualify.groupby("ent")
        .agg(average_age=("edad", "mean"), n_individuals=("edad", "size"))
        .reset_index()
        .sort_values("average_age", ascending=False)
        .head(10)
    )

    return result