def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]

    # Step 1: Households that received Liconsa milk in last 12 months (in03a == 1)
    df_in_liconsa = df_in[df_in["in03a"] == 1]

    # Step 2: Get household IDs (folio) of those households
    folios_liconsa = set(df_in_liconsa["folio"].dropna())

    # Step 3: Individuals in those households
    df_portad_liconsa = df_portad[df_portad["folio"].isin(folios_liconsa)].copy()

    # Step 4: Compute overall average Age Interviewed in these individuals
    avg_age = df_portad_liconsa["edad"].mean()

    # Step 5: Households that feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]
    folios_unsafe = set(df_vlh_unsafe["folio"].dropna())

    # Step 6: Individuals in Liconsa households, in unsafe households, and older than average
    mask = (
        df_portad_liconsa["folio"].isin(folios_unsafe) &
        (df_portad_liconsa["edad"] > avg_age)
    )
    result = df_portad_liconsa.loc[mask, ["folio", "ls", "edad"]].reset_index(drop=True)

    return result