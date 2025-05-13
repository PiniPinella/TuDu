import streamlit as st

st.title("Hier ein Codeblock:")
st.subheader("Hier kommen alle Infos rein die zur App gehören:")
code = '''def get_user_name(user_id):
    query = "SELECT first_name FROM users WHERE user_id = %s"
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None'''
st.code(code, language="python")

