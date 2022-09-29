import streamlit as st

# Title
st.title("Hello python class !")


# Header
st.header("This is a header")

# Subheader
st.subheader("This is a subheader")

st.text("Hello again !!")


# Markdown
st.markdown("### This is a markdown")


# success
st.success("Success")

# success
st.info("Information")

# success
st.warning("Warning")

# success
st.error("Error")


# Write text
st.write("Text with write")

# Writing python inbuilt function range()
st.write(range(10))


# Display Images

# import Image from pillow to open images
from PIL import Image

img = Image.open("../images/architecture.png")

# display image using streamlit
# width is used to set the width of an image
st.image(img, width=200)


# checkbox
# check if the checkbox is checked
# title of the checkbox is 'Show/Hide'
if st.checkbox("Show/Hide"):

    # display the text if the checkbox returns True value
    st.text("Showing the widget")


# radio button
# first argument is the title of the radio button
# second argument is the options for the ratio button
status = st.radio("Select favourite pet: ", ("Dog", "Cat"))

# conditional statement to print
if status == "Dog":
    st.success("Dog")
else:
    st.success("Cat")


# Selection box

# first argument takes the titleof the selectionbox
# second argument takes options
hobby = st.selectbox("Hobbies: ", ["Dancing", "Reading", "Sports"])

# print the selected hobby
st.write("Your hobby is: ", hobby)


# multi select box

# first argument takes the box title
# second argument takes the options to show
hobbies = st.multiselect("Hobbies: ", ["Dancing", "Reading", "Sports"])

# write the selected options
st.write("You selected", len(hobbies), "hobbies")


# Create a simple button that does nothing
st.button("Click me for no reason")

# Create a button, that when clicked, shows a dictionary printed in the app
if st.button("About"):
    st.write({"Name": "John", "Age": 30, "Address": "New York", "Phone": 1234567890})


# Text Input

# save the input text in the variable 'name'
# first argument shows the title of the text input box
# second argument displays a default text inside the text input area
name = st.text_input("Enter Your name", "Type Here ...")

# .title() is used to get the input text string
if st.button("Submit"):
    result = name.title()
    st.success(result)

# slider

# first argument takes the title of the slider
# second argument takes the starting of the slider
# last argument takes the end number
level = st.slider("Select the level", 1, 5)

# print the level
# format() is used to print value
# of a variable at a specific position
st.text("Selected: {}".format(level))


# give a title to our app
st.title("Welcome to the Calculator App")

if "final_result" not in st.session_state:
    st.session_state.final_result = ""

st.write("This results calculated until now:")

st.write(st.session_state.final_result)

# reset the result
if st.button("Reset"):
    st.session_state.final_result = ""

# TAKE WEIGHT INPUT in kgs
X = st.number_input("Enter your X")
Y = st.number_input("Enter your Y")

# TAKE HEIGHT INPUT
# radio button to choose height format
addition_or_multiplication = st.radio("Select the operation", ("add", "multiply"))

if st.button("Calculate"):
    if addition_or_multiplication == "add":
        result = X + Y
    else:
        result = X * Y
    # print the BMI INDEX
    st.text("The result is {}.".format(result))
    st.session_state.final_result += str(result) + " "
