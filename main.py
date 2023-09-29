import streamlit as st
import pandas as pd
from gtts import gTTS
import tempfile
import os
import io

#Sidebar
st.sidebar.title("About")
st.sidebar.info(
    "This is a simple Streamlit app for managing a grocery list with quantities(in kg). "
    "You can add items along with their quantities, search for items, clear the list, pop the last item, and export to Excel."
)
#Title
st.title("Grocery List App")
st.write("Add grocery items along with their quantities (in kg) to your list and search for them.")

#dictionary initialisation
grocery_dict = st.session_state.get("grocery_dict", {})

#Input
new_item = st.text_input("Add a grocery item:")
quantity = st.number_input("Quantity (in kg):", min_value=0.01, step=0.01, format="%.2f", value=0.01)
if st.button("Add"):
    if new_item.strip():
        item_number = len(grocery_dict) + 1
        grocery_dict[item_number] = {"Item": new_item, "Quantity": f"{quantity} kg"}
        st.success(f"'{new_item}' (Quantity: {quantity} kg) added to the list.")

#pop button
if st.button("Pop Last Item"):
    if grocery_dict:
        last_item_number = max(grocery_dict.keys())
        popped_item = grocery_dict.pop(last_item_number)
        st.success(f"Popped '{popped_item['Item']}' (Quantity: {popped_item['Quantity']}) from the list.")
    else:
        st.warning("The grocery list is empty. Add items before popping.")

#Sidebar layout
with st.sidebar:
    #Searchbar
    search_term = st.text_input("Search for a grocery item:")

#Display dict
st.subheader("Grocery List:")
filtered_items = {}
for item_number, data in grocery_dict.items():
    if search_term.lower() in data["Item"].lower():
        filtered_items[item_number] = data

if search_term:
    df = pd.DataFrame([(item_number, data["Item"], data["Quantity"]) for item_number, data in filtered_items.items()],
                      columns=["S.no", "Grocery Item", "Quantity"])
else:
    df = pd.DataFrame([(item_number, data["Item"], data["Quantity"]) for item_number, data in grocery_dict.items()],
                      columns=["S.no", "Grocery Item", "Quantity"])
if not df.empty:
    st.dataframe(df.style.hide_index())  # Use st.dataframe instead of st.write to display it in tabular format

#clear button
if st.button("Clear List"):
    grocery_dict.clear()
    st.success("Grocery list cleared.")

#reset button
if st.button("Reset Search"):
    search_term = ""
    st.text_input("Search for a grocery item:", value="")

#update
st.session_state["grocery_dict"] = grocery_dict

#input textspeech
text_input_list = [(item_number, data["Item"], data["Quantity"]) for item_number, data in
                   grocery_dict.items()]
text_input = "\n\n".join([f"{item_number}: {item} ({quantity})" for item_number, item, quantity in
                          text_input_list])


#text speech function
def text_to_speech(text):
    try:
        #gTTS object
        tts = gTTS(text)

        #temp file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            tts.save(temp_audio.name)

        #play audio
        st.audio(temp_audio.name, format="audio/mp3")

        #clean the audio file
        os.unlink(temp_audio.name)
    except Exception as e:
        st.error(f"Error: {e}")


#button textspeech
if st.button("Convert to Speech"):
    if text_input:
        text_to_speech(text_input)
    else:
        st.warning("Please enter some text to convert to speech.")

#excel
if st.button("Export to Excel"):
    if grocery_dict:
        export_df = pd.DataFrame(grocery_dict).T.reset_index(drop=True)

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            export_df.to_excel(writer, sheet_name="Grocery List", index=False)

        #button download excel
        excel_buffer.seek(0)
        st.download_button("Download Excel", excel_buffer, key="excel_download", file_name="grocery_list.xlsx")
    else:
        st.warning("The grocery list is empty. Add items before exporting to Excel.")
