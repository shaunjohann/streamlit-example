from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import os
import yaml

from langchain.agents import create_openapi_agent
from langchain.agents.agent_toolkits import OpenAPIToolkit
from langchain.llms.openai import OpenAI
from langchain.requests import RequestsWrapper
from langchain.tools.json.tool import JsonSpec

with open("openai_openapi.yml") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
json_spec=JsonSpec(dict_=data, max_value_length=4000)

headers = {
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
}
requests_wrapper=RequestsWrapper(headers=headers)

openapi_toolkit = OpenAPIToolkit.from_llm(OpenAI(temperature=0), json_spec, requests_wrapper, verbose=True)
openapi_agent_executor = create_openapi_agent(
    llm=OpenAI(temperature=0),
    toolkit=openapi_toolkit,
    verbose=True
)

"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""

with st.echo(code_location='below'):
    total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
    num_turns = st.slider("Number of turns in spiral", 1, 100, 9)

    Point = namedtuple('Point', 'x y')
    data = []

    points_per_turn = total_points / num_turns

    for curr_point_num in range(total_points):
        curr_turn, i = divmod(curr_point_num, points_per_turn)
        angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
        radius = curr_point_num / total_points
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        data.append(Point(x, y))

    st.altair_chart(alt.Chart(pd.DataFrame(data), height=500, width=500)
        .mark_circle(color='#0068c9', opacity=0.5)
        .encode(x='x:Q', y='y:Q'))

    # Display Langchain commands and allow users to communicate with the agent
    commands = openapi_agent_executor.get_available_commands()
    st.write("Available commands:")
    for command in commands:
        st.write(f"- {command}")

    user_input = st.text_input("Enter a command:")
    if user_input:
        response = openapi_agent_executor.run_command(user_input)
        st.write("Response:")
        st.write(response)
