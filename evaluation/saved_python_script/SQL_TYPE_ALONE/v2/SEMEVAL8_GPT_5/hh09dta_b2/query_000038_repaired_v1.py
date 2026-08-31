import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    # Adult flag per person
    df_portad["adult_flag"] = (df_portad["edad"] >= 18).fillna(False)
    # Aggregate to household level
    df_adult = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), adult_present=("adult_flag", "max"))
    )

    df_ah = tables["ii_ah"][["folio", "ah03d"]].copy()
    df_ah["motor_owner_flag"] = (df_ah["ah03d"] == 1.0).fillna(False)
    df_motor = (
        df_ah.groupby("folio", as_index=False)
        .agg(motor_owner_present=("motor_owner_flag", "max"))
    )

    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_vlh["unsafe_flag"] = df_vlh["vlh04"].isin([3.0, 4.0])
    df_unsafe = (
        df_vlh.groupby("folio", as_index=False)
        .agg(unsafe_household=("unsafe_flag", "max"))
    )

    # Merge household-level info
    df_house = (
        df_adult.merge(df_unsafe, on="folio", how="inner")
        .merge(df_motor, on="folio", how="left")
    )
    df_house["motor_owner_present"] = df_house["motor_owner_present"].fillna(False)

    # Oaxaca code is 20
    df_oax_unsafe = df_house[(df_house["ent"] == 20.0) & (df_house["unsafe_household"])]

    n_unsafe = df_oax_unsafe["folio"].nunique()
    n_unsafe_adult_and_motor = df_oax_unsafe[
        df_oax_unsafe["adult_present"] & df_oax_unsafe["motor_owner_present"]
    ]["folio"].nunique()

    return pd.DataFrame(
        {
            "oaxaca_unsafe_households": [int(n_unsafe)],
            "oaxaca_unsafe_with_adult_and_motor_owner": [int(n_unsafe_adult_and_motor)],
        }
    )