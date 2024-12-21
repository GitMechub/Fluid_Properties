import streamlit as st
st.session_state.update(st.session_state)
for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os
path = os.path.dirname(__file__)
my_file = path+'/pages/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='Fluid Properties Coolprop',
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

st.title("Fluid Properties v1.0.0", anchor=False)

col1, col2 = st.columns([1, 2])

col1.subheader("Setup", divider="gray", anchor=False)


if 'active_page' not in st.session_state:
    st.session_state.active_page = '1_Fluid_Properties'
    st.session_state.input_P = 101.325
    st.session_state.input_T = 30
    st.session_state.input_U = 100000.0
    st.session_state.input_H = 200000.0
    st.session_state.input_S = 1000.0
    st.session_state.input_Q = 0.5
    st.session_state.input_D = 1.0

    st.session_state.fluid = 'H2O'

# Refrigerant selection
fluid = col1.selectbox(
    'Refrigerant Fluid',
    [
        "1-Butene", "Acetone", "Air", "Ammonia", "Argon", "Benzene", "CH4", "CO", "CO2",
        "CycloHexane", "CycloPropane", "Cyclopentane", "H2", "H2O", "R134a", "R410A", "n-Butane"
    ],
    key='fluid'
)
if fluid != st.session_state.get('fluid', None):
    st.session_state['fluid'] = fluid

# Define default values for parameters
default_values = {
    "Pressure": 101.325,  # kPa
    "Temperature": 25.0,  # °C (use float for consistency)
    "Mass specific internal energy": 100000.0,  # J/kg
    "Mass specific enthalpy": 200000.0,  # J/kg
    "Mass specific entropy": 1000.0,  # J/kgK
    "Quality": 0.5,  # Unitless (0-1 for two-phase systems)
    "Mass density": 1.0  # kg/m³
}

# Parameter mapping for CoolProp
coolprop_params = {
    "Pressure": "P",
    "Temperature": "T",
    "Mass specific internal energy": "U",
    "Mass specific enthalpy": "H",
    "Mass specific entropy": "S",
    "Quality": "Q",
    "Mass density": "D"
}

# Input parameter selection
options = col1.multiselect(
    "Choose 2 input parameters",
    list(default_values.keys()),
    max_selections=2
)

# Dynamically display input fields for the selected parameters
inputs = {}
for param in options:
    inputs[param] = col1.number_input(
        label=f"{param} ({'kPa' if param == 'Pressure' else '°C' if param == 'Temperature' else 'J/kg' if param == 'Mass specific internal energy' else 'J/kg' if param == 'Mass specific enthalpy' else 'J/(kg.K)' if param == 'Mass specific entropy' else 'Unitless' if param == 'Quality' else 'kg/m³' if param == 'Mass density' else ''})",
        value=float(default_values[param]),  # Ensure default value is float
        format="%f",
        step=1.0,  # Step must also be float
        key=f'input_{coolprop_params[param]}',
        min_value=0. if param in ['Pressure', 'Mass density', 'Quality'] else None,
        max_value=1. if param in ['Quality'] else None
    )

    if inputs[param] != st.session_state.get(f'input_{coolprop_params[param]}', None):
        st.session_state[f'input_{coolprop_params[param]}'] = inputs[param]

################# FUNCTIONS #################

# Função principal para calcular as propriedades
def Fluid_Properties(param_dict, input_list, fluid):
    try:
        # Verificação mínima de entrada
        if len(input_list) < 2:
            raise ValueError("Error: 'input_list' must contain at least 2 variables (e.g., pressure, temperature).")

        # Lista de parâmetros a calcular
        params = [
            'P', 'T', 'U', 'H', 'S', 'Q', 'D',
            'DMOLAR',  # Molar density in mol/m^3
            'HMOLAR',  # Molar specific enthalpy in J/mol
            'SMOLAR',  # Molar specific entropy in J/mol/K
            'UMOLAR',  # Molar specific internal energy in J/mol
            'CONDUCTIVITY',  # Thermal conductivity in W/m/K
            'CVMASS',  # Mass specific constant volume specific heat in J/kg/K
            'CVMOLAR',  # Molar specific constant volume specific heat in J/mol/K
            'V',  # Viscosity in Pa s
            'PRANDTL',  # Prandtl number
            'A',  # Speed of sound in m/s
            'GAS_CONSTANT',  # Molar gas constant in J/mol/K
            'GMASS',  # Mass specific Gibbs energy in J/kg
            'GMOLAR',  # Molar specific Gibbs energy in J/mol
            'Z',  # Compressibility Factor
            'PTRIPLE', # Pressure at the triple point (pure only)
            'PCRIT', # Pressure at the critical point in kPa
            'TCRIT' # Temperature at the critical point in K
        ]

        # Remove os parâmetros que já estão na lista de entrada
        params = [param for param in params if param not in input_list]

        # Calcula cada parâmetro restante
        for param in params:
            try:
                param_dict[param] = PropsSI(
                    param,
                    input_list[0], param_dict[input_list[0]],
                    input_list[1], param_dict[input_list[1]], fluid
                )
            except Exception as e:
                # Apenas exibe uma mensagem de erro se necessário
                print(f"Error calculating {param}: {e}")
                param_dict[param] = np.nan
                pass

        return param_dict

    except KeyError as e:
        raise KeyError(f"Error: Missing key {str(e)} in 'param_dict'. Ensure all required variables are defined.") from e
    except ValueError as e:
        raise ValueError(f"Value Error: {str(e)}. Check the values in 'param_dict' and 'input_list'.") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}.") from e


################# RUNNING #################

# Run button
if len(options) == 2:
    run_button = col1.button("Run", use_container_width=True)

    param_dict = {}
    if run_button:

        input_list = []
        for param in inputs.keys():
            # Check if the parameter exists in CoolProp mapping and append the mapped key
            if param in coolprop_params:
                input_list.append(coolprop_params[param])
                if coolprop_params[param] == 'T':
                    param_dict[coolprop_params[param]] = inputs[param] + 273.15
                elif coolprop_params[param] == 'P':
                    param_dict[coolprop_params[param]] = inputs[param]*1e3
                else:
                    param_dict[coolprop_params[param]] = inputs[param]

        try:
            param_dict_0 = Fluid_Properties(param_dict, input_list, fluid)

            # Ajuste das variáveis para exibir no DataFrame
            param_dict_1 = {
                'Pressure (kPa)': [round(param_dict_0['P'] / 1e3, 2)],
                'Temperature (°C)': [round(param_dict_0['T'] - 273.15, 2)],
                'Internal Energy (J/kg)': [round(param_dict_0['U'], 2)],
                'Enthalpy (J/kg)': [round(param_dict_0['H'], 2)],
                'Entropy (J/(kg.K))': [round(param_dict_0['S'], 2)],
                'Quality': [param_dict_0['Q']],
                'Mass Density (kg/m³)': [round(param_dict_0['D'], 2)],
                'Molar Density (mol/m³)': [round(param_dict_0['DMOLAR'], 3)],
                'Molar Enthalpy (J/mol)': [round(param_dict_0['HMOLAR'], 2)],
                'Molar Entropy (J/mol/K)': [round(param_dict_0['SMOLAR'], 2)],
                'Molar Internal Energy (J/mol)': [round(param_dict_0['UMOLAR'], 2)],
                'Thermal Conductivity (W/(m.K))': [round(param_dict_0['CONDUCTIVITY'], 6)],
                'Mass Specific Heat at Constant Volume (J/(kg.K))': [round(param_dict_0['CVMASS'], 2)],
                'Molar Specific Heat at Constant Volume (J/(mol.K))': [round(param_dict_0['CVMOLAR'], 2)],
                'Viscosity (Pa.s * 1e3)': [round(param_dict_0['V'] * 1e3, 8)],
                'Prandtl Number': [round(param_dict_0['PRANDTL'], 3)],
                'Speed of Sound (m/s)': [round(param_dict_0['A'], 2)],
                'Molar Gas Constant (J/(mol.K))': [round(param_dict_0['GAS_CONSTANT'], 2)],
                'Mass Specific Gibbs Energy (J/kg)': [round(param_dict_0['GMASS'], 2)],
                'Molar Gibbs Energy (J/mol)': [round(param_dict_0['GMOLAR'], 2)],
                'Compressibility Factor': [round(param_dict_0['Z'], 5)],
                'Pressure at Triple Point (kPa)': [round(param_dict_0['PTRIPLE'] / 1e3, 2)],
                'Pressure at Critical Point (kPa)': [round(param_dict_0['PCRIT'] / 1e3, 2)],
                'Temperature at Critical Point (°C)': [round(param_dict_0['TCRIT'] - 273.15, 2)]
            }

            # Criação do DataFrame
            df_param_dict_1 = pd.DataFrame.from_dict(param_dict_1, orient='index', columns=['Value'])
            pd.options.display.float_format = '{:.4f}'.format
            df_param_dict = df_param_dict_1.dropna(subset=['Value'])
            # Exibe o DataFrame
            print(df_param_dict_1)

        except Exception as e:
            print(f"An error occurred: {e}")
            df_param_dict_1 = None

        col2.dataframe(df_param_dict_1, use_container_width=True)