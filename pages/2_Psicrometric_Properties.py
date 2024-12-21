import streamlit as st
st.session_state.update(st.session_state)
for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os
path = os.path.dirname(__file__)
my_file = path + '/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='Psicrometric Properties',
    layout="wide",
    page_icon=img
                   )

st.sidebar.image(img)
st.sidebar.markdown("[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@Mechub?sub_confirmation=1) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GitMechub)")

hide_menu = '''
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        '''
st.markdown(hide_menu, unsafe_allow_html=True)


from CoolProp import AbstractState
from CoolProp.CoolProp import PhaseSI, PropsSI, get_global_param_string
import CoolProp.CoolProp as CoolProp
from CoolProp.HumidAirProp import HAPropsSI
import CoolProp.Plots as CPP

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

################# SETUP #################

st.title("Psicrometric Properties", anchor=False)

col1, col2 = st.columns([1, 2])

col1.subheader("Setup", divider="gray", anchor=False)


import streamlit as st
import pandas as pd
import numpy as np
from CoolProp.CoolProp import PropsSI

# Configurações iniciais da sessão do Streamlit
if 'active_page' not in st.session_state:
    st.session_state.active_page = '2_Psicrometric_Properties'
    st.session_state.input_P_p = 101.325
    st.session_state.input_Tdb_p = 30.0
    st.session_state.input_Twb_p = 25.0
    st.session_state.input_Tdp_p = 23.2
    st.session_state.input_R_p = 0.67
    st.session_state.input_W_p = 18.
    st.session_state.input_H_p = 76280.77
    st.session_state.input_V_p = 0.88

# Define os valores padrão para os parâmetros psicrométricos
default_values = {
    "Pressure": 101.325,  # kPa
    "Dry Bulb Temperature": 30.0,  # °C
    "Wet Bulb Temperature": 25.0,  # °C
    "Dew Point Temperature": 23.2,  # °C
    "Relative Humidity": 0.67,  # %
    "Humidity Ratio": 18.,  # g/kg dry air
    "Enthalpy": 76280.77,  # J/kg
    "Specific Volume": 0.88  # m³/kg dry air
}

# Mapeamento para os parâmetros psicrométricos
coolprop_params = {
    "Pressure": "P",
    "Dry Bulb Temperature": "Tdb",
    "Wet Bulb Temperature": "Twb",
    "Dew Point Temperature": "Tdp",
    "Relative Humidity": "R",
    "Humidity Ratio": "W",
    "Enthalpy": "H",
    "Specific Volume": "V"
}

# Seleção de parâmetros de entrada
options = col1.multiselect(
    "Choose 3 input parameters",
    list(default_values.keys()),
    max_selections=3
)

# Inputs dinâmicos para os parâmetros selecionados
inputs = {}
for param in options:
    inputs[param] = col1.number_input(
        label=f"{param} ({'kPa' if param == 'Pressure' else '°C' if 'Temperature' in param else '%' if param == 'Relative Humidity' else 'g/kg' if param == 'Humidity Ratio' else 'J/kg' if param == 'Enthalpy' else 'm³/kg' if param == 'Specific Volume' else ''})",
        value=default_values[param],
        key=f'input_{coolprop_params[param]}_p',
        step=0.1 if param != "Pressure" else 1.0,
        min_value=0. if param in ['Pressure', 'Specific Volume','Humidity Ratio','Relative Humidity'] else None,
        max_value=1. if param in ['Relative Humidity'] else None
    )
    if inputs[param] != st.session_state.get(f'input_{coolprop_params[param]}_p', None):
        st.session_state[f'input_{coolprop_params[param]}_p'] = inputs[param]

################# FUNCTIONS #################

def Psicrometric_Properties(p_param_dict, input_list_p):

  try:

    if len(input_list_p) < 3:
            raise ValueError("Error: 'input_list' must contain at least 3 variables (e.g., pressure, temperature, relative humidity).")

    # List of parameters to calculate
    params = [
        'P',
        'Tdb',
        'Twb',
        'Tdp',
        'R',
        'W',
        'H',
        'V',
        'P_w',   # Partial pressure of water vapor in Pa
        'S',     # Mixture entropy per unit dry air in J/(kg dry air·K)
        'cp',    # Mixture specific heat per unit dry air in J/(kg dry air·K)
        'CV',    # Mixture specific heat at constant volume in J/(kg dry air·K)
        'Y',     # Water mole fraction in mol water/mol humid air
        'k',     # Mixture thermal conductivity in W/(m·K)
        'Visc'   # Mixture viscosity in Pa·s
    ]

    params = [param for param in params if param not in input_list_p]

    # Calculate each parameter in the list
    with col2:
        with st.expander("Error Log"):
            for param in params:
                try:
                    p_param_dict[param] = HAPropsSI(param, input_list_p[0], p_param_dict[input_list_p[0]],
                                                    input_list_p[1], p_param_dict[input_list_p[1]],
                                                    input_list_p[2], p_param_dict[input_list_p[2]])
                except Exception as e:

                    #print(f"[Erro] Não foi possível calcular o parâmetro '{param}'. Detalhes: {e}")
                    st.error(f"Unable to calculate {param}. Error: {e}")
                    p_param_dict[param] = np.nan
                    pass

    # Calculate partial pressure of dry air (Pa) explicitly
    if 'P' in p_param_dict and 'P_w' in p_param_dict:
        p_param_dict['Pa'] = p_param_dict['P'] - p_param_dict['P_w']
    else:
        print("Warning: Could not calculate 'Partial pressure of dry air' because 'Total Pressure' or 'Partial pressure of water vapor' is missing.")

    return p_param_dict

  except KeyError as e:
        raise KeyError(f"Error: The key {str(e)} is missing in the 'p_param_dict' dictionary. Ensure all required variables are defined.") from e

  except ValueError as e:
      raise ValueError(f"Value Error: {str(e)}. Check the values in 'p_param_dict' and 'input_list' for correctness.") from e

  except Exception as e:
      raise RuntimeError(f"An unexpected error occurred: {str(e)}. Please check the input data and try again.") from e


################# RUNNING #################

if len(options) == 3:
    run_button = col1.button("Run", use_container_width=True)

    param_dict = {}
    if run_button:

        input_list = []
        for param in inputs.keys():
            # Check if the parameter exists in CoolProp mapping and append the mapped key
            if param in coolprop_params:
                input_list.append(coolprop_params[param])
                if coolprop_params[param] == 'Tdb':
                    param_dict[coolprop_params[param]] = inputs[param] + 273.15
                elif coolprop_params[param] == 'Twb':
                    param_dict[coolprop_params[param]] = inputs[param] + 273.15
                elif coolprop_params[param] == 'Tdp':
                    param_dict[coolprop_params[param]] = inputs[param] + 273.15
                elif coolprop_params[param] == 'W':
                    param_dict[coolprop_params[param]] = inputs[param]/1e3
                elif coolprop_params[param] == 'P':
                    param_dict[coolprop_params[param]] = inputs[param]*1e3
                else:
                    param_dict[coolprop_params[param]] = inputs[param]

        try:

            p_param_dict_0 = Psicrometric_Properties(param_dict, input_list)

            # Adjusting the variables for displaying the DataFrame

            p_param_dict_1 = {
                'Pressure (kPa)': [p_param_dict_0['P'] / 1e3],
                'Dry-bulb Temperature (°C)': [round(p_param_dict_0['Tdb'] - 273.15, 2)],
                'Wet-bulb Temperature (°C)': [round(p_param_dict_0['Twb'] - 273.15, 2)],
                'Dew Point Temperature (°C)': [round(p_param_dict_0['Tdp'] - 273.15, 2)],
                'Relative Humidity (%)': [round(param_dict['R'] * 100, 2)],
                'Humidity Ratio (g/kg dry air)': [round(param_dict['W'] * 1e3, 2)],
                'Enthalpy (J/kg dry air)': [round(param_dict['H'], 2)],
                'Specific Volume (m³/kg dry air)': [round(param_dict['V'], 3)],
                'Partial Pressure Water Vapor (kPa)': [round(param_dict['P_w'] / 1e3, 3)],
                'Partial Pressure Dry Air (kPa)': [round(param_dict['Pa'] / 1e3, 3)],
                'Entropy (J/(kg.K))': [round(param_dict['S'], 2)],
                'Specific Heat (cp, J/(kg.K))': [round(param_dict['cp'], 2)],
                'Specific Heat at Constant Volume (CV, J/(kg.K))': [round(param_dict['CV'], 2)],
                'Water Mole Fraction': [round(param_dict['Y'], 6)],
                'Thermal Conductivity (W/(m.K))': [round(param_dict['k'], 6)],
                'Viscosity (Pa.s * 1e3)': [round(param_dict['Visc'] * 1e3, 8)]
            }

            #

            # Creating the DataFrame

            df_p_param_dict_1 = pd.DataFrame.from_dict(p_param_dict_1, orient='index', columns=['Value'])
            pd.options.display.float_format = '{:.4f}'.format
            # display(df_p_param_dict_1)
            df_p_param_dict = df_p_param_dict_1.dropna(subset=['Value'])

            #

        except:
            df_p_param_dict = 0
            pass

        col2.dataframe(df_p_param_dict, use_container_width=True)