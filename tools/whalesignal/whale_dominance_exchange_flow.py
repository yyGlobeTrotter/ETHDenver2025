import requests
import numpy as np

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/global"
WHALE_ALERT_API_KEY = "O78CBmluLQUT9ZZ59i3Pi5F1mxjgYV4B"
DEFILLAMA_API = "https://stablecoins.llama.fi/stablecoin"

def get_current_market_dominance(token="btc"): 
    response = requests.get(f"{COINGECKO_API_URL}")
    # Note: Debug code below:
    #print(f"DEBUG: CoinGecko BTC Dominance Response Code: {response.status_code}")
    #print(f"DEBUG: CoinGecko BTC Dominance Response: {response.json()}")

    if response.status_code == 200:
        '''
        try:
            data = response.json()
            if not isinstance(data, list):
                return None, None, "Error: CoinGecko API returned invalid format."
        except Exception as e:
            return None, None, "Error: Failed to parse CoinGecko API response."
        '''
        data = response.json()
        
        if 'data' in data and 'market_cap_percentage' in data['data']:
            print(f"DEBUG: Market Dominance Data: {data['data']['market_cap_percentage']}")

            market_dominance = data['data']['market_cap_percentage'].get(token, None)
            market_cap_change_24h = data['data'].get('market_cap_change_percentage_24h_usd', None)
            return market_dominance, market_cap_change_24h, None
    if not isinstance(data, dict):
        return None, None, "Error: CoinGecko API returned invalid format."
        
    return None, None, "Error: No market dom data received from CoinGecko API."

def get_whale_transactions(token, min_value=1000000, direction="all", days=1):
    params = {"api_key": WHALE_ALERT_API_KEY, "min_value": min_value, "currency": token}
    response = requests.get("https://api.whale-alert.io/v1/transactions", params=params)
    if response.status_code == 200:
        transactions = response.json().get("transactions", [])
        inflows = sum(1 for tx in transactions if tx.get("to") == "exchange")
        outflows = sum(1 for tx in transactions if tx.get("from") == "exchange")
        return (inflows, outflows, None) if inflows is not None and outflows is not None else (None, None, "Error: No valid whale transaction data received.")
    return None, None, "Error: No valid whale exchange flow data received from whale-alert.io."

def get_exchange_flows(token: str, days: int = 1):
    url = f"{DEFILLAMA_API}/chains"
    response = requests.get(url)
    '''
    print(f"DEBUG: Exchange Flows API URL: {url}")
    print(f"DEBUG: Response Code: {response.status_code}")
    print(f"DEBUG: Response Text: {response.text}")
    '''
    if response.status_code == 200:
        data = response.json()
        if not isinstance(data, dict):
            return None, None, "Error: DeFiLlama API returned invalid format."
        inflow = sum(d.get("inflow", 0) for d in data if "inflow" in d)
        outflow = sum(d.get("outflow", 0) for d in data if "outflow" in d)
        return (inflow, outflow, None) if inflow is not None and outflow is not None else (None, None, "Error: No valid exchange flow data received from DeFiLlama.")
    
    return None, None, "Error: No exchange flow data received from DeFiLlama API."

def get_historical_btc_dominance(days=30):
    response = requests.get(f"{COINGECKO_API_URL}/coins/bitcoin/market_chart?vs_currency=usd&days={days}")
    if response.status_code == 200:
        data = response.json().get("market_caps", [])
        if data:
            btc_dominance_values = [item[1] for item in data]
            return np.mean(btc_dominance_values), None
    return None, "Error: Unable to fetch historical BTC dominance from CoinGecko API."

def generate_risk_signals(token):
    signal_messages = []
    
    current_dom, market_cap_change_24h, dom_error = get_current_market_dominance(token)
    # Note: Debug code below:
    print(f"DEBUG: CoinGecko current dom value of {token}: {current_dom}")
    print(f"DEBUG: CoinGecko 24h market cap change for {token}: {market_cap_change_24h}")

    historical_dom, hist_dom_error = get_historical_btc_dominance(days=30)
    if dom_error:
        signal_messages.append(dom_error)
    if hist_dom_error:
        signal_messages.append(hist_dom_error)
        signal_messages.append(dom_error)
    
    inflows, outflows, inflow_error = get_exchange_flows(token, days=1)
    historical_inflows, historical_outflows, hist_inflow_error = get_exchange_flows(token, days=30)
    whale_inflows, whale_outflows, whale_error = get_whale_transactions(token, days=1)
    historical_whale_inflows, historical_whale_outflows, hist_whale_error = get_whale_transactions(token, days=30)
    
    if inflow_error:
        signal_messages.append(inflow_error)
    if hist_inflow_error:
        signal_messages.append(hist_inflow_error)
    if whale_error:
        signal_messages.append(whale_error)
    if hist_whale_error:
        signal_messages.append(hist_whale_error)
    
    risk_score = 0
    dom_z_score = 0
    
    if current_dom:
        if historical_dom is None:
            dom_z_score = 0
        if historical_dom is not None and current_dom is not None:
            dom_z_score = (current_dom - historical_dom) / (historical_dom if historical_dom != 0 else 1)
        if dom_z_score > 2:
            risk_score += 2
            signal_messages.append(f"🚨 BTC dominance is unusually high at {current_dom:.2f}%, compared to 30-day average of {historical_dom:.2f}%.")
        elif dom_z_score < -2:
            risk_score -= 2
            signal_messages.append(f"⚠️ BTC dominance is unusually low at {current_dom:.2f}%, compared to 30-day average of {historical_dom:.2f}%.")
            risk_score += 2
            signal_messages.append(f"BTC dominance is high at {current_dom:.2f}%, compared to the 30-day average.")
        elif current_dom < 40:
            risk_score -= 1
            signal_messages.append(f"BTC dominance is declining at {current_dom:.2f}%, compared to the 30-day average.")
    
    if inflows and outflows and historical_inflows and historical_outflows:
        inflow_z = (inflows - historical_inflows) / (historical_inflows if historical_inflows != 0 else 1)
        outflow_z = (outflows - historical_outflows) / (historical_outflows if historical_outflows != 0 else 1)
        if inflow_z > 2:
            risk_score += 2
            signal_messages.append(f"Exchange inflows in the last 24 hours: {inflows:.2f}, compared to 30-day average: {historical_inflows:.2f}. Increased selling pressure.")
        elif outflow_z > 2:
            risk_score -= 2
            signal_messages.append(f"Exchange outflows in the last 24 hours: {outflows:.2f}, compared to 30-day average: {historical_outflows:.2f}. Potential accumulation.")
    
    if whale_inflows and whale_outflows and historical_whale_inflows and historical_whale_outflows:
        whale_inflow_z = (whale_inflows - historical_whale_inflows) / (historical_whale_inflows if historical_whale_inflows != 0 else 1)
        whale_outflow_z = (whale_outflows - historical_whale_outflows) / (historical_whale_outflows if historical_whale_outflows != 0 else 1)
        if whale_inflow_z > 2:
            risk_score += 3
            signal_messages.append(f"Whale inflows in the last 24 hours: {whale_inflows:.2f}, compared to 30-day average: {historical_whale_inflows:.2f}. Bearish signal.")
        elif whale_outflow_z > 2:
            risk_score -= 3
            signal_messages.append(f"Whale outflows in the last 24 hours: {whale_outflows:.2f}, compared to 30-day average: {historical_whale_outflows:.2f}. Bullish signal.")
    
    signal_level = "🚨 HIGH RISK ALERT" if risk_score >= 5 else "⚠️ MODERATE RISK" if risk_score >= 2 else "🟢 LOW RISK"
    return {"risk_score": risk_score, "level": signal_level, "signals": signal_messages}

if __name__ == "__main__":
    token = "btc"
    risk_result = generate_risk_signals(token)
    print(f"Risk Score: {risk_result['risk_score']} - {risk_result['level']}")
    for msg in risk_result["signals"]:
        print(msg)
