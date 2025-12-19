import streamlit as st
import joblib
import pandas as pd
import plotly.express as px

@st.cache_resource
def load_models():
    try:
        modelA = joblib.load('model_A.pkl')
        modelB = joblib.load('model_B.pkl')
        return modelA, modelB
    except FileNotFoundError:
        return None, None


def render_sidebar():
    st.sidebar.header('Simulator Controls')

#     Section 1
    st.sidebar.subheader('Date and Time')
    date_val = st.sidebar.date_input("Select Date", value=pd.to_datetime('today').date())
    hour_val = st.sidebar.slider("Select Hour", 0, 23, 17)

#     Section 2
    st.sidebar.subheader('Weather')
    wind_speed_val = st.sidebar.slider("Wind Speed (km/h)", 0, 50, 15)
    temperature_val = st.sidebar.slider("Temperature (C)", -30, 40, 20)

#     Section 3
    st.sidebar.subheader('Infrastructure')

    add_nuc = st.sidebar.slider('Add Nuclear Capacity (MW)', 0, 5000, value=0)
    st.sidebar.markdown("On average, one reactor generates 500 MW,  "
                        "plants can have multiple reactors.")

    return {
        "date": date_val,
        "hour": hour_val,
        "wind_speed": wind_speed_val,
        "temperature": temperature_val,
        "add_nuclear": add_nuc
    }


def run_predictions(model_a, model_b, inputs):
    dt = pd.to_datetime(inputs['date'])
    day_of_year = dt.dayofyear
    weekday = dt.weekday()
    is_weekend = 1 if weekday >= 5 else 0

    X_demand = pd.DataFrame({
        'Temperature_C': [inputs['temperature']],
        'Month': [dt.month],
        'Hour': [inputs['hour']],
        'Is_Weekend': [is_weekend],
        'Weekday': [weekday],
        'Year': [dt.year],
        'DayOfYear': [day_of_year],
    })

    predicted_demand = model_a.predict(X_demand)[0]

    X_mix = pd.DataFrame({
        'Wind_Speed_kmh': [inputs['wind_speed']],
        'Total_Demand': [predicted_demand],
    })


    predicted_mix = model_b.predict(X_mix)[0]

    fuel_names = ['NUCLEAR', 'HYDRO', 'WIND', 'SOLAR', 'GAS', 'BIOFUEL']
    supply_dict = dict(zip(fuel_names, predicted_mix))

    supply_dict['NUCLEAR'] += inputs['add_nuclear']

    current_generation = sum(supply_dict.values())
    excess_power = current_generation - predicted_demand

    if excess_power > 0:
        supply_dict['GAS'] = max(0, supply_dict['GAS'] - excess_power)

    for fuel in supply_dict:
        supply_dict[fuel] = int(round(supply_dict[fuel]))

    return predicted_demand, supply_dict



def render_dashboard(demand, supply_mix, inputs):
    st.title("⚡ Ontario Energy Grid Simulator")

    date_str = inputs['date'].strftime("%B %d, %Y")
    st.markdown(f"**Scenario:** {date_str} at {inputs['hour']}:00 | **Temp:** {inputs['temperature']}°C | **Wind:** {inputs['wind_speed']} km/h")

    # Calculating key metrics
    clean_power = supply_mix['NUCLEAR'] + supply_mix['HYDRO'] + supply_mix['WIND'] + supply_mix['SOLAR']

    if demand > 0:
        green_percent = clean_power / demand * 100
    else:
        green_percent = 0

    gas_mw = supply_mix['GAS']

    co2_tonnes = gas_mw * 0.4
    cars_equivalent = co2_tonnes * 2000


    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Demand", f"{demand:.0f} MW", delta="Grid Load")
    col2.metric("Carbon Free Score", f"{green_percent:.1f}%", delta="Target: 100%")
    col3.metric("Gas Generation", f"{gas_mw:,.0f} MW", delta="-Goal: 0 MW", delta_color="inverse")
    col4.metric("CO2 Emissions", f"{co2_tonnes:,.0f} Tonnes", f"~{cars_equivalent:,.0f} - Hours of Cars Driving", delta_color="inverse")

    st.divider()

    #Plotting graphs and data

    c1, c2 = st.columns([2, 1])

    chart_data = pd.DataFrame({
        'Source': list(supply_mix.keys()),
        'MW': list(supply_mix.values())
    })

    color_map = {
        'NUCLEAR': '#2ca02c',  # Green
        'GAS': '#d62728',  # Red
        'HYDRO': '#1f77b4',  # Blue
        'WIND': '#17becf',  # Cyan
        'SOLAR': '#ff7f0e',  # Orange
        'BIOFUEL': '#8c564b'  # Brown
    }


    with c1:
        st.subheader("Power Generation Mix")

        fig_bar = px.bar(
            chart_data, x='Source', y='MW', color='Source',
            color_discrete_map=color_map,
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Energy Production Breakdown")

        fig_donut = px.pie(
            chart_data, values='MW', names='Source', hole=0.4,
            color='Source', color_discrete_map=color_map,
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    if demand > 30000:
        st.error(f"SYSTEM OVERLOAD! Demand ({demand:,.0f} MW) exceeds grid capacity of 30,000 MW!")
    elif gas_mw == 0:
        st.success("PURE CLEAN ENERGY ACHIEVED! The grid is running on 0% Carbon.")
    else:
        st.info("Grid Status: Stable. Gas is active to meet peak demand.")



def main():
    st.set_page_config(page_title="Ontario Energy Simulator", page_icon=":lightning:", layout="wide")

    model_a, model_b = load_models()
    if model_a is None or model_b is None:
        st.error("Models not found. Please run data_pipeline.py first.")
        st.stop()

    inputs = render_sidebar()

    demand, supply_mix = run_predictions(model_a, model_b, inputs)

    render_dashboard(demand, supply_mix, inputs)

if __name__ == "__main__":
    main()