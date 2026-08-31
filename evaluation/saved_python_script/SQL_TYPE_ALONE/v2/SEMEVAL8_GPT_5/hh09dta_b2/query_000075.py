import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()

    # Aggregate to household level: average age, presence of a member aged 18–24, and state
    hh = (
        df_portad.groupby("folio")
        .agg(
            ent=("ent", "first"),
            avg_age=("edad", "mean"),
            has_18_24=("edad", lambda s: ((s >= 18) & (s <= 24)).any()),
        )
        .reset_index()
    )

    # Overall average of household average ages
    overall_avg = hh["avg_age"].mean()

    # Households that use a plot/land for farming (su01 == 1)
    su_yes = df_su.loc[df_su["su01"] == 1, ["folio"]].drop_duplicates()

    # Eligible households: use plot, have 18–24 member, and avg age >= overall avg
    eligible = (
        hh.merge(su_yes, on="folio", how="inner")
        .loc[lambda d: d["has_18_24"] & (d["avg_age"] >= overall_avg)]
    )

    # Attach non-ag business ownership indicator
    eligible = eligible.merge(df_nna, on="folio", how="left")

    # For each state, count total eligible households and those with non-ag business (nna01 == 1)
    result = (
        eligible.groupby("ent", dropna=True)
        .agg(
            households_meeting_criteria=("folio", "nunique"),
            households_with_nonag_business=("nna01", lambda s: (s == 1).sum()),
        )
        .reset_index()
    )

    return result