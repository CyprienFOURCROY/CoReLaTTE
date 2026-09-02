def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_inr = tables["ii_inr"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # 2. Households that own a motor vehicle (ah03d == 1)
    motor_vehicle = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # 3. Households that produced/sold crafts in last 12 months (inr02f == 1)
    crafts = df_inr[df_inr["inr02f"] == 1.0][["folio"]].drop_duplicates()

    # 4. Intersection: Oaxaca & own motor vehicle & produced/sold crafts
    result = oaxaca_households.merge(motor_vehicle, on="folio")
    result = result.merge(crafts, on="folio")

    count = len(result["folio"].unique())

    return pd.DataFrame({"households": [count]})