"""
generate_data.py
----------------
Run this script to regenerate data.json from your R&R tracker Excel file.
Power Automate will call this automatically on a schedule.

Usage:
    python generate_data.py --input "tracker.xlsx" --output "data.json"
"""

import pandas as pd
import json
import argparse
from datetime import datetime
from pathlib import Path

def generate(input_path: str, output_path: str):
    print(f"Reading: {input_path}")
    df = pd.read_excel(input_path, sheet_name='R&R - FY26', header=12)
    actual = df[df['Case#'].notna() & (df['Case#'] != 'Enter Case#')].copy()
    actual['Creation Date'] = pd.to_datetime(actual['Creation Date'], errors='coerce')
    actual['Case Value Num'] = pd.to_numeric(
        actual['Case Value'].astype(str)
        .str.replace(r'[\$~]', '', regex=True).str.strip(),
        errors='coerce').fillna(0)
    actual['Case Type Clean'] = actual['Case Type'].str.strip().str.lower().apply(
        lambda x: 'Claim' if x == 'claim'
        else ('Feedback' if x in ('feedback', 'reviews') else 'Other'))

    months = actual['Creation Date'].dt.to_period('M').dropna().unique()
    monthly_data = {}

    def fc(df_, s): return int((df_['Funds Status'] == s).sum())
    def fv(df_, s): return round(float(df_[df_['Funds Status'] == s]['Case Value Num'].sum()), 2)

    for period in sorted(months):
        m    = actual[actual['Creation Date'].dt.to_period('M') == period].copy()
        key  = str(period)
        claims   = m[m['Case Type Clean'] == 'Claim']
        feedback = m[m['Case Type Clean'] == 'Feedback']
        open_cl  = claims[claims['Resolved Satisfactorily?'].astype(str) == 'Pending']
        open_days = pd.to_numeric(open_cl['Total # of Days'], errors='coerce').dropna()

        outstanding = {}
        for s in ['MSP - More Info','MSP - Quote/ Book','Guest - No Response',
                  'Guest - Push Back','Owner - Need Response','Contractor - Booked',
                  'Courier Pending (Ordered)','New']:
            c = int((open_cl['CLAIMS - High Level Status'] == s).sum())
            if c > 0: outstanding[s] = c

        issue_counts = {}
        for it in m['Primary Case Type'].dropna().unique():
            c = int((m['Primary Case Type'] == it).sum())
            if c > 0 and str(it) != 'nan': issue_counts[str(it)] = c

        damage = {}
        for dt in ['Claim -Damages','Claim -Additional Cleaning','Claim -Missing Items']:
            sub = claims[claims['Primary Case Type'] == dt]
            damage[dt] = {'count': int(len(sub)), 'value': round(float(sub['Case Value Num'].sum()), 2)}

        monthly_data[key] = {
            'label': period.strftime('%B %Y'),
            'total_cases':    int(len(m)),
            'total_claims':   int(len(claims)),
            'total_feedback': int(len(feedback)),
            'resolved_yes':   int((m['Resolved Satisfactorily?'] == 'Yes').sum()),
            'open_claims':    int(len(open_cl)),
            'avg_days_open':  round(float(open_days.mean()), 1) if len(open_days) > 0 else 0,
            'oldest_days_open': int(open_days.max()) if len(open_days) > 0 else 0,
            'key_account_cases': int((m['Key Account?'] == 'Yes').sum()),
            'funds': {
                'guest_payment': {'count': fc(m,'Guest Payment Received'), 'value': fv(m,'Guest Payment Received')},
                'owner_funded':  {'count': fc(m,'Owner Funded'),           'value': fv(m,'Owner Funded')},
                'gel_funded':    {'count': fc(m,'GEL Funded'),             'value': fv(m,'GEL Funded')},
                'split':         {'count': fc(m,'Split - Advise in notes'),'value': fv(m,'Split - Advise in notes')},
                'no_funds':      {'count': fc(m,'No Funds Required'),      'value': fv(m,'No Funds Required')},
                'pending':       {'count': fc(m,'Pending Recovery'),        'value': fv(m,'Pending Recovery')},
                'written_off':   {'count': fc(m,'FUNDS NOT RECOVERED'),    'value': fv(m,'FUNDS NOT RECOVERED')},
                'airbnb':        {'count': fc(m,'Airbnb Guest Refund'),     'value': fv(m,'Airbnb Guest Refund')},
                'aircover':      {'count': fc(m,'Aircover Recovery'),       'value': fv(m,'Aircover Recovery')},
            },
            'claims_funds': {
                'gel_funded':  {'count': fc(claims,'GEL Funded'),             'value': fv(claims,'GEL Funded')},
                'written_off': {'count': fc(claims,'FUNDS NOT RECOVERED'),    'value': fv(claims,'FUNDS NOT RECOVERED')},
                'owner':       {'count': fc(claims,'Owner Funded'),           'value': fv(claims,'Owner Funded')},
                'recovered':   {'count': fc(claims,'Guest Payment Received'), 'value': fv(claims,'Guest Payment Received')},
            },
            'feedback_funds': {
                'gel':     {'count': fc(feedback,'GEL Funded'),              'value': fv(feedback,'GEL Funded')},
                'owner':   {'count': fc(feedback,'Owner Funded'),            'value': fv(feedback,'Owner Funded')},
                'split':   {'count': fc(feedback,'Split - Advise in notes'), 'value': fv(feedback,'Split - Advise in notes')},
                'no_cost': {'count': fc(feedback,'No Funds Required'),       'value': fv(feedback,'No Funds Required')},
            },
            'outstanding_reasons': outstanding,
            'issue_types': dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:12]),
            'damage_types': damage,
        }

    output = {
        'generated': datetime.now().isoformat(),
        'months': monthly_data,
        'month_list': [{'key': k, 'label': v['label']} for k, v in sorted(monthly_data.items())]
    }

    Path(output_path).write_text(json.dumps(output, indent=2))
    print(f"✅ Written {len(monthly_data)} months → {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',  default='tracker.xlsx')
    parser.add_argument('--output', default='data.json')
    args = parser.parse_args()
    generate(args.input, args.output)
