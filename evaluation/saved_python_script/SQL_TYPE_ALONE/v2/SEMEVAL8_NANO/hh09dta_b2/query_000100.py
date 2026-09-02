def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_inr = tables["ii_inr"]

    # Filter households with positive amount received from '70 y más' program
    # 'in01a11_1' indicates participation (1: participated and received income)
    # 'in02a11' indicates amount received directly (non-NaN)
    households_with_participation = df_in[
        (df_in["in01a11_1"] == 1) & (df_in["in02a11"].notna())
    ]["folio"].unique()

    # Filter households that participated and received positive amount
    df_participated = df_in[
        (df_in["folio"].isin(households_with_participation))
        & (df_in["in02a11"].notna())
        & (df_in["in02a11"] > 0)
    ]

    # Merge with portad to get age info
    df_merged = pd.merge(
        df_participated,
        df_portad[["folio", "edad"]],
        on="folio",
        how="left"
    )

    # For each household, check if any member is aged 70 or older
    household_age_flag = df_merged.groupby("folio").agg(
        has_70_or_older=pd.NamedAgg(
            column="edad",
            aggfunc=lambda x: any(x >= 70)
        )
    ).reset_index()

    # Merge with portad to get state info
    household_state = pd.merge(
        household_age_flag,
        df_portad[["folio", "ent"]],
        on="folio",
        how="left"
    )

    # Count households per state with at least one member >=70
    at_least_one_70 = household_state[
        household_state["has_70_or_older"]
    ].groupby("ent").size().reset_index(name="count_with_70_or_older")

    # Count households per state with no members >=70
    no_70 = household_state[
        ~household_state["has_70_or_older"]
    ].groupby("ent").size().reset_index(name="count_no_70")

    # Merge results
    result = pd.merge(
        at_least_one_70,
        no_70,
        on="ent",
        how="outer"
    ).fillna(0)

    # Map 'ent' codes to state names
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
    result["state"] = result["ent"].map(state_map)

    # Reorder columns
    result = result[["state", "count_with_70_or_older", "count_no_70"]]

    return result