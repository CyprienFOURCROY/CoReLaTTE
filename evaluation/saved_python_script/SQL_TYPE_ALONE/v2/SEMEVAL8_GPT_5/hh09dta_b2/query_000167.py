import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ls", "edad"]].copy()
    df_in = tables["ii_in"][["folio", "in03a"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Households that received Liconsa milk in the last 12 months
    liconsa_hh = df_in[df_in["in03a"] == 1.0][["folio"]].drop_duplicates()

    # Overall average age among individuals in Liconsa-receiving households
    individuals_liconsa = df_portad.merge(liconsa_hh, on="folio", how="inner")
    avg_age = individuals_liconsa["edad"].mean(skipna=True)

    # Households that feel unsafe or very unsafe
    unsafe_hh = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]].drop_duplicates()

    # Intersection: Liconsa-receiving and unsafe households
    liconsa_unsafe_hh = liconsa_hh.merge(unsafe_hh, on="folio", how="inner")

    # Individuals older than the overall average age in these households
    result = (
        df_portad.merge(liconsa_unsafe_hh, on="folio", how="inner")
        .query("edad > @avg_age")
        [["folio", "ls", "edad"]]
        .sort_values(["folio", "ls"])
        .reset_index(drop=True)
    )

    return result