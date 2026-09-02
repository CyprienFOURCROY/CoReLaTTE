def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_vlh = tables["ii_vlh"]

    # 1. Households that did NOT produce/sell any listed goods in last 12 months
    inr_cols = [
        'inr02a', 'inr02b', 'inr02c', 'inr02d', 'inr02e', 'inr02f',
        'inr02g', 'inr02h', 'inr02i', 'inr02j', 'inr02k'
    ]
    # All must be 3 (No)
    mask_no_goods = (df_inr[inr_cols] == 3).all(axis=1)

    # 2. Know a family/friend robbed in last 5 years: vlh08a == 1
    mask_knows_robbed = df_vlh['vlh08a'] == 1

    # 3. Merge on 'folio'
    df_merge = df_inr.loc[mask_no_goods, ['folio']].merge(
        df_vlh[['folio', 'vlh04', 'vlh08a']], on='folio', how='inner'
    )
    df_merge = df_merge[mask_knows_robbed.reindex(df_merge.index, fill_value=False)]

    # 4. Merge with state info
    df_merge = df_merge.merge(df_portad[['folio', 'ent']], on='folio', how='left')

    # 5. Households who feel unsafe or very unsafe at home: vlh04 in [3, 4]
    mask_unsafe = df_merge['vlh04'].isin([3, 4])

    # 6. Group by state, count eligible households and unsafe ones
    grouped = df_merge.groupby('ent').agg(
        total_households=('folio', 'count'),
        unsafe_households=('vlh04', lambda x: x.isin([3, 4]).sum())
    ).reset_index()

    # 7. Only states with at least 30 eligible households
    grouped = grouped[grouped['total_households'] >= 30]

    # 8. Compute average number of unsafe households across these states
    avg_unsafe = grouped['unsafe_households'].mean()

    # 9. Filter to states with above-average number of unsafe households
    result = grouped[grouped['unsafe_households'] > avg_unsafe].copy()

    # 10. Sort by unsafe count descending
    result = result.sort_values('unsafe_households', ascending=False)

    # 11. Map state codes to names
    state_map = {
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        9: "Distrito Federal",
        10: "Durango",
        11: "Guanajuato",
        12: "Guerrero",
        13: "Hidalgo",
        14: "Jalisco",
        15: "Estado de México",
        16: "Michoacán",
        17: "Morelos",
        18: "Nayarit",
        19: "Nuevo León",
        20: "Oaxaca",
        21: "Puebla",
        22: "Querétaro",
        25: "Sinaloa",
        26: "Sonora",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas"
    }
    result['state'] = result['ent'].map(state_map)
    result = result[['state', 'total_households', 'unsafe_households']]

    return result.reset_index(drop=True)