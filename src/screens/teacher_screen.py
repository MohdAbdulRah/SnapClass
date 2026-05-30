import streamlit as st 
from src.ui.base_layout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.database.db import check_teacher_username,create_teacher,login_teacher,get_teacher_subjects
from src.components.dialog_create_subject import create_subject_dialog
from src.components.subject_card import subject_card
import time
from src.database.db import get_attendance_for_teacher
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime

import pandas as pd

from src.database.config import supabase


from src.components.dialog_voice_attendance import voice_attendance_dialog
def teacher_screen():
    st.markdown("""
      <style>
       h2{
         color:black !important;    
         font-weight:300 !important;     
       }
      </style>
    """,unsafe_allow_html=True)
    style_base_layout()
    style_background_dashboard()
    if "teacher_data" in st.session_state:
        teacher_dashboard()
        return
    elif 'teacher_login_type' not in st.session_state:
        st.session_state['teacher_login_type'] = 'teacher_login'
    match st.session_state['teacher_login_type']:
        case 'teacher_login':
            teacher_screen_login()
        case 'teacher_register':
             teacher_screen_register()
        case None:
             teacher_screen_register()
    
def teacher_login(username,password):
    if not username or not password:
        return False
    teacher = login_teacher(username,password)
    if teacher:
       st.session_state["role"] = "teacher"
       st.session_state['teacher_data'] = teacher
       st.session_state["is_logged_in"] = True
       return True
    return False
       
def teacher_dashboard():
    teacher_data = st.session_state["teacher_data"]
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1:
       header_dashboard()
    with c2:
       if st.button("Logout",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
           st.session_state['is_logged_in'] = False
           del st.session_state.teacher_data
           st.rerun()
    st.subheader(f"""Welcome {teacher_data["name"]}""")

    st.space()

    tab1,tab2,tab3 = st.columns(3)
    if "current_teacher_tab" not in st.session_state:
        st.session_state["current_teacher_tab"] = "take_attendance"
    with tab1:
        type1 = "primary" if st.session_state["current_teacher_tab"] == "take_attendance" else "tertiary"
        if st.button('Take Attendance',type=type1,width='stretch',icon=":material/ar_on_you:"):
            st.session_state["current_teacher_tab"] = "take_attendance"
            st.rerun()
    with tab2:
        type2 = "primary" if st.session_state["current_teacher_tab"] == "manage_subjects" else "tertiary"
        if st.button('Manage Subjects',type=type2,width='stretch',icon=":material/book_ribbon:"):
            st.session_state["current_teacher_tab"] = "manage_subjects"
            st.rerun()
    with tab3:
        type3 = "primary" if st.session_state["current_teacher_tab"] == "attendance_records" else "tertiary"
        if st.button('Attendance Records',type=type3,width='stretch',icon=":material/cards_stack:"):
            st.session_state["current_teacher_tab"] = "attendance_records"
            st.rerun()

    st.divider()
    if st.session_state["current_teacher_tab"] == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state["current_teacher_tab"] == "manage_subjects":
        teacher_tab_manage_subjects()
    else:
        teacher_tab_attendance_records()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)




def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)


    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]
            def share_btn():
                if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                    share_subject_dialog(sub['name'], sub['subject_code'])
                st.space()

            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats=stats,
                footer_callback=share_btn
            )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")



def teacher_tab_attendance_records():
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N'A",
            "Subject": r['subjects']['name'],
            "Subject Code":r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })


    df = pd.DataFrame(data)



    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count =('is_present', 'count')
        ).reset_index()

    )

    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str) + " /"
        + summary['Total_Count'].astype(str) + ' Students'
    )

    display_df = ( summary.sort_values(by='ts_group' ,ascending=False)
                  [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
                  )
    
    st.dataframe(display_df, width='stretch', hide_index=True)

def register_teacher(teacher_username,teacher_name,teacher_password,teacher_confirm_password):
    if not teacher_username or not teacher_password or not teacher_name:
        return False,"All Fields Are Required"
    if check_teacher_username(teacher_username):
        return False,"Username Already Exists"
    if teacher_password != teacher_confirm_password:
        return False,"Password and Confirm Passowrd are not matching"
    try:
        create_teacher(teacher_username,teacher_password,teacher_name)
        return True,"SuccessFully Created User!! Login Now"
    except Exception as e:
        return False,f"UnExpected Error {e}"

def teacher_screen_login():
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1:
       header_dashboard()
    with c2:
       if st.button("Go Back to Home",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
           st.session_state['login_type'] = None
           st.rerun()
    st.header("Login Using Password",text_alignment='center')
    st.space()
    st.space()
    teacher_username = st.text_input("Enter Username",placeholder="ananyaRoy")
    teacher_password = st.text_input("Enter Password",type='password',placeholder='Enter Password')
    st.divider()
    btncl1,btncl2 = st.columns(2,gap='small')
    with btncl1:
        if st.button("Login",key='lginscreenbtn',shortcut='control+enter',icon=":material/passkey:",width='stretch'):
            if teacher_login(teacher_username,teacher_password):
                st.toast("Welcome BAck",icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Credentials")
    with btncl2:
        if st.button("Register Instead",key='registerBtn',icon=":material/person_add:",width='stretch',type='primary'):
            st.session_state['teacher_login_type'] = 'teacher_register'
            st.rerun()




def teacher_screen_register():
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1:
       header_dashboard()
    with c2:
       if st.button("Go Back to Home",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
           st.session_state['login_type'] = None
           st.rerun()
    st.header("Register Your Teacher Profile",text_alignment='center')
    st.space()
    st.space()
    teacher_username = st.text_input("Enter Username",placeholder="ananyaRoy")
    teacher_name = st.text_input("Enter Your Name",placeholder="Ananya Roy")
    teacher_password = st.text_input("Enter Password",type='password',placeholder='Enter Password')
    teacher_confirm_password = st.text_input("Confirm Your Password",type='password',placeholder='ReEnter Password')
    st.divider()
    btncl1,btncl2 = st.columns(2,gap='small')
    with btncl1:
        if st.button("Register Now",key='registerBtn',icon=":material/person_add:",shortcut='control+enter',width='stretch'):
            success,message = register_teacher(teacher_username,teacher_name,teacher_password,teacher_confirm_password)
            if success:
                st.success(message)
                time.sleep(2)
                st.session_state['teacher_login_type'] = 'teacher_login'
                st.rerun()
            else:
                st.error(message)
    with btncl2:
        if st.button("Login Instead",key='lginscreenbtn',icon=":material/passkey:",width='stretch',type='primary'):
            st.session_state['teacher_login_type'] = 'teacher_login'
            st.rerun()




