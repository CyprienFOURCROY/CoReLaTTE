def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # 1. At least one adult member (age >= 18)
    adults = df_portad[df_portad["edad"] >= 18].groupby("folio", as_index=False).size()
    adults = adults.rename(columns={"size": "adult_count"})
    adults = adults[adults["adult_count"] > 0]

    # 2. At least one member who reports owning the dwelling they live in (ah03a == 1)
    owns_dwelling = df_ah[df_ah["ah03a"] == 1].groupby("folio", as_index=False).size()
    owns_dwelling = owns_dwelling.rename(columns={"size": "owns_count"})
    owns_dwelling = owns_dwelling[owns_dwelling["owns_count"] > 0]

    # 3. At least one member who reports feeling unsafe or very unsafe at home (vlh04 == 3 or 4)
    unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])].groupby("folio", as_index=False).size()
    unsafe = unsafe.rename(columns={"size": "unsafe_count"})
    unsafe = unsafe[unsafe["unsafe_count"] > 0]

    # 4. At least one member who completely agrees or agrees that their locality is close (vlh01k == 1 or 2)
    close = df_vlh[df_vlh["vlh01k"].isin([1.0, 2.0])].groupby("folio", as_index=False).size()
    close = close.rename(columns={"size": "close_count"})
    close = close[close["close_count"] > 0]

    # Intersect all conditions on folio
    eligible = set(adults["folio"]) & set(owns_dwelling["folio"]) & set(unsafe["folio"]) & set(close["folio"])

    result = pd.DataFrame({"households": [len(eligible)]})
    return result