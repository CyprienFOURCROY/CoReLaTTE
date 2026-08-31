import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01", "su234"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah03d"]].copy()

    # Farming households
    farming = df_su[df_su["su01"] == 1.0].copy()

    # Average seed expense among farming households with positive seed expenses
    avg_seed = farming.loc[farming["su234"] > 0, "su234"].mean()

    # Households owning a motor vehicle
    own_mv = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Eligible households: farming and own motor vehicle
    eligible = farming.merge(own_mv, on="folio", how="inner")

    # Filter by seed expense greater than the computed average
    eligible = eligible[eligible["su234"].notna() & (eligible["su234"] > avg_seed)]

    result = (
        eligible[["folio", "su234"]]
        .drop_duplicates()
        .sort_values(by="su234", ascending=False)
        .reset_index(drop=True)
    )

    return result