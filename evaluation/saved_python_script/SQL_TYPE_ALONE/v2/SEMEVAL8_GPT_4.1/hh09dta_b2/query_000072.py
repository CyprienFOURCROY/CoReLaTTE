def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Adults (age 18+) in Oaxaca (ent == 20)
    adults_oaxaca = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)]

    # Merge with household info
    merged = adults_oaxaca.merge(df_vlh, on="folio", how="left")

    # Households that report feeling unsafe or very unsafe at home (vlh04 == 3 or 4)
    unsafe = merged[merged["vlh04"].isin([3.0, 4.0])]

    # Compute Oaxaca average for vlh18a among unsafe households (exclude NaN)
    oaxaca_unsafe = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)].merge(
        df_vlh, on="folio", how="left"
    )
    oaxaca_unsafe = oaxaca_unsafe[oaxaca_unsafe["vlh04"].isin([3.0, 4.0])]
    avg_vlh18a = oaxaca_unsafe["vlh18a"].dropna().mean()

    # Individuals whose household's vlh18a > Oaxaca average (exclude NaN)
    result = unsafe[(unsafe["vlh18a"].notna()) & (unsafe["vlh18a"] > avg_vlh18a)]

    # Return relevant columns: folio, ls (individual id), edad, vlh04, vlh18a
    return result[["folio", "ls", "edad", "vlh04", "vlh18a"]].reset_index(drop=True)