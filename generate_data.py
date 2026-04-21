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


# ─────────────────────────────────────────────────────────────────────────────
# CANCELLATION DATA GENERATOR
# Run separately: python generate_data.py --mode cancel --input "cancellations.xlsx"
# ─────────────────────────────────────────────────────────────────────────────

BAU_DAYS = {
    'booking.com': 7,
    'homeaway': 14, 'vrbo': 14,
    'airbnb': 30,
    'bachcare': 30,
}

def get_threshold(source):
    if not source: return 30
    s = str(source).lower()
    if 'booking.com' in s: return 7
    if 'homeaway' in s or 'vrbo' in s: return 14
    if 'airbnb' in s: return 30
    return 30

def get_source_group(source):
    if not source: return 'Other'
    s = str(source).lower()
    if 'booking.com' in s: return 'Booking.com'
    if 'airbnb' in s: return 'Airbnb'
    if 'homeaway' in s or 'vrbo' in s: return 'HomeAway / VRBO'
    if 'bachcare' in s: return 'Bachcare'
    return 'Other'

def generate_cancellations(input_path: str, output_path: str = 'cancellation_data.json'):
    import pandas as pd
    import json
    from datetime import datetime
    from pathlib import Path

    df = pd.read_excel(input_path)
    df.columns = df.columns.str.strip()

    col_map = {
        'source':      next((c for c in df.columns if 'source' in c.lower()), None),
        'cancel_by':   next((c for c in df.columns if 'cancelled by' in c.lower()), None),
        'cancel_date': next((c for c in df.columns if 'cancelled date' in c.lower()), None),
        'checkin':     next((c for c in df.columns if 'holiday start' in c.lower()), None),
        'reason':      next((c for c in df.columns if 'reason' in c.lower()), None),
        'total_cost':  next((c for c in df.columns if 'total holiday cost' in c.lower()), None),
    }

    rows = []
    for _, r in df.iterrows():
        src = r.get(col_map['source'], '')
        cancel_by = str(r.get(col_map['cancel_by'], '')).strip()
        ctype = 'Owner' if 'owner' in cancel_by.lower() else ('Office' if 'office' in cancel_by.lower() else 'Customer')
        cd = pd.to_datetime(r.get(col_map['cancel_date']), errors='coerce')
        ci = pd.to_datetime(r.get(col_map['checkin']), errors='coerce')
        if pd.isna(cd): continue
        days = int((ci - cd).days) if not pd.isna(ci) else None
        thresh = get_threshold(src)
        is_oob = days is not None and 0 <= days < thresh
        mk = cd.strftime('%Y-%m')
        rows.append({
            'month_key': mk,
            'month_label': cd.strftime('%B %Y'),
            'source_group': get_source_group(src),
            'source': str(src),
            'cancel_by': ctype,
            'days_to_checkin': days,
            'threshold': thresh,
            'is_oob': is_oob,
            'reason': str(r.get(col_map['reason'], '')),
            'total_cost': float(r.get(col_map['total_cost'], 0) or 0),
        })

    months = {}
    for r in rows:
        mk = r['month_key']
        if mk not in months:
            months[mk] = {'label': r['month_label'], 'rows': []}
        months[mk]['rows'].append(r)

    for mk, m in months.items():
        rs = m['rows']
        reasons = {}
        for r in rs:
            k = r['reason'] or 'Not specified'
            reasons[k] = reasons.get(k, 0) + 1
        m.update({
            'total': len(rs),
            'customer': sum(1 for r in rs if r['cancel_by']=='Customer'),
            'owner':    sum(1 for r in rs if r['cancel_by']=='Owner'),
            'office':   sum(1 for r in rs if r['cancel_by']=='Office'),
            'oob':      sum(1 for r in rs if r['is_oob']),
            'by_source': {
                sg: {
                    'total': sum(1 for r in rs if r['source_group']==sg),
                    'oob':   sum(1 for r in rs if r['source_group']==sg and r['is_oob']),
                }
                for sg in ['Booking.com','Airbnb','HomeAway / VRBO','Bachcare','Other']
            },
            'top_reasons': dict(sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:10]),
            'oob_cases': [r for r in rs if r['is_oob']],
        })
        del m['rows']

    out = {
        'generated': datetime.now().isoformat(),
        'months': months,
        'month_list': [{'key':k,'label':v['label']} for k,v in sorted(months.items())]
    }
    Path(output_path).write_text(json.dumps(out, indent=2))
    print(f"✅ Cancellation data → {output_path} ({len(months)} months)")

