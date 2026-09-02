import pandas as pd


def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    ii_portad = tables['ii_portad'].copy()
    ii_in = tables['ii_in'].copy()
    ii_crh = tables['ii_crh'].copy()

    # Households in Oaxaca with at least one member aged 70 or older
    hh_70plus = (
        ii_portad[(ii_portad['ent'] == 20) & (ii_portad['edad'] >= 70)][['folio']]
        .drop_duplicates()
    )

    # Households that received income from Other Government Program
    hh_in_prog = ii_in[ii_in['in01a10_1'] == 1][['folio']].drop_duplicates()

    # Households that reported having paid something toward debts
    hh_paid_debts = ii_crh[ii_crh['crh03_1'] == 1][['folio']].drop_duplicates()

    # Eligible households meeting all three criteria
    eligible = (
        hh_70plus.merge(hh_in_prog, on='folio', how='inner')
        .merge(hh_paid_debts, on='folio', how='inner')
    )

    # Total debt values among eligible households with explicit total-debt value
    debt = ii_crh[ii_crh['crh04_1'] == 1][['folio', 'crh04_2']].copy()
    debt['crh04_2'] = pd.to_numeric(debt['crh04_2'], errors='coerce')
    debt = debt.dropna(subset=['crh04_2'])

    # If multiple rows per household, take the maximum reported total debt
    debt_agg = debt.groupby('folio', as_index=False)['crh04_2'].max()

    subset = eligible.merge(debt_agg, on='folio', how='inner')

    # Compute average within the subset and filter strictly above average
    avg_debt = subset['crh04_2'].mean()
    result = subset[subset['crh04_2'] > avg_debt][['folio', 'crh04_2']].copy()

    # Sort from highest to lowest debt
    result = result.sort_values('crh04_2', ascending=False).reset_index(drop=True)

    return result
