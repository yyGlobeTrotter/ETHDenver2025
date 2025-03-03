import requests
import datetime
import numpy as np

TOKEN = "btc"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/global"
WHALE_ALERT_API_KEY = "O78CBmluLQUT9ZZ59i3Pi5F1mxjgYV4B"


def get_current_btc_dominance():
    response = requests.get(f"{COINGECKO_API_URL}/global")
    if response.status_code == 200:
        data = response.json()
        return data["data"]["market_cap_percentage"]["btc"]
    return None


def get_historical_btc_dominance(days=30):
    url = f"{COINGECKO_API_URL}/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["market_caps"]
        btc_dominance_values = [item[1] for item in data]
        return np.mean(btc_dominance_values)
    return None


def get_current_whale_transactions(min_value=1000000):
    params = {"api_key": WHALE_ALERT_API_KEY, "min_value": min_value, "currency": TOKEN}
    response = requests.get("https://api.whale-alert.io/v1/transactions", params=params)

    if response.status_code == 200:
        data = response.json()
        return len(data.get("transactions", []))
    return None


def get_historical_whale_transactions():
    daily_whale_counts = []

    for i in range(1, 31):
        date = (datetime.datetime.utcnow() - datetime.timedelta(days=i)).strftime(
            "%Y-%m-%d"
        )
        response = requests.get(
            f"https://api.whale-alert.io/v1/transactions?date={date}&api_key={WHALE_ALERT_API_KEY}"
        )

        if response.status_code == 200:
            data = response.json()
            daily_whale_counts.append(len(data.get("transactions", [])))

    return np.mean(daily_whale_counts) if daily_whale_counts else None


# === RISK SIGNAL GENERATION ===
def generate_risk_signals():
    current__dom = get_current_btc_dominance()
    historical__dom = get_historical_btc_dominance()

    current_whales = get_current_whale_transactions()
    historical_whales = get_historical_whale_transactions()

    risk_score = 0
    signal_messages = []

    #  Dominance Risk Calculation
    if current__dom and historical__dom:
        deviation = ((current__dom - historical__dom) / historical__dom) * 100
        if deviation > 5:  # FIXME: Temp use  Dom >5% over historical avg
            risk_score += 2
            signal_messages.append(
                f"🚨  Dominance is {deviation:.2f}% above historical average."
            )
        elif deviation < -5:  #  Dom significantly lower
            risk_score += 1
            signal_messages.append(
                f"⚠️  Dominance is {deviation:.2f}% below historical average."
            )

    # Whale Transaction Risk Calculation
    if current_whales and historical_whales:
        deviation = ((current_whales - historical_whales) / historical_whales) * 100
        if deviation > 50:  # Example threshold: Whale transfers 50% higher than average
            risk_score += 3
            signal_messages.append(
                f"🚨 Whale transactions are {deviation:.2f}% above historical average."
            )
        elif deviation < -50:  # Sudden drop in whale activity
            risk_score += 1
            signal_messages.append(
                f"⚠️ Whale transactions are {deviation:.2f}% below historical average."
            )

    # Risk Signal Categorization
    if risk_score >= 5:
        signal_level = "🚨 HIGH RISK ALERT"
    elif risk_score >= 3:
        signal_level = "⚠️ MODERATE RISK"
    else:
        signal_level = "🟢 LOW RISK"

    return {"risk_score": risk_score, "level": signal_level, "signals": signal_messages}


if __name__ == "__main__":
    risk_result = generate_risk_signals()

    print(f"Risk Score: {risk_result['risk_score']} - {risk_result['level']}")
    for msg in risk_result["signals"]:
        print(msg)
