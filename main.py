import streamlit as st
import pandas as pd
from gtts import gTTS
import tempfile
import os
import io

# Sidebar with additional information or options
st.sidebar.title("About")
st.sidebar.info(
    "This is a simple Streamlit app for managing a grocery list with quantities (in kg). "
    "You can add items along with their quantities, search for items, clear the list, pop the last item, and export to Excel."
)
# Title and description
st.title("Grocery List App")
st.write("Add grocery items along with their quantities (in kg) to your list and search for them.")

# Create an empty dictionary to store grocery items and quantities, or load from the previous session
grocery_dict = st.session_state.get("grocery_dict", {})

# Input fields to add grocery items and quantities
new_item = st.text_input("Add a grocery item:")
quantity = st.number_input("Quantity (in kg):", min_value=0.01, step=0.01, format="%.2f", value=0.01)
if st.button("Add"):
    if new_item.strip():  # Check if the input is not empty
        # Find the next available number for the item
        item_number = len(grocery_dict) + 1
        grocery_dict[item_number] = {"Item": new_item, "Quantity": f"{quantity} kg"}
        st.success(f"'{new_item}' (Quantity: {quantity} kg) added to the list.")

# Button to pop out the last element from the grocery list
if st.button("Pop Last Item"):
    if grocery_dict:
        last_item_number = max(grocery_dict.keys())
        popped_item = grocery_dict.pop(last_item_number)
        st.success(f"Popped '{popped_item['Item']}' (Quantity: {popped_item['Quantity']}) from the list.")
    else:
        st.warning("The grocery list is empty. Add items before popping.")

# Sidebar layout for additional information or options
with st.sidebar:
    # Search bar to search for items
    search_term = st.text_input("Search for a grocery item:")

# Display the grocery dictionary using pandas in tabular format
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

# Button to clear the grocery list
if st.button("Clear List"):
    grocery_dict.clear()
    st.success("Grocery list cleared.")

# Button to reset the search
if st.button("Reset Search"):
    search_term = ""
    st.text_input("Search for a grocery item:", value="")

# Store the updated grocery dictionary in session state
st.session_state["grocery_dict"] = grocery_dict

# User input for text-to-speech
text_input_list = [(item_number, data["Item"], data["Quantity"]) for item_number, data in
                   grocery_dict.items()]  # Create a list of tuples
text_input = "\n\n".join([f"{item_number}: {item} ({quantity})" for item_number, item, quantity in
                          text_input_list])  # Join items and quantities with two newlines for a gap


# Text-to-Speech function
def text_to_speech(text):
    try:
        # Create a gTTS object
        tts = gTTS(text)

        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            tts.save(temp_audio.name)

        # Play the audio using st.audio
        st.audio(temp_audio.name, format="audio/mp3")

        # Clean up: Remove the temporary audio file
        os.unlink(temp_audio.name)
    except Exception as e:
        st.error(f"Error: {e}")


# Button to trigger text-to-speech
if st.button("Convert to Speech"):
    if text_input:
        text_to_speech(text_input)
    else:
        st.warning("Please enter some text to convert to speech.")

# Export grocery dictionary to Excel
if st.button("Export to Excel"):
    if grocery_dict:
        # Create a DataFrame from the grocery dictionary
        export_df = pd.DataFrame(grocery_dict).T.reset_index(drop=True)

        # Create an in-memory Excel file buffer
        excel_buffer = io.BytesIO()

        # Write the DataFrame to the Excel buffer
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            export_df.to_excel(writer, sheet_name="Grocery List", index=False)

        # Download the Excel file
        excel_buffer.seek(0)
        st.download_button("Download Excel", excel_buffer, key="excel_download", file_name="grocery_list.xlsx")
    else:
        st.warning("The grocery list is empty. Add items before exporting to Excel.")
