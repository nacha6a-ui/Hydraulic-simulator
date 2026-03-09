import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Page Config & UI Setup ---
st.set_page_config(layout="wide", page_title="Hydraulic System Simulator")
st.title("💧 Building Water Supply Simulation")
st.markdown("""
Welcome to the Hydraulic Sandbox! 
Experiment with the booster pump to see how it overcomes low overhead clearance (Boyle's Law & Bernoulli's Principle). 
**New:** Toggle the roof tank's air vent to see the "Juice Box Effect." If the tank is sealed, draining water creates a vacuum that fights gravity!
""")

# --- 2. System Specifications & Constants ---
rho = 1000  # Density of water (kg/m^3)
g = 9.81    # Gravity (m/s^2)
floor_height = 3.0  # Height per floor in meters
num_floors = 5
tank_clearance = 2.0  # Tank height above the top floor in meters
tank_elevation = (num_floors * floor_height) + tank_clearance

# Define elevations for Ground (0) through Floor 5
floors = np.arange(num_floors + 1)
elevations = floors * floor_height
delta_h = tank_elevation - elevations

# Vacuum Physics Constants
P_atm = 101.3  # Atmospheric pressure in kPa
V_air_initial = 500.0  # Initial headspace air volume in Liters

# Pressure tank parameters for the booster
V_tank_total = 100.0  # Liters
P_precharge = 150.0   # kPa

# --- 3. Interactive Control Panel ---
st.markdown("---")
st.markdown("### 🎛️ System Controls")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🚀 Booster Pump (Enhanced System)")
    P_boost = st.slider(
        'Booster Pressure (kPa)', 
        min_value=0.0, max_value=400.0, value=0.0, step=10.0,
        help="Simulates the pump pushing water into the pressure tank."
    )

with col2:
    st.markdown("#### 🌬️ Tank Venting (Gravity System)")
    vent_status = st.radio(
        "Roof Tank Air Vent:", 
        ["Vented (Open to Atmosphere)", "Sealed (Closed)"]
    )
    water_drained = st.slider(
        "Water Drained from Tank (Liters)", 
        min_value=0.0, max_value=1000.0, value=0.0, step=50.0,
        help="As water drains, a sealed tank creates a vacuum."
    )

# --- 4. Physics Calculations ---

# A. Vacuum Effect (Boyle's Law applied to the roof tank)
if vent_status == "Sealed (Closed)":
    # Air volume expands as water leaves, dropping the pressure below atmospheric
    V_air_new = V_air_initial + water_drained
    P_air_abs = P_atm * (V_air_initial / V_air_new)
    P_vacuum = P_air_abs - P_atm  # This results in a negative gauge pressure
else:
    P_vacuum = 0.0  # Vented tank maintains atmospheric pressure (0 gauge pressure)

# B. Gravity System (Baseline + Vacuum)
# Gravity pressure is rho*g*h PLUS the negative vacuum pressure
P_gravity = (rho * g * delta_h / 1000) + P_vacuum

# If vacuum is stronger than gravity, flow stops entirely (pressure can't be negative for flow)
P_gravity = np.maximum(P_gravity, 0)
v_gravity = np.sqrt(2 * (P_gravity * 1000) / rho)

# C. Enhanced System Calculations (Pump + Vacuum)
current_tank_pressure = max(P_precharge, P_precharge + P_boost)
V_air_booster = (P_precharge * V_tank_total) / current_tank_pressure

P_enhanced = P_gravity + P_boost
P_enhanced = np.maximum(P_enhanced, 0)
v_enhanced = np.sqrt(2 * (P_enhanced * 1000) / rho)

# --- 5. Alerts for Students ---
if vent_status == "Sealed (Closed)" and water_drained > 0:
    if np.all(P_gravity == 0):
        st.error(f"🚨 **Vapor Lock!** The vacuum ({P_vacuum:.1f} kPa) has completely overpowered gravity. Water flow has stopped!")
    else:
        st.warning(f"⚠️ **Vacuum Forming:** A negative pressure of {P_vacuum:.1f} kPa is fighting the gravity flow.")

# --- 6. Visualization Engine ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

# Plot A: Static Gravity System
bars1 = ax1.barh(floors, P_gravity, color='#3498db', edgecolor='black', alpha=0.8)
ax1.set_yticks(floors)
ax1.set_yticklabels([f'Floor {i}\n(h={h}m)' for i, h in zip(floors, elevations)])
ax1.set_xlabel('Hydrostatic Pressure (kPa)', fontsize=11)
ax1.set_title(f'A. Gravity System\nVacuum: {P_vacuum:.1f} kPa', fontsize=14, fontweight='bold')
ax1.set_xlim(0, 700)
ax1.grid(axis='x', linestyle='--', alpha=0.5)

for bar, v, p in zip(bars1, v_gravity, P_gravity):
    if p > 0:
        ax1.text(p + 15, bar.get_y() + bar.get_height()/2, 
                 f"{p:.1f} kPa\n{v:.1f} m/s", va='center', fontsize=9)
    else:
        ax1.text(15, bar.get_y() + bar.get_height()/2, 
                 "0.0 kPa\n0.0 m/s", va='center', fontsize=9, color='red', fontweight='bold')

# Plot B: Dynamic Enhanced System
bars2 = ax2.barh(floors, P_enhanced, color='#2ecc71', edgecolor='black', alpha=0.8)
ax2.set_yticks(floors)
ax2.set_yticklabels([f'Floor {i}\n(h={h}m)' for i, h in zip(floors, elevations)])
ax2.set_xlabel('Total System Pressure (kPa)', fontsize=11)

ax2.set_title(f'B. Enhanced System (Booster + Tank)\nAir Vol: {V_air_booster:.1f} L | Boost: {P_boost:.1f} kPa', 
              fontsize=14, fontweight='bold')
ax2.set_xlim(0, 700)
ax2.grid(axis='x', linestyle='--', alpha=0.5)

for bar, v, p in zip(bars2, v_enhanced, P_enhanced):
    if p > 0:
        ax2.text(p + 15, bar.get_y() + bar.get_height()/2, 
                 f"{p:.1f} kPa\n{v:.1f} m/s", va='center', fontsize=9, color='darkgreen', fontweight='bold')
    else:
        ax2.text(15, bar.get_y() + bar.get_height()/2, 
                 "0.0 kPa\n0.0 m/s", va='center', fontsize=9, color='red', fontweight='bold')

fig.tight_layout()
st.pyplot(fig)