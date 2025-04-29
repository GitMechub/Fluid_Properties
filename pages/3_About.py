import streamlit as st

for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os

path = os.path.dirname(__file__)
my_file = path + '/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='About - Fluid Properties',
    layout="wide",
    page_icon=img
)

st.sidebar.image(img)
st.sidebar.markdown(
    "[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@Mechub?sub_confirmation=1) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GitMechub)")

hide_menu = '''
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        '''
st.markdown(hide_menu, unsafe_allow_html=True)

st.header("Fluid Properties v1.0.1", divider="gray", anchor=False)

st.markdown('''
## About Fluid Properties:

The Fluid Properties app uses **CoolProp** to calculate thermodynamic and psychrometric properties of various fluids.
It allows users to input parameters like temperature, pressure, and quality to calculate key thermodynamic values.

## How it Works:

1. **Select the Fluid**: Choose the fluid you want to analyze (e.g., R134a, Water, Air, etc.).
2. **Input Parameters**: Enter key values such as temperature, pressure, or quality.
3. **Calculation**: The app calculates various properties like enthalpy, entropy, and specific volume based on the input parameters.
4. **Results**: View the calculated properties, displayed in an easy-to-read format.

## Psychrometric Calculation:

This app also allows psychrometric calculations for air properties. You can input parameters such as:
- **Dry Bulb Temperature** (°C)
- **Relative Humidity** (%) 

The app will compute important psychrometric properties such as:
- **Wet Bulb Temperature** (°C)
- **Dew Point Temperature** (°C)
- **Specific Humidity** (kg of water vapor per kg of dry air)
- **Enthalpy** (kJ/kg of dry air)

''')

