import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_se = tables["ii_se"]

    # Oaxaca code
    oaxaca_code = 20.0

    # Average age in Oaxaca
    avg_age_oax = df_portad.loc[df_portad["ent"] == oaxaca_code, "edad"].mean()

    # Individuals in Oaxaca older than the average age
    older_oax = df_portad.loc[
        (df_portad["ent"] == oaxaca_code) & (df_portad["edad"] > avg_age_oax),
        ["folio"]
    ]

    # Households that reported knowing a family/friend robbed in last 12 months
    hh_rob_last12 = set(
        df_vlh.loc[df_vlh["vlh10a"] == 1.0, "folio"].dropna().unique().tolist()
    )

    # Households that reported no HH member death in last five years
    hh_no_death5y = set(
        df_se.loc[df_se["se01a"] == 3.0, "folio"].dropna().unique().tolist()
    )

    # Eligible households
    eligible_hh = hh_rob_last12 & hh_no_death5y

    # Count individuals meeting all conditions
    count_individuals = int(older_oax["folio"].isin(eligible_hh).sum())

    return pd.DataFrame({"count_individuals": [count_individuals]})