import streamlit as st

# Display the page based on the URL path
query_params = st.query_params

if query_params.get("page") == ["fighters"]:
    st.title("Fighters Page")
    st.write("Welcome to the Fighters Page!")
else:
    st.title("Main Page")
    st.write("This is the main page. Click a button to navigate.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Turnaje"):
            # Use meta-refresh to navigate to /fighters
            st.markdown('<meta http-equiv="refresh" content="0; URL=/turnaje" />', unsafe_allow_html=True)

    with col2:
        if st.button("Fighters"):
            # Use meta-refresh to navigate to /fighters
            st.markdown('<meta http-equiv="refresh" content="0; URL=/fighters?fighter=Leo Brichta" />', unsafe_allow_html=True)

#streamlit run c:/Users/admin/Desktop/Pythony/Clashdog/main.py --client.showErrorDetails=false
