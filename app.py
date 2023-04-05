import logging
logging.info("Importing libraries")
import streamlit as st
import streamlit.components.v1 as components
from controller import generate_net, prompt

print(prompt)

logging.basicConfig(level=logging.INFO, filename="app.log")
logging.basicConfig(level=logging.WARNING, filename="app.log")
logging.basicConfig(level=logging.ERROR, filename="app.log")

logging.info("Starting app.py")
# Expand the default container width
st.set_page_config(layout="wide")

with st.container():
    # Add CSS styles to adjust margins and padding
    st.markdown("""
        <style>
        .stApp {
            margin-top: -100px;
        }
        .stApp > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title("Mind The Map")
    
    # Create input fields for user input and OpenAI API key
    # st.sidebar.title("Input")
    user_input = st.sidebar.text_area("Enter your text here", max_chars=250)
    openai_api_key = st.sidebar.text_input("Enter your OpenAI API key here")
    
    # Create a container for the input and button
    input_col, button_col = st.columns([4, 1])
    with input_col:
        hide_input_label_css = """
            <style>
            div[data-testid="stText"][role="textbox"] > label {visibility: hidden;}
            </style>
            """
        st.markdown(hide_input_label_css, unsafe_allow_html=True)
    with button_col:
            st.write("") # Add some empty space
            st.write("") # Add some empty space
            generate_button = st.sidebar.button("Generate")

    # Call generate_net() function when Generate button is clicked
    if generate_button:
        logging.info("Generating graph")
        with st.spinner("Doing something awesome behind the scenes..."):
            text = generate_net(prompt=prompt, user=user_input, key=openai_api_key)
            logging.info("Graph generated")
            # st.sidebar.title("Output")
            text_output = st.sidebar.empty()
            text_output.markdown("## Description for " + user_input)
            text_output.markdown(text)

    # Hide the Streamlit menu and footer to maximize white space
    # hide_menu_footer_css = """
    #     <style>
    #     #MainMenu, footer {visibility: hidden;}
    #     </style>
    #     """
    # st.markdown(hide_menu_footer_css, unsafe_allow_html=True)

# Open the experiment.html file in the HtmlFile variable and add it to the components.html
with open("experiment.html", "r") as HtmlFile:
    source_code = HtmlFile.read()
    html_url = "./experiment.html"
    components.html(source_code, scrolling=False, height=800, width=1300)