import streamlit as st
import numpy as np
from LatexRagLLM import LatexLLM
from lectures import LECTURES
from resultsSave import ResultsSaver
import random
import time

@st.cache_resource
def get_LLM():
    llm = LatexLLM()
    return llm

# # Streamed response emulator
# def response_generator():
#     response = random.choice(
#         [
#             "Hello there! How can I assist you today?",
#             "Hi, human! Is there anything I can help you with?",
#             "Do you need help?",
#             "$$\\text{Annual Cost} = \\left(\\frac{\\text{Miles per Year}}{\\text{Fuel Efficiency}}\\right) \\times \\text{Price per Gallon}$$"
#         ]
#     )
#     for word in response.split():
#         yield word + " "
#         time.sleep(0.05)

if "rs" not in st.session_state:
    st.session_state.rs = ResultsSaver()
if "models" not in st.session_state:
    st.session_state.models = ["gpt-oss-20b",
                               "meta-llama-3-8b-instruct",
                               "deepseek-r1-0528-qwen3-8b"]

LLM = get_LLM()

st.title("LLM teacher of AI course")



lectureTitle = st.selectbox(label="Название лекции", index=None, options=LECTURES.keys())
if not lectureTitle == None:
    lectureTopic = st.selectbox(label="Название главы", index=None, options=LECTURES[lectureTitle])

    if not lectureTopic == None:
        model = st.selectbox(label="Название модели", index=None, options=st.session_state.models)

        if not model == None:
            devMode = st.checkbox("DevMode")

            if devMode:
                # Prompt
                st.sidebar.write("## Промпт")
                prompt = st.sidebar.text_area(label="Введите промпт")
                st.session_state.prompt = prompt
                desc = st.sidebar.text_area(label="Введите описание")
                version = 0
                if (v := st.sidebar.number_input(label="Версия", min_value=0)):
                    version = v


                if (st.sidebar.button(label="Сохранить промпт в текущий файл")):
                    st.session_state.rs.savePrompt(prompt, desc, version)



                if (st.sidebar.button(label="Создать новый файл промптов")):
                    st.session_state.rs.startNewPrompt()

                # Dialog
                st.sidebar.write("## Диалог")

                if (st.sidebar.button(label="Сохранить диалог в текущий файл")):
                    if (("messages" in st.session_state) and ("ratings" in st.session_state)):
                        st.session_state.rs.saveDialog(st.session_state.messages, st.session_state.ratings)


                if (st.sidebar.button(label="Создать новый файл диалогов")):
                    st.session_state.rs.startNewDialog()
                    st.session_state.ratings = []
                    st.session_state.messages = []

                # Report
                st.sidebar.write("## Отчет")
                modelName = st.sidebar.text_area(label="Введите имя модели", value=model)

                modelParams = st.sidebar.text_area(label="Введите кол-во параметров модели")

                ltip = st.session_state.lectureTitle if ("lectureTitle" in st.session_state) else ""
                ltop = st.session_state.lectureTopic if ("lectureTopic" in st.session_state) else ""

                lTitle = st.sidebar.text_area(label="Введите название лекции", value=ltip)
                lTopic = st.sidebar.text_area(label="Введите название главы", value=ltop)

                oRatings = np.mean(st.session_state.ratings, where=[st.session_state.ratings[f] > 0 for f in range(len(st.session_state.ratings))]) if (
                            ("ratings" in st.session_state) and (len(st.session_state.ratings) > 0)) else 0

                st.sidebar.write(f"Рекомендуемая оценка эксперимента: {oRatings}")

                rate = st.sidebar.number_input(label="Введите оценку эксперименту в целом", min_value=0)

                notes = st.sidebar.text_area(label="Введите заметку к эксперименту")


                if (st.sidebar.button(label="Сохранить в финальный отчет")):
                    st.session_state.rs.addRowToReport(modelName, modelParams, lTitle, lTopic, rate, notes)

                st.sidebar.write("## Оценки диалога:")

                if ("ratings" in st.session_state):
                    st.sidebar.write(st.session_state.ratings)

                st.sidebar.write("## Кеш")

                if (st.sidebar.button(label="Очистить кеш Streamlit")):
                    st.cache_resource.clear()
                    st.rerun()

            st.session_state.lectureTitle = lectureTitle
            st.session_state.lectureTopic = lectureTopic


            left,  right = st.columns(2, vertical_alignment="top")



            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            if "ratings" not in st.session_state:
                st.session_state.ratings = []

            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                if message["role"] == "user":
                    with left.chat_message(message["role"]):
                        left.markdown(message["content"])
                else:
                    with right.chat_message(message["role"]):
                        right.markdown(message["content"])

            # Accept user input
            if query := st.chat_input("Введите вопрос?"):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": query})
                # Display user message in chat message container
                with left.chat_message("user"):
                    left.markdown(query)
                    st.session_state.ratings.append(0)

                    #compare len of messages and ratings and if len_m > len_r append 0 for equ lens
                    #if (len(st.session_state.messages) > len(st.session_state.ratings)):
                     #   st.session_state.ratings.append(0)


                # Display assistant response in chat message container
                with right.chat_message("assistant"):
                    response = right.write_stream(LLM.stream(
                        modelName=model,
                        lTitle=lectureTitle,
                        prompt=st.session_state.prompt,
                        userQuery=query,
                        chatHistory=st.session_state.messages
                    ))
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
            # Add rating to bot response
            if (("messages" in st.session_state) and (len(st.session_state.messages) > 0)):
                if (rr := right.chat_input(placeholder="Оцените ответ поледний бота (от 0 до 10)",)):
                    try:
                        st.session_state.ratings.append(int(rr))
                    except:
                        st.session_state.ratings.append(0)

