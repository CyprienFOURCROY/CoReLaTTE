def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]

    # Filter Oaxaca individuals
    df_oax = df_portad[df_portad["ent"] == 20.0]

    # Merge with non-ag business info
    df_oax_nna = pd.merge(df_oax, df_nna[["folio", "nna01"]], on="folio", how="left")

    # Households WITHOUT non-ag business (nna01 == 2.0)
    df_no_biz = df_oax_nna[df_oax_nna["nna01"] == 2.0]

    # Compute average age for this group
    avg_age = df_no_biz["edad"].mean()

    # Households WITH non-ag business (nna01 == 1.0)
    df_with_biz = df_oax_nna[df_oax_nna["nna01"] == 1.0]

    # Individuals with age >= average age of non-biz group
    df_result = df_with_biz[df_with_biz["edad"] >= avg_age][["folio", "ls", "edad"]].reset_index(drop=True)

    return df_result