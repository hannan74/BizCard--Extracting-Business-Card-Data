import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import numpy as np
from PIL import Image
import re
import io
import mysql.connector

################# GETTING IMAGE OF BUSINESS CARDS ############################

def image_path(path):

    image = Image.open(path)

    #Converting Image into array

    image_arr= np.array(image)

    #Getting data from image

    image_read= easyocr.Reader(['en'])
    image_ocr = image_read.readtext(image_arr, detail=0)

    return image_ocr, image



############### TO DICTIONARY FORMAT #######################


def extract_data(txt):

    data_dict = {"NAME": [], "DESIGNATION": [], "COMPANY_NAME": [], "MOBILE": [], "EMAIL": [], "COMPANY_URL": [],
                    "ADDRESS": [], "PINCODE": []}

    data_dict["NAME"].append(txt[0])
    data_dict["DESIGNATION"].append(txt[1])

    for item in range(2, len(txt)):
        
        if "@"  in txt[item] and ".com" in txt[item]:
            data_dict["EMAIL"].append(txt[item].lower())

        elif 'www' in txt[item] or 'WWW' in txt[item] or 'wwW' in txt[item] or 'Www' in txt[item] or 'wWw' in txt[item]:
            data_dict["COMPANY_URL"].append(txt[item].lower())

        elif "Tamil Nadu" in txt[item] or "TamilNadu" in txt[item]  or re.match(r'\b\d{6}\b', txt[item])  or txt[item].isdigit():
            data_dict["PINCODE"].append(txt[item])

        elif re.match(r"^[a-zA-Z\s,]", txt[item]):
            data_dict["COMPANY_NAME"].append(txt[item])

        elif txt[item].startswith("+") or (txt[item].replace("-", "").isdigit() and '-' in txt[item]):
            data_dict["MOBILE"].append(txt[item])
            
        else:
            filtered_add = re.sub(r"[,;]", "", txt[item])
            data_dict["ADDRESS"].append(filtered_add)

    for key, value in data_dict.items():
        if len(value)>0:
            something = ' '.join(value)
            data_dict[key] = [something]

        else:
            value = 'None'
            data_dict[key] = [value]

    return data_dict




############################# STREAMLIT ###################################

st.set_page_config(layout='wide')
st.backgroundColor = '6739B7'

st.header(':violet[BIZCARD-X]',anchor=False)
st.write('**(Note)**:-**Extracting business card Data with OCR**')
st.balloons()


with st.sidebar:
    st.title(":green[CAPSTONE PROJECT-3]")
    st.header("Introduction about Myself")
    st.caption("Name : Mohamed Hannan. S")
    st.caption("Course : Master in DataScience")
    st.caption("Batch : MDE88")

options = option_menu(
                menu_title = "Explore",
                options=["Home", "Data Exploration and Modification","Remove"],
                icons=["house-fill","database-fill","archive"],
                default_index = 0,
                menu_icon="cast",
                orientation="horizontal",
                key="navigation_menu",
                styles={
                        "font_color": "#DC143C",   
                        "border": "2px solid #DC143C", 
                        "padding": "10px 25px"   
                    }
            )

if options == "Home":
    
    st.write("""
    # BizCardX: Extracting Business Card Data with OCR

    ## Introduction:
    BizCardX is a Streamlit application designed to extract relevant information from business cards using Optical Character Recognition (OCR) technology. The application allows users to upload images of business cards, from which it extracts details such as company name, cardholder name, designation, contact information, email address, website URL, address, and pin code. The extracted information is then displayed in a clean and organized manner in the application's graphical user interface (GUI). Users can also save the extracted data along with the uploaded business card image into a database for future reference.

    ## Technologies Used:
    - Python: Programming language used for application development.
    - Streamlit: Web application framework for building interactive and customizable GUIs.
    - easyOCR: Python library for performing OCR tasks on images.
    - PIL (Python Imaging Library): Library for opening, manipulating, and saving many different image file formats.
    - Pandas: Library for data manipulation and analysis.
    - NumPy: Library for numerical computing.
    - Regular Expressions (regex): Used for text pattern matching and extraction.
    - MySQL: Relational database management system for storing extracted business card data.

    ## Problem Statement:
    The goal of BizCardX is to simplify the process of extracting and managing information from business cards. Traditional methods of manually entering data from business cards into digital formats can be time-consuming and error-prone. BizCardX addresses this challenge by automating the extraction process using OCR technology, thereby saving time and improving accuracy.

    ## Application Features:
    - Image Upload: Users can upload images of business cards through the application interface.
    - OCR Extraction: The application uses easyOCR to extract text from the uploaded images.
    - Data Display: Extracted information is displayed in a structured format within the application's GUI.
    - Database Integration: Users can save extracted data along with the uploaded images into a MySQL database.
    - Data Management: The application allows users to read, update, and delete data entries from the database through the Streamlit UI.
    - User-Friendly Interface: The GUI is designed to be intuitive and easy to navigate, guiding users through the extraction and management process.

    ## Application Workflow:
    - User uploads an image of a business card through the application interface.
    - OCR technology extracts text from the uploaded image.
    - Extracted information is displayed in the application's GUI.
    - User has the option to save the extracted data into a MySQL database along with the uploaded image.
    - Users can also perform CRUD (Create, Read, Update, Delete) operations on the database entries through the Streamlit UI.

    ## Conclusion:
    BizCardX simplifies the process of managing business card information by leveraging OCR technology and database integration. It streamlines data extraction, improves accuracy, and provides users with a convenient way to store and manage business card details digitally. With its user-friendly interface and robust features, BizCardX is a valuable tool for businesses and individuals alike.
    """)


elif options == "Data Exploration and Modification":
    img= st.file_uploader("UPLOAD THE IMAGE", type= ["png", "jpg", "jpeg"])

    if img is not None:
        st.image(img, width=600)

        txt_image, Image= image_path(img)

        txt_image_dict = extract_data(txt_image)

        if txt_image_dict:
            st.success("FILE EXTRACTED SUCCESSFULLY!")

        df_txt_image_dict= pd.DataFrame(txt_image_dict)
        ########################## BINARY FORMAT ##########################

        image_bin = io.BytesIO()
        Image.save(image_bin, format="PNG")

        image_data = image_bin.getvalue()
        

        ### IN DICTIONARY ###

        img_data_dict = {"IMAGE" : [image_data]}

        df_img_data_dict = pd.DataFrame(img_data_dict)

        df_all= pd.concat([df_txt_image_dict, df_img_data_dict], axis=1)
        st.dataframe(df_all)

        click = st.button("Store into SQL Databses", use_container_width = True)

        if click:

            mydb = mysql.connector.connect(host ='localhost',user='root',password='7ApriL@2002',database='bizcard')
            mycursor=mydb.cursor()


            ################# CREATING TABLE IN SQL ###########################

            create_query= '''create table if not exists card_details(name varchar(300),
                                                                        designation varchar(300),
                                                                        company_name varchar(300),
                                                                        mobile varchar(300),
                                                                        email varchar(300),
                                                                        company_url varchar(300),
                                                                        address varchar(300),
                                                                        pincode varchar(300),
                                                                        image LONGBLOB
                                                                        )'''

            mycursor.execute(create_query)
            mydb.commit()


            ########################## INSERTING THE VALUES IN MYSQL #####################################

            insert_query = '''INSERT INTO card_details(name,
                                                        designation,
                                                        company_name,
                                                        mobile,
                                                        email,
                                                        company_url,
                                                        address,
                                                        pincode,
                                                        image)
                                                        
                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            values= df_all.values.tolist()[0]
            mycursor.execute(insert_query, values)
            mydb.commit()


            st.success("Upload Sucessfully Completed")
        
        st.divider()

    radio = st.radio("Select the Method", ["None", "Preview","Modify"])

    if radio == "None":
        pass

    elif radio == "Preview":

        mydb = mysql.connector.connect(host ='localhost',user='root',password='7ApriL@2002',database='bizcard')
        mycursor=mydb.cursor()

        #Preview the table
        query = "SELECT * FROM card_details"

        mycursor.execute(query)
        table = mycursor.fetchall()
        mydb.commit()

        df1 = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "MOBILE", "EMAIL", "COMPANY_URL", "ADDRESS", "PINCODE", "IMAGE"))
        st.dataframe(df1)

    elif radio == "Modify":

        mydb = mysql.connector.connect(host ='localhost',user='root',password='7ApriL@2002',database='bizcard')
        mycursor=mydb.cursor()

        #Preview the table
        query = "SELECT * FROM card_details"

        mycursor.execute(query)
        table = mycursor.fetchall()
        mydb.commit()

        df1 = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "MOBILE", "EMAIL", "COMPANY_URL", "ADDRESS", "PINCODE", "IMAGE"))
        

        col1,col2 = st.columns(2)

        with col1:

            selected = st.selectbox("Select the Name to be Modified", df1["NAME"])

        name_df = df1[df1["NAME"] == selected]
        

        name_df_copy= name_df.copy()
        

        col3,col4 = st.columns(2)

        with col3:

            new_name = st.text_input("Name", name_df["NAME"].unique()[0])
            new_designation = st.text_input("Designation", name_df["DESIGNATION"].unique()[0])
            new_company_name = st.text_input("Company_Name", name_df["COMPANY_NAME"].unique()[0])
            new_mobile = st.text_input("Mobile", name_df["MOBILE"].unique()[0])

            name_df_copy["NAME"] = new_name
            name_df_copy["DESIGNATION"] = new_designation
            name_df_copy["COMPANY_NAME"] = new_company_name     
            name_df_copy["MOBILE"] = new_mobile
            
            

        with col4:

            new_email = st.text_input("Email", name_df["EMAIL"].unique()[0])
            new_company_url = st.text_input("Company_URL", name_df["COMPANY_URL"].unique()[0])
            new_address = st.text_input("Address", name_df["ADDRESS"].unique()[0])
            new_pincode  =st.text_input("Pincode", name_df["PINCODE"].unique()[0])

            name_df_copy["EMAIL"] = new_email
            name_df_copy["COMPANY_URL"] = new_company_url
            name_df_copy["ADDRESS"] = new_address 
            name_df_copy["PINCODE"] = new_pincode

        st.dataframe(name_df_copy)

        col5,col6= st.columns(2)
        with col5:
            button = st.button("Modify the Data", use_container_width=True)

        if button:

            mydb = mysql.connector.connect(host ='localhost',user='root',password='7ApriL@2002',database='bizcard')
            mycursor=mydb.cursor()

            mycursor.execute(f"DELETE FROM card_details WHERE NAME = '{selected}'")
            mydb.commit()

            # Insert Query

            insert_query_mo = '''INSERT INTO card_details(name,
                                                        designation,
                                                        company_name,
                                                        mobile,
                                                        email,
                                                        company_url,
                                                        address,
                                                        pincode,
                                                        image)
                                                        
                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            value= name_df_copy.values.tolist()[0]
            mycursor.execute(insert_query_mo, value)
            mydb.commit()

            st.success("SUCCESSFULLY MODIFIED THE TABLE")
            st.dataframe(name_df_copy)
        
        st.divider()



elif options == "Remove":
    
    mydb = mysql.connector.connect(host ='localhost',user='root',password='7ApriL@2002',database='bizcard')
    mycursor=mydb.cursor()

    col1,col2= st.columns(2)
    with col1:

        query1 = "SELECT name FROM card_details"

        mycursor.execute(query1)
        table1 = mycursor.fetchall()
        mydb.commit()

        total_names=[]

        for i in table1:
            total_names.append(i[0])

        all_names = st.selectbox("Select the Name which you want to Remove", total_names)

    if all_names:

        st.write(f"Selected Name : {all_names}")
        st.write("")

        click = st.button("Delete Record")

        if click:
            mycursor.execute(f"DELETE FROM card_details WHERE name = '{all_names}' ")
            mydb.commit()
            
            st.warning("REMOVED SUCCESFULLY")
            mycursor.execute("SELECT * FROM card_details")
            tab = mycursor.fetchall()
            mydb.commit()
            df_deleted = pd.DataFrame(tab, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "MOBILE", "EMAIL", "COMPANY_URL", "ADDRESS", "PINCODE", "IMAGE"))

            st.dataframe(df_deleted)

