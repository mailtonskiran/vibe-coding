from app import db, FundMaster, AssetAllocation

# --- Master Fund List ---
fund_list = [
    # Equity
    {"fund_name": "Large Cap Equity Fund", "asset_class": "equity", "category": "Large Cap", "expected_return": 12.0, "risk_level": "Medium", "min_investment": 5000},
    {"fund_name": "Mid Cap Equity Fund", "asset_class": "equity", "category": "Mid Cap", "expected_return": 14.0, "risk_level": "High", "min_investment": 5000},
    {"fund_name": "Small Cap Equity Fund", "asset_class": "equity", "category": "Small Cap", "expected_return": 16.0, "risk_level": "High", "min_investment": 5000},
    {"fund_name": "Multi Cap Equity Fund", "asset_class": "equity", "category": "Multi Cap", "expected_return": 13.0, "risk_level": "Medium", "min_investment": 5000},
    # Hybrid/BAF
    {"fund_name": "Balanced Advantage Fund", "asset_class": "hybrid_baf", "category": "Balanced Advantage", "expected_return": 10.0, "risk_level": "Medium", "min_investment": 1000},
    {"fund_name": "Aggressive Hybrid Fund", "asset_class": "hybrid_baf", "category": "Aggressive Hybrid", "expected_return": 11.0, "risk_level": "Medium", "min_investment": 1000},
    {"fund_name": "Multi Asset Fund", "asset_class": "hybrid_baf", "category": "Multi Asset", "expected_return": 10.5, "risk_level": "Medium", "min_investment": 1000},
    # Debt/Arbitrage
    {"fund_name": "Liquid Fund", "asset_class": "debt_arbitrage", "category": "Liquid", "expected_return": 6.0, "risk_level": "Low", "min_investment": 1000},
    {"fund_name": "Ultra Short Duration Fund", "asset_class": "debt_arbitrage", "category": "Ultra Short", "expected_return": 6.5, "risk_level": "Low", "min_investment": 1000},
    {"fund_name": "Corporate Bond Fund", "asset_class": "debt_arbitrage", "category": "Corporate Bond", "expected_return": 7.0, "risk_level": "Low", "min_investment": 1000},
    # International Equity
    {"fund_name": "US Equity Fund", "asset_class": "international_equity", "category": "US Equity", "expected_return": 11.0, "risk_level": "Medium", "min_investment": 1000},
    {"fund_name": "Global Equity Fund", "asset_class": "international_equity", "category": "Global Equity", "expected_return": 10.0, "risk_level": "Medium", "min_investment": 1000},
    # Gold
    {"fund_name": "Gold ETF", "asset_class": "gold", "category": "ETF", "expected_return": 7.0, "risk_level": "Low", "min_investment": 1000},
    {"fund_name": "Gold Fund of Funds", "asset_class": "gold", "category": "FoF", "expected_return": 6.5, "risk_level": "Low", "min_investment": 1000},
]

# --- Asset Allocation Matrix ---
allocation_matrix = [
    # Conservative
    {"risk_profile": "Conservative", "asset_class": "equity", "percentage": 10},
    {"risk_profile": "Conservative", "asset_class": "hybrid_baf", "percentage": 20},
    {"risk_profile": "Conservative", "asset_class": "debt_arbitrage", "percentage": 60},
    {"risk_profile": "Conservative", "asset_class": "international_equity", "percentage": 5},
    {"risk_profile": "Conservative", "asset_class": "gold", "percentage": 5},
    # Cautious
    {"risk_profile": "Cautious", "asset_class": "equity", "percentage": 25},
    {"risk_profile": "Cautious", "asset_class": "hybrid_baf", "percentage": 35},
    {"risk_profile": "Cautious", "asset_class": "debt_arbitrage", "percentage": 30},
    {"risk_profile": "Cautious", "asset_class": "international_equity", "percentage": 5},
    {"risk_profile": "Cautious", "asset_class": "gold", "percentage": 5},
    # Moderate
    {"risk_profile": "Moderate", "asset_class": "equity", "percentage": 50},
    {"risk_profile": "Moderate", "asset_class": "hybrid_baf", "percentage": 25},
    {"risk_profile": "Moderate", "asset_class": "debt_arbitrage", "percentage": 15},
    {"risk_profile": "Moderate", "asset_class": "international_equity", "percentage": 5},
    {"risk_profile": "Moderate", "asset_class": "gold", "percentage": 5},
    # Aggressive
    {"risk_profile": "Aggressive", "asset_class": "equity", "percentage": 70},
    {"risk_profile": "Aggressive", "asset_class": "hybrid_baf", "percentage": 15},
    {"risk_profile": "Aggressive", "asset_class": "debt_arbitrage", "percentage": 5},
    {"risk_profile": "Aggressive", "asset_class": "international_equity", "percentage": 7},
    {"risk_profile": "Aggressive", "asset_class": "gold", "percentage": 3},
]

def populate_fund_master():
    for fund in fund_list:
        exists = FundMaster.query.filter_by(fund_name=fund["fund_name"]).first()
        if not exists:
            db.session.add(FundMaster(**fund))
    db.session.commit()
    print(f"Inserted {len(fund_list)} funds into FundMaster table.")

def populate_asset_allocation():
    for row in allocation_matrix:
        exists = AssetAllocation.query.filter_by(risk_profile=row["risk_profile"], asset_class=row["asset_class"]).first()
        if not exists:
            db.session.add(AssetAllocation(**row))
    db.session.commit()
    print(f"Inserted {len(allocation_matrix)} asset allocations.")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        populate_fund_master()
        populate_asset_allocation()
