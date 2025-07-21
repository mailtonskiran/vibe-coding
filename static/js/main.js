document.addEventListener('DOMContentLoaded', function() {
    const investorForm = document.getElementById('investorForm');
    const investorsListDiv = document.getElementById('investorsList');

    let currentInvestorId = null;
    let currentRecommendations = [];

    // --- UTILITY FUNCTIONS ---
    function formatNumber(num) {
        return num.toLocaleString('en-IN');
    }

    // --- RENDER FUNCTIONS ---
    function renderContent(investorCard, html) {
        const contentDiv = investorCard.querySelector('.investor-content');
        contentDiv.innerHTML = html;
        contentDiv.style.display = 'block';
    }

    function renderMessage(investorCard, text, type) {
        const messageDiv = investorCard.querySelector('.message-area');
        messageDiv.textContent = text;
        messageDiv.className = `message-area ${type}`;
    }

    function hideAllContentViews() {
        document.querySelectorAll('.investor-content').forEach(div => {
            div.style.display = 'none';
            div.innerHTML = '';
        });
        document.querySelectorAll('.message-area').forEach(div => {
            div.textContent = '';
            div.className = 'message-area';
        });
    }

    // --- LOAD INVESTORS ---
    function loadInvestors() {
        fetch('/api/investors')
            .then(response => response.json())
            .then(data => {
                investorsListDiv.innerHTML = '';
                data.forEach(investor => {
                    const investorCard = document.createElement('div');
                    investorCard.className = 'investor-card';
                    investorCard.setAttribute('data-investor-id', investor.id);
                    investorCard.innerHTML = `
                        <div class="investor-header">
                            <strong>${investor.name}</strong>
                        </div>
                        <div class="investor-details">
                            <p><strong>Email:</strong> ${investor.email}</p>
                            <p><strong>Risk Tolerance:</strong> ${investor.risk_tolerance}</p>
                            <p><strong>Risk Category:</strong> ${investor.risk_category} (${investor.risk_category_code})</p>
                        </div>
                        <div class="investor-actions">
                            <button class="save-portfolio-btn" data-investor-id="${investor.id}" disabled>Save Portfolio</button>
                            <button class="recommendation-btn" data-investor-id="${investor.id}">Get Recommendations</button>
                            <button class="view-portfolio-btn" data-investor-id="${investor.id}">View Portfolio</button>
                        </div>
                        <div class="message-area"></div>
                        <div class="investor-content" style="display:none;"></div>
                    `;
                    investorsListDiv.appendChild(investorCard);
                });
            })
            .catch(error => {
                console.error('Error loading investors:', error);
                investorsListDiv.innerHTML = '<p class="error">Could not load investors.</p>';
            });
    }

    // --- REGISTER INVESTOR ---
    function registerInvestor(e) {
        e.preventDefault();
        const formData = new FormData(investorForm);
        const data = Object.fromEntries(formData.entries());

        fetch('/api/investors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Validation failed'); });
            }
            return response.json();
        })
        .then(result => {
            alert(result.message);
            investorForm.reset();
            loadInvestors();
        })
        .catch(error => {
            console.error('Registration Error:', error);
            alert(`Error: ${error.message}`);
        });
    }

    // --- GET RECOMMENDATIONS ---
    function getRecommendations(investorId, investorCard) {
        currentInvestorId = investorId;
        hideAllContentViews();
        renderContent(investorCard, '<p>Loading recommendations...</p>');

        fetch(`/api/recommendations/${investorId}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Server error'); });
                }
                return response.json();
            })
            .then(data => {
                currentRecommendations = data.recommendations;
                let htmlContent = `<h4>Comprehensive Analysis for ${data.investor_profile.name}</h4>`;

                // --- Risk Profile Table ---
                htmlContent += `<h5>Risk Profile</h5>
                <table class="recommendation-table">
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Risk Score</td><td>${data.risk_assessment.risk_score}</td></tr>
                    <tr><td>Demographic Score</td><td>${data.risk_assessment.demographic_score}</td></tr>
                    <tr><td>Risk Category</td><td>${data.risk_assessment.risk_category} (${data.risk_assessment.risk_category_code})</td></tr>
                    <tr><td><strong>Final Risk Tolerance</strong></td><td><strong>${data.risk_assessment.risk_tolerance}</strong></td></tr>
                </table>`;

                // --- Asset Allocation Table ---
                htmlContent += `<h5>Recommended Asset Allocation (Total Investment: ₹${formatNumber(data.asset_allocation.total_investment)})</h5>
                <table class="recommendation-table">
                    <tr><th>Asset Class</th><th>Allocation (%)</th><th>Amount (₹)</th></tr>`;
                for (const [assetClass, percent] of Object.entries(data.asset_allocation.strategy)) {
                    const amount = data.asset_allocation.amounts[assetClass] || 0;
                    const formattedAssetClass = assetClass.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    htmlContent += `<tr><td>${formattedAssetClass}</td><td>${percent}%</td><td>₹${formatNumber(amount)}</td></tr>`;
                }
                htmlContent += `</table>`;

                // --- Fund Recommendations Table ---
                htmlContent += `<h5>Fund Recommendations</h5>`;
                if (data.recommendations && data.recommendations.length > 0) {
                    htmlContent += `<table class="recommendation-table"><tr><th>Asset Class</th><th>Fund Name</th><th>Amount (₹)</th><th>Return (%)</th></tr>`;
                    let total = 0;
                    data.recommendations.forEach(r => {
                        total += r.recommended_investment;
                        const formattedAssetClass = r.asset_class.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        htmlContent += `<tr><td>${formattedAssetClass}</td><td>${r.fund_name}</td><td>₹${formatNumber(r.recommended_investment)}</td><td>${r.expected_return}</td></tr>`;
                    });
                    htmlContent += `<tr><td colspan="2" style="text-align:right;font-weight:bold;">Total Recommended Investment:</td><td style="font-weight:bold;">₹${formatNumber(total)}</td><td></td></tr></table>`;
    
                } else {
                    htmlContent += '<p>No suitable funds found for this profile.</p>';
                }
                
                renderContent(investorCard, htmlContent);
                investorCard.querySelector(`.save-portfolio-btn`).disabled = false;
            })
            .catch(error => {
                console.error('Error getting recommendations:', error);
                renderContent(investorCard, `<p class="error">Error: ${error.message}</p>`);
            });
    }

    // --- VIEW PORTFOLIO ---
    function getPortfolio(investorId, investorCard) {
        currentInvestorId = investorId;
        currentRecommendations = []; // Clear old recommendations
        hideAllContentViews();
        renderContent(investorCard, '<p>Loading portfolio...</p>');

        fetch(`/api/portfolio/${investorId}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Could not load portfolio.'); });
                }
                return response.json();
            })
            .then(data => {
                let htmlContent = `<h4>Portfolio for ${data.investor_name}</h4>
                <p><strong>Portfolio Name:</strong> ${data.portfolio_name}<br>
                <strong>Created On:</strong> ${data.created_at}</p>`;

                htmlContent += `<h5>Saved Funds</h5>
                <table class="recommendation-table">
                    <tr><th>Asset Class</th><th>Fund Name</th><th>Amount (₹)</th><th>Expected Return (%)</th></tr>`;
                
                let totalAmount = 0;
                data.funds.forEach(fund => {
                    totalAmount += fund.amount;
                    const formattedAssetClass = fund.asset_class.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    htmlContent += `<tr>
                        <td>${formattedAssetClass}</td>
                        <td>${fund.fund_name}</td>
                        <td>₹${formatNumber(fund.amount)}</td>
                        <td>${fund.expected_return}</td>
                    </tr>`;
                });

                htmlContent += `<tr>
                    <td colspan="2" style="text-align:right;font-weight:bold;">Total Portfolio Value:</td>
                    <td style="font-weight:bold;">₹${formatNumber(totalAmount)}</td>
                    <td></td>
                </tr>`;
                htmlContent += `</table>`;
                renderContent(investorCard, htmlContent);
            })
            .catch(error => {
                console.error('Error getting portfolio:', error);
                renderContent(investorCard, `<p class="error">Error: ${error.message}</p>`);
            });
    }

    // --- SAVE PORTFOLIO ---
    async function savePortfolio(investorId, investorCard) {
        if (investorId !== currentInvestorId || !currentRecommendations || currentRecommendations.length === 0) {
            renderMessage(investorCard, 'Please get the latest recommendations before saving.', 'error');
            return;
        }

        renderMessage(investorCard, 'Checking existing portfolio...', 'info');

        try {
            const response = await fetch(`/api/portfolio/${investorId}`);
            
            let savedFunds = [];
            if (response.ok) {
                const savedPortfolio = await response.json();
                savedFunds = savedPortfolio.funds.map(f => ({ fund_name: f.fund_name, amount: f.amount })).sort((a, b) => a.fund_name.localeCompare(b.fund_name));
            } else if (response.status !== 404) {
                throw new Error('Could not check existing portfolio.');
            }

            const newFunds = currentRecommendations.map(r => ({ fund_name: r.fund_name, amount: r.recommended_investment })).sort((a, b) => a.fund_name.localeCompare(b.fund_name));

            if (JSON.stringify(savedFunds) === JSON.stringify(newFunds)) {
                renderMessage(investorCard, 'No changes detected. Portfolio is already up-to-date.', 'success');
                return;
            }

            renderMessage(investorCard, 'Saving new portfolio...', 'info');
            const portfolioData = {
                name: `Portfolio for ${currentInvestorId} - ${new Date().toISOString().split('T')[0]}`,
                funds: currentRecommendations.map(rec => ({
                    fund_name: rec.fund_name,
                    amount: rec.recommended_investment,
                    expected_return: rec.expected_return
                }))
            };

            const saveResponse = await fetch(`/api/portfolio/${investorId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(portfolioData)
            });

            if (!saveResponse.ok) {
                const errorData = await saveResponse.json();
                throw new Error(errorData.error || 'Failed to save portfolio.');
            }

            const result = await saveResponse.json();
            renderMessage(investorCard, `Portfolio saved successfully! Portfolio ID: ${result.portfolio_id}`, 'success');
            investorCard.querySelector('.save-portfolio-btn').disabled = true;

        } catch (error) {
            console.error('Error saving portfolio:', error);
            renderMessage(investorCard, `Error: ${error.message}`, 'error');
        }
    }

    // --- INITIALIZATION & EVENT LISTENERS ---
    loadInvestors();
    investorForm.addEventListener('submit', registerInvestor);

    investorsListDiv.addEventListener('click', e => {
        const target = e.target;
        const investorCard = target.closest('.investor-card');
        if (!investorCard) return;

        const investorId = investorCard.dataset.investorId;

        if (target.classList.contains('recommendation-btn')) {
            getRecommendations(investorId, investorCard);
        } else if (target.classList.contains('view-portfolio-btn')) {
            getPortfolio(investorId, investorCard);
        } else if (target.classList.contains('save-portfolio-btn')) {
            savePortfolio(investorId, investorCard);
        }
    });
});
