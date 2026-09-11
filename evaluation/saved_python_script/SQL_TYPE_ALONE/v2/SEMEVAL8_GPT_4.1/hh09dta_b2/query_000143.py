def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # 1. Adults (18+) in Oaxaca (ent==20)
    df_adults_oax = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)]

    # 2. Households that report feeling very safe or safe at home (vlh04==1 or 2)
    df_vlh_safe = df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])]

    # 3. Households with at least one member who owns a motor vehicle (ah03d==1)
    df_ah_mv = df_ah[df_ah["ah03d"] == 1.0]
    folios_with_mv = set(df_ah_mv["folio"].unique())

    # 4. Merge adults with safe households and with motor vehicle
    df_merge = df_adults_oax.merge(
        df_vlh_safe[["folio"]], on="folio", how="inner"
    )
    df_merge = df_merge[df_merge["folio"].isin(folios_with_mv)]

    # 5. Compute average age in this group
    avg_age = df_merge["edad"].mean()

    # 6. Households that have experienced a forced entry/robbery since 2005
    # This is vlh12a_a==1 (current dwelling) or vlh12a_b==2 (other dwelling)
    df_vlh_rob = df_vlh[
        (df_vlh["vlh12a_a"] == 1.0) | (df_vlh["vlh12a_b"] == 2.0)
    ]
    folios_robbed = set(df_vlh_rob["folio"].unique())

    # 7. Adults older than average age, in households with forced entry/robbery since 2005
    df_final = df_merge[
        (df_merge["edad"] > avg_age) &
        (df_merge["folio"].isin(folios_robbed))
    ]

    count = len(df_final)

    return pd.DataFrame({"count": [count]})