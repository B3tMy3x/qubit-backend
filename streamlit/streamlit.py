import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from streamlit.components.v1 import html

load_dotenv()
st.set_page_config(
    page_title="Admin Panel"
)

BASE_URL = os.getenv("BASE_URL")

def authenticate_user(username, password):
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password},
        verify=False,
    )
    if response.status_code == 200:
        token = response.json().get("access_token")
        if token:
            return token
        st.error("Токен не найден в ответе.")
    else:
        st.error(f"Ошибка: {response.status_code} - {response.text}")
    return None


def make_api_call(endpoint, token, method='GET', data=None):
    headers = {"token": token}
    url = f"{BASE_URL}/{endpoint}"
    
    if method == 'GET':
        response = requests.get(url, headers=headers, verify=False,)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data, verify=False,)
    
    if response.status_code == 200:
        return response.json()
    
    st.error(f"Ошибка: {response.status_code} - {response.text}")
    return None


def solve_ticket(ticket_id, token):
    response = make_api_call(f"tickets/{ticket_id}", token, method='POST')
    if response:
        st.success(f"Задача {ticket_id} решена успешно!")
    else:
        st.error(f"Не удалось решить задачу {ticket_id}")

def login_page():
    st.markdown(
        """
        <h1 style="color: #8f00ff; font-size: 2.5rem; font-weight: bold;">
            Qubit Admin Panel
        </h1>
        """,
        unsafe_allow_html=True
    ) 
    st.markdown("### ваш центр управления RAG-системой")

    st.markdown("---")
    st.header("Вход")

    username = st.text_input("Имя пользователя", placeholder="Введите ваше имя пользователя")
    password = st.text_input("Пароль", type="password", placeholder="Введите ваш пароль")
    if st.button("Войти"):
        token = authenticate_user(username, password)
        if token:
            st.session_state.token = token
            st.session_state.page = "chats"
            st.rerun()
        else:
            st.error("Неверное имя пользователя или пароль. Попробуйте снова.")


    st.markdown("---")
    st.caption("© 2024 Qubit")



def chats_page():
    st.title("Чаты")
    if "token" not in st.session_state:
        st.warning("Пожалуйста, войдите в систему.")
        st.session_state.page = "login"
        st.rerun()
        return

    token = st.session_state.token
    chats = make_api_call("chats", token)

    if chats:
        sort_option = st.selectbox(
            "Выберите режим сортировки:",
            ["По умолчанию", "По уверенности (возрастание)", "По уверенности (убывание)"]
        )

        if sort_option == "По уверенности (возрастание)":
            chats.sort(key=lambda x: float(x["assurance"]))
        elif sort_option == "По уверенности (убывание)":
            chats.sort(key=lambda x: float(x["assurance"]), reverse=True)

        for chat in chats:
            assurance_value = float(chat["assurance"])

            chat_title = f"💬 Чат {chat['id']} (IP: <span style='color:#8f00ff; font-weight: bold;'>{chat['user_ip']}</span>) Уверенность:  <span style='color:#8f00ff; font-weight: bold;'> {assurance_value:.2f}</span>"

            st.markdown(chat_title, unsafe_allow_html=True)
            st.progress(assurance_value)
            with st.expander("Задачи", expanded=False):

                tickets = make_api_call(f"chats/{chat['id']}", token)
                if tickets:
                    for ticket in tickets:
                        display_ticket(ticket, token)
                else:
                    st.write("Нет задач для этого чата.")
    else:
        st.write("Чаты не найдены.")

def display_ticket(ticket, token):
    st.markdown("---")
    st.subheader(f"🎫 ID задачи: {ticket['id']}")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Вопрос:**")
        st.write(ticket["question"])

    with col2:
        st.write(f"**Ответ:**")
        st.write(ticket["answer"] or "Ответ еще не предоставлен.")

    st.write(f"📅 **Дата:** {ticket['date']}")
    st.write(f"🟢 **Статус:** {'Решено' if ticket['solved'] else 'Не решено'}")
    if not ticket['solved']:
        if st.button(f"Решить задачу {ticket['id']}", key=f"solve_{ticket['id']}"):
            solve_ticket(ticket["id"], token)


def tickets_page():
    st.title("Задачи")
    if "token" not in st.session_state:
        st.warning("Пожалуйста, войдите в систему.")
        st.session_state.page = "login"
        st.rerun()
        return

    token = st.session_state.token
    unsolved_tickets = make_api_call("tickets/unsolved", token)

    if unsolved_tickets:
        st.subheader("Нерешенные задачи")
        for ticket in unsolved_tickets:
            display_ticket(ticket, token)


def settings_page():
    st.title("Настройки")
    if "token" not in st.session_state:
        st.warning("Пожалуйста, войдите в систему.")
        st.session_state.page = "login"
        st.rerun()
        return

    st.subheader("Выбор модели")
    model_options = ["GPT4o", "Локальная модель"]

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = model_options[0]

    selected_model = st.selectbox(
        "Выберите модель:",
        model_options,
        index=model_options.index(st.session_state.selected_model),
    )

    st.session_state.selected_model = selected_model
    st.success(f"Выбрана модель: {selected_model}")


def logout_page():
    st.title("Выход")
    st.session_state.token = None
    st.session_state.page = "login"
    st.success("Вы вышли из системы!")
    st.rerun()


def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "token" not in st.session_state:
        st.session_state.token = None

    with st.sidebar:
        if st.session_state.token:
            selected = option_menu(
                "Навигация",
                ["Чаты", "Задачи", "Настройки", "Выход"],
                icons=["chat", "ticket", "gear", "power"],
                default_index=0,
                orientation="vertical",
            )
        else:
            selected = option_menu(
                "Навигация",
                ["Вход"],
                icons=["person"],
                default_index=0,
                orientation="vertical",
            )
    st.logo("https://b3tmy3x.github.io/depl-widget/Qubit-21.png", size="large")
    if selected == "Вход":
        st.session_state.page = "login"
    elif selected == "Чаты":
        st.session_state.page = "chats"
    elif selected == "Задачи":
        st.session_state.page = "tickets"
    elif selected == "Настройки":
        st.session_state.page = "settings"
    elif selected == "Выход":
        st.session_state.page = "logout"

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "chats":
        chats_page()
    elif st.session_state.page == "tickets":
        tickets_page()
    elif st.session_state.page == "settings":
        settings_page()
    elif st.session_state.page == "logout":
        logout_page()


st.markdown(
    """
    <style>
    .ef3psqc6 {
        display: none;
    }
    .e16jpq800 {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if __name__ == "__main__":
    main()
