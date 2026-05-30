import streamlit as st 


def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown("""
       <style>
       .header-div{
            align-items: center;
            display: flex;
            flex-direction: column;
            justify-content: center; 
            margin-bottom:3vh;
            margin-top:2vh;  
        }   
        .header-text{
            
               text-align:center;
               color:#E0E3FF;
               font-weight:300 !important;    
                 
        }     
      </style>
    """,unsafe_allow_html=True)
    st.markdown(f"""
     
      <div class="header-div">
      <img src='{logo_url}' style='height:100px;'/>
      <h1 class="header-text">SNAP<br/> CLASS</h1>
      </div>
    """,unsafe_allow_html=True)

def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown("""
       <style>
       .header-div{
            align-items: center;
            display: flex;
            flex-direction: row;
            gap:1vw;
           
        }   
        .header-text{
            
               
               color:#5865F2 !important;
               font-weight:300 !important;    
                 
        }  
        h1{
           font-size:2.0rem !important;        
        }   
      </style>
    """,unsafe_allow_html=True)
    st.markdown(f"""
     
      <div class="header-div">
      <img src='{logo_url}' style='height:90px;'/>
      <h1 class="header-text">SNAP<br/> CLASS</h1>
      </div>
    """,unsafe_allow_html=True)