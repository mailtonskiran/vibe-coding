from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mutual_funds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class FundMaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fund_name = db.Column(db.String(100), nullable=False)
    asset_class = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))
    expected_return = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20))
    min_investment = db.Column(db.Float, nullable=False)

class AssetAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    risk_profile = db.Column(db.String(30), nullable=False)
    asset_class = db.Column(db.String(50), nullable=False)
    percentage = db.Column(db.Float, nullable=False)

class Investor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    
    # Enhanced Demographics
    education_level = db.Column(db.String(50), nullable=False)  # High School, Some College, Graduate, Post Graduate
    occupation_type = db.Column(db.String(50), nullable=False)  # Self Employed, Business, Salaried-Govt, Salaried-Private, Retired
    annual_income_range = db.Column(db.String(50), nullable=False)  # Income brackets
    
    # Financial Information
    monthly_income = db.Column(db.Float, nullable=False)
    monthly_expenses = db.Column(db.Float, nullable=False)
    existing_assets = db.Column(db.Float, nullable=False)
    existing_liabilities = db.Column(db.Float, nullable=False)
    emergency_fund = db.Column(db.Float, nullable=False)
    
    # Investment Details
    investment_amount = db.Column(db.Float, nullable=False)
    investment_horizon = db.Column(db.String(20), nullable=False)  # Upto 3 years, 3-5 years, 5+ years, 7+ years
    required_return = db.Column(db.Float, nullable=False)
    equity_experience = db.Column(db.String(20), nullable=False)  # None, Less than 3 years, More than 3 years
    
    # Goals and Risk Assessment
    financial_goals = db.Column(db.Text, nullable=False)
    
    # Risk Assessment Questionnaire Responses (12 questions)
    risk_q1 = db.Column(db.String(1), nullable=False)  # A, B, C, D
    risk_q1_reason = db.Column(db.Text)  # For A and D responses
    risk_q2 = db.Column(db.String(1), nullable=False)
    risk_q3 = db.Column(db.String(1), nullable=False)
    risk_q4 = db.Column(db.String(1), nullable=False)
    risk_q5 = db.Column(db.String(1), nullable=False)
    risk_q6 = db.Column(db.String(1), nullable=False)
    risk_q7 = db.Column(db.String(1), nullable=False)
    risk_q8 = db.Column(db.String(1), nullable=False)
    risk_q8_reason = db.Column(db.Text)  # For A and D responses
    risk_q9 = db.Column(db.String(1), nullable=False)
    risk_q10 = db.Column(db.String(1), nullable=False)
    risk_q11 = db.Column(db.String(1), nullable=False)
    risk_q12 = db.Column(db.String(1), nullable=False)
    
    # Additional Profile Questions (7 questions)
    profile_q1 = db.Column(db.String(1), nullable=False)  # Risk-return comfort scenario
    profile_q2 = db.Column(db.String(1), nullable=False)  # Low-risk allocation preference
    profile_q3 = db.Column(db.String(1), nullable=False)  # Reaction to 30% loss
    profile_q4 = db.Column(db.String(1), nullable=False)  # Volatility association (duplicate of risk_q2 - will use this version)
    profile_q5 = db.Column(db.String(1), nullable=False)  # Existing portfolio description
    profile_q6 = db.Column(db.String(1), nullable=False)  # Mutual fund familiarity
    profile_q7 = db.Column(db.String(1), nullable=False)  # Investment horizon with Happy Investor
    
    # Calculated Risk Profile
    risk_score = db.Column(db.Integer, nullable=False)  # Sum of all responses (12-48)
    profile_score = db.Column(db.Integer, nullable=False)  # Sum of profile responses (7-28)
    combined_score = db.Column(db.Integer, nullable=False)  # Combined risk + profile score
    risk_tolerance = db.Column(db.String(20), nullable=False)  # Conservative, Moderate, Aggressive
    
    # Relationships
    portfolios = db.relationship('Portfolio', backref='investor', lazy=True)
    
    def calculate_risk_score(self):
        """Calculate risk score based on questionnaire responses (12-48 range)"""
        score_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        total_score = (
            score_map[self.risk_q1] + score_map[self.risk_q2] + score_map[self.risk_q3] +
            score_map[self.risk_q4] + score_map[self.risk_q5] + score_map[self.risk_q6] +
            score_map[self.risk_q7] + score_map[self.risk_q8] + score_map[self.risk_q9] +
            score_map[self.risk_q10] + score_map[self.risk_q11] + score_map[self.risk_q12]
        )
        # Convert to 120-480 scale (multiply by 10)
        return total_score * 10

    def calculate_profile_score(self):
        """Calculate profile score based on the 7 additional profile questions."""
        score_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        total_score = (
            score_map[self.profile_q1] + score_map[self.profile_q2] + score_map[self.profile_q3] +
            score_map[self.profile_q4] + score_map[self.profile_q5] + score_map[self.profile_q6] +
            score_map[self.profile_q7]
        )
        return total_score

    def calculate_combined_score(self):
        """Calculate the combined score from the risk and profile scores."""
        # This assumes risk_score and profile_score have been calculated and set on the instance
        return self.risk_score + self.profile_score
    
    def calculate_demographic_score(self):
        """Calculate demographic score based on education, occupation, income, experience"""
        score = 0
        
        # Education Level scoring
        education_scores = {
            'High School': 0,
            'Some College but not graduate': 1,
            'Graduate': 2,
            'Post Graduate': 3
        }
        score += education_scores.get(self.education_level, 0)
        
        # Occupation Type scoring
        occupation_scores = {
            'Retired': 0,
            'Salaried – Govt': 1,
            'Salaried – Private sector': 2,
            'Self Employed': 3,
            'Business': 4
        }
        score += occupation_scores.get(self.occupation_type, 0)
        
        # Annual Income Range scoring
        income_scores = {
            'Upto Rs 5 lacs': 0,
            'Between Rs 5 – 10 lacs': 1,
            'Between Rs 10 20 lacs': 2,
            'Between Rs 20 -50 lacs': 3,
            'Above Rs 50 lacs': 4
        }
        score += income_scores.get(self.annual_income_range, 0)
        
        # Equity Experience scoring
        experience_scores = {
            'None': 0,
            'Less than 3 years': 1,
            'More than 3 years': 2
        }
        score += experience_scores.get(self.equity_experience, 0)
        
        return min(score, 7)  # Cap at 7 as per matrix
    
    def determine_risk_category(self):
        """Determine final risk category using risk score and demographic score matrix"""
        risk_score = self.calculate_risk_score()
        demo_score = self.calculate_demographic_score()
        
        # Risk categorization matrix
        if risk_score <= 150:
            if demo_score <= 5:
                return 'Conservative Investor', 'CON I'
            else:
                return 'Cautious Investor', 'CAU I'
        elif risk_score <= 200:
            if demo_score <= 1:
                return 'Conservative Investor', 'CON I'
            elif demo_score <= 5:
                return 'Cautious Investor', 'CAU I'
            else:
                return 'Moderate Investor', 'MI'
        elif risk_score <= 300:
            if demo_score <= 1:
                return 'Cautious Investor', 'CAU I'
            elif demo_score <= 5:
                return 'Moderate Investor', 'MI'
            else:
                return 'Aggressive Investor', 'AI'
        else:  # 301 & Above
            if demo_score == 0:
                return 'Cautious Investor', 'CAU I'
            elif demo_score == 1:
                return 'Moderate Investor', 'MI'
            else:
                return 'Aggressive Investor', 'AI'
    
    def determine_risk_tolerance(self):
        """Determine risk tolerance based on final risk category"""
        category, _ = self.determine_risk_category()
        if 'Conservative' in category:
            return 'Conservative'
        elif 'Cautious' in category:
            return 'Cautious'  # Keep cautious separate for asset allocation
        elif 'Moderate' in category:
            return 'Moderate'
        else:
            return 'Aggressive'
    
    def get_asset_allocation(self):
        """Get recommended asset allocation based on risk profile"""
        risk_tolerance = self.determine_risk_tolerance()
        
        # Query asset allocation from database
        allocation_rows = AssetAllocation.query.filter_by(risk_profile=risk_tolerance).all()
        
        # Convert to dictionary format
        allocation = {}
        for row in allocation_rows:
            allocation[row.asset_class] = row.percentage
        
        # Fallback to Conservative if no data found
        if not allocation:
            allocation_rows = AssetAllocation.query.filter_by(risk_profile='Conservative').all()
            for row in allocation_rows:
                allocation[row.asset_class] = row.percentage
        
        return allocation
    
    def calculate_portfolio_amounts(self):
        """Calculate actual investment amounts for each asset class"""
        allocation = self.get_asset_allocation()
        investment_amount = self.investment_amount
        
        portfolio_amounts = {}
        for asset_class, percentage in allocation.items():
            portfolio_amounts[asset_class] = (investment_amount * percentage) / 100
        
        return portfolio_amounts

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    funds = db.relationship('Fund', backref='portfolio', lazy=True)

class Fund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    fund_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expected_return = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/investors', methods=['GET'])
def get_investors():
    try:
        investors = Investor.query.all()
        investor_list = []
        for investor in investors:
            risk_category, risk_category_code = investor.determine_risk_category()
            investor_list.append({
                'id': investor.id,
                'name': investor.name,
                'email': investor.email,
                'age': investor.age,
                'risk_tolerance': investor.risk_tolerance,
                'risk_category': risk_category,
                'risk_category_code': risk_category_code
            })
        return jsonify(investor_list)
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve investors: {str(e)}'}), 500

@app.route('/api/investors', methods=['POST'])
def create_investor():
    try:
        data = request.get_json()
        
        # Check if investor with this email already exists
        existing_investor = Investor.query.filter_by(email=data['email']).first()
        if existing_investor:
            return jsonify({'error': 'An investor with this email already exists'}), 400
        
        new_investor = Investor(
            name=data['name'],
            email=data['email'],
            age=data['age'],
            
            # Enhanced Demographics
            education_level=data['education_level'],
            occupation_type=data['occupation_type'],
            annual_income_range=data['annual_income_range'],
            
            # Financial Information
            monthly_income=data['monthly_income'],
            monthly_expenses=data['monthly_expenses'],
            existing_assets=data['existing_assets'],
            existing_liabilities=data['existing_liabilities'],
            emergency_fund=data['emergency_fund'],
            
            # Investment Details
            investment_amount=data['investment_amount'],
            investment_horizon=data['investment_horizon'],
            required_return=data['required_return'],
            equity_experience=data['equity_experience'],
            
            # Goals and Risk Assessment
            financial_goals=data['financial_goals'],
            
            # Risk Assessment Questionnaire Responses
            risk_q1=data['risk_q1'],
            risk_q1_reason=data.get('risk_q1_reason', ''),
            risk_q2=data['risk_q2'],
            risk_q3=data['risk_q3'],
            risk_q4=data['risk_q4'],
            risk_q5=data['risk_q5'],
            risk_q6=data['risk_q6'],
            risk_q7=data['risk_q7'],
            risk_q8=data['risk_q8'],
            risk_q8_reason=data.get('risk_q8_reason', ''),
            risk_q9=data['risk_q9'],
            risk_q10=data['risk_q10'],
            risk_q11=data['risk_q11'],
            risk_q12=data['risk_q12'],
            
            # Additional Profile Questions
            profile_q1=data['profile_q1'],
            profile_q2=data['profile_q2'],
            profile_q3=data['profile_q3'],
            profile_q4=data['profile_q4'],
            profile_q5=data['profile_q5'],
            profile_q6=data['profile_q6'],
            profile_q7=data['profile_q7'],
            
            # Calculated fields (will be updated below)
            risk_score=0,
            risk_tolerance='Conservative'
        )
        
        # Calculate risk profile
        new_investor.risk_score = new_investor.calculate_risk_score()
        new_investor.profile_score = new_investor.calculate_profile_score()
        new_investor.combined_score = new_investor.calculate_combined_score()
        new_investor.risk_tolerance = new_investor.determine_risk_tolerance()
        
        db.session.add(new_investor)
        db.session.commit()
        return jsonify({'message': 'Investor created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create investor: {str(e)}'}), 500

@app.route('/api/portfolio/<int:investor_id>', methods=['POST'])
def create_portfolio(investor_id):
    investor = Investor.query.get_or_404(investor_id)
    data = request.get_json()

    recommendations = data.get('recommendations')
    if not recommendations:
        return jsonify({'error': 'No recommendations provided'}), 400

    # Create a new portfolio
    portfolio_name = f"{investor.name}'s Recommended Portfolio - {datetime.utcnow().strftime('%Y-%m-%d')}"
    new_portfolio = Portfolio(investor_id=investor.id, name=portfolio_name)
    db.session.add(new_portfolio)
    db.session.flush()  # Use flush to assign an ID to new_portfolio before commit

    # Add funds to the portfolio
    for rec in recommendations:
        new_fund = Fund(
            portfolio_id=new_portfolio.id,
            fund_name=rec['fund_name'],
            amount=rec['recommended_investment'],
            expected_return=rec['expected_return']
        )
        db.session.add(new_fund)

    db.session.commit()
    
    return jsonify({'message': 'Portfolio created successfully', 'portfolio_id': new_portfolio.id}), 201

@app.route('/api/portfolio/<int:investor_id>', methods=['GET'])
def get_portfolio(investor_id):
    # Find the most recent portfolio for the investor
    portfolio = Portfolio.query.filter_by(investor_id=investor_id).order_by(Portfolio.created_at.desc()).first()

    if not portfolio:
        return jsonify({'error': 'No portfolio found for this investor.'}), 404

    # Get the investor's name
    investor = Investor.query.get_or_404(investor_id)

    # Get the funds associated with this portfolio
    funds = Fund.query.filter_by(portfolio_id=portfolio.id).all()

    portfolio_data = {
        'investor_name': investor.name,
        'portfolio_id': portfolio.id,
        'portfolio_name': portfolio.name,
        'created_at': portfolio.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'funds': [
            {
                'fund_name': fund.fund_name,
                'amount': fund.amount,
                'expected_return': fund.expected_return,
                # Attempt to get asset_class from FundMaster
                'asset_class': FundMaster.query.filter_by(fund_name=fund.fund_name).first().asset_class or 'N/A'
            } for fund in funds
        ]
    }

    return jsonify(portfolio_data), 201

@app.route('/api/recommendations/<int:investor_id>', methods=['GET'])
def get_recommendations(investor_id):
    investor = Investor.query.get_or_404(investor_id)
    
    # Calculate financial health metrics
    net_worth = investor.existing_assets - investor.existing_liabilities
    monthly_surplus = investor.monthly_income - investor.monthly_expenses
    debt_to_income_ratio = (investor.existing_liabilities / investor.monthly_income) if investor.monthly_income > 0 else 0
    
    # Get asset allocation based on risk profile
    asset_allocation = investor.get_asset_allocation()
    portfolio_amounts = investor.calculate_portfolio_amounts()
    
    # Generate recommendations for each asset class
    recommendations = []
    portfolio_amounts = investor.calculate_portfolio_amounts()

    for asset_class, amount in portfolio_amounts.items():
        if amount > 0:
            # Query available funds from database for this asset class
            available_funds = FundMaster.query.filter_by(asset_class=asset_class).all()
            if not available_funds:
                continue

            # Find funds the investor can afford with the allocated amount
            affordable_funds = [f for f in available_funds if f.min_investment <= amount]

            best_fund = None
            if affordable_funds:
                # From affordable funds, pick the one with the highest return
                best_fund = max(affordable_funds, key=lambda x: x.expected_return)
            elif available_funds:
                # If none are affordable, recommend the one with the lowest min investment as a fallback
                best_fund = min(available_funds, key=lambda x: x.min_investment)

            if best_fund:
                recommendations.append({
                    'asset_class': asset_class.replace('_', ' ').title(),
                    'fund_name': best_fund.fund_name,
                    'recommended_investment': round(amount, 2),
                    'expected_return': best_fund.expected_return
                })

    # Generate financial health assessment
    financial_health = "Good"
    health_warnings = []
    
    if debt_to_income_ratio > 0.4:
        financial_health = "Needs Attention"
        health_warnings.append("High debt-to-income ratio. Consider reducing debt before investing.")
    
    if investor.emergency_fund < (investor.monthly_expenses * 6):
        financial_health = "Needs Attention"
        health_warnings.append("Insufficient emergency fund. Maintain 6 months of expenses as emergency fund.")
    
    if monthly_surplus < 0:
        financial_health = "Poor"
        health_warnings.append("Monthly expenses exceed income. Focus on budgeting before investing.")
    
    return jsonify({
        'investor_profile': {
            'name': investor.name,
            'age': investor.age,
            'education_level': investor.education_level,
            'occupation_type': investor.occupation_type,
            'annual_income_range': investor.annual_income_range,
            'equity_experience': investor.equity_experience,
            'investment_horizon': investor.investment_horizon,
            'financial_goals': investor.financial_goals
        },
        'risk_assessment': {
            'risk_score': investor.risk_score,
            'demographic_score': investor.calculate_demographic_score(),
            'combined_score': investor.risk_score + investor.calculate_demographic_score(),
            'risk_category': investor.determine_risk_category()[0],
            'risk_category_code': investor.determine_risk_category()[1],
            'risk_tolerance': investor.risk_tolerance
        },
        'asset_allocation': {
            'strategy': asset_allocation,
            'amounts': {k: round(v, 2) for k, v in portfolio_amounts.items()},
            'total_investment': investor.investment_amount
        },
        'financial_analysis': {
            'monthly_income': investor.monthly_income,
            'monthly_expenses': investor.monthly_expenses,
            'monthly_surplus': monthly_surplus,
            'net_worth': net_worth,
            'debt_to_income_ratio': round(debt_to_income_ratio * 100, 2),
            'emergency_fund': investor.emergency_fund,
            'financial_health': financial_health,
            'health_warnings': health_warnings
        },
        'recommendations': recommendations
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
