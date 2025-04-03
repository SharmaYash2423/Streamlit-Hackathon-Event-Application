import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from PIL import Image, ImageFilter, ImageEnhance
import io
import base64
import random
import os
import re
from datetime import datetime, timedelta
from collections import Counter

# Set page configuration
st.set_page_config(
    page_title="Hackathon Event Analysis",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make the app visually appealing
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4527A0;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #7E57C2;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #5E35B1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .chart-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .insights-text {
        background-color: #d92329;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        display: flex;
        width: 100%;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #9575CD;
        border-radius: 4px 4px 0px 0px;
        flex: 1;
        padding-top: 10px;
        padding-bottom: 10px;
        text-align: center;
        justify-content: center;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: black;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("<h1 class='main-header'>Hackathon Event Analysis Dashboard</h1>", unsafe_allow_html=True)
    
    # Tabs for different sections
    tabs = st.tabs(["🏠 Home", "📊 Data Generation", "📈 Analytics Dashboard", "💬 Feedback Analysis", "🖼️ Image Gallery"])
    
    with tabs[0]:
        show_home()
        
    with tabs[1]:
        data = generate_dataset_page()
        
    with tabs[2]:
        if 'hackathon_data' in st.session_state:
            analytics_dashboard(st.session_state.hackathon_data)
        else:
            st.warning("Please generate or upload data in the 'Data Generation' tab first!")
            
    with tabs[3]:
        if 'hackathon_data' in st.session_state:
            feedback_analysis(st.session_state.hackathon_data)
        else:
            st.warning("Please generate or upload data in the 'Data Generation' tab first!")
            
    with tabs[4]:
        image_gallery_and_processing()

def show_home():
    st.markdown("<h2 class='sub-header'>Welcome to Hackathon Event Analysis!</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### :grey[About This Dashboard]
        
        This interactive dashboard provides comprehensive analysis and insights for a 3-day hackathon event
        across 5 domains with 350 participants. Explore data visualizations, participant feedback, and event images.
        
        ### :grey[Features:]
        
        - :red[**Data Generation**]: Create a synthetic dataset with 350 participants
        - :green[**Analytics Dashboard**]: 8 different visualizations with interactive filters
        - :blue[**Feedback Analysis**]: Word clouds and sentiment analysis by domain
        - :orange[**Image Gallery**]: Day-wise image display with custom processing options
        """)
        
    with col2:
        st.image("https://media.istockphoto.com/id/1484758991/photo/hackathon-concept-the-meeting-at-the-white-office-table.jpg?s=612x612&w=0&k=20&c=ifl2F6QptCk87wh82yIX7HLILdvmoMdJeB92zr4BR6o=", 
                 use_column_width=True)
    
    st.markdown("""
    ### :grey[How to Use]
    
    1. Start by generating a dataset in the **Data Generation** tab
    2. Explore visualizations in the **Analytics Dashboard** tab
    3. Analyze participant feedback in the **Feedback Analysis** tab
    4. View and process event images in the **Image Gallery** tab
    
    Navigate through the tabs above to get started!
    """)

def generate_dataset_page():
    st.markdown("<h2 class='sub-header'>Dataset Generation</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Generate a synthetic dataset for 350 hackathon participants across 3 days and 5 domains.
        The dataset includes participant details, event participation data, and feedback.
        """)
        
        # User inputs for customization
        num_participants = st.slider("Number of participants", 50, 500, 350)
        
        domains = st.multiselect(
            "Select Hackathon Domains",
            ["Web Development", "Mobile App Development", "AI/ML", "Blockchain", "IoT", "Cybersecurity", "Game Development", "Data Science"],
            ["Web Development", "Mobile App Development", "AI/ML", "Blockchain", "IoT"]
        )
        
        if len(domains) < 1:
            st.error("Please select at least one domain")
            return None
            
        # States selection with default values
        all_states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat", 
            "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", 
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        
        # Default selection of 10 states
        default_states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Uttar Pradesh", 
                         "Gujarat", "Telangana", "West Bengal", "Rajasthan", "Punjab"]
        
        selected_states = st.multiselect(
            "Select States (for participant distribution)",
            all_states,
            default_states
        )
        
        seed = st.number_input("Random Seed (for reproducibility)", min_value=0, max_value=9999, value=42)
        
    with col2:
        st.markdown("### Dataset Preview")
        if st.button("Generate Dataset", type="primary", use_container_width=True):
            with st.spinner("Generating dataset..."):
                data = generate_dataset(num_participants, domains, selected_states, seed)
                st.session_state.hackathon_data = data
                st.success(f"Successfully generated dataset with {len(data)} participants!")
                
                # Preview the first few rows
                st.dataframe(data.head())
                
                # Provide download link
                csv = data.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="hackathon_data.csv" class="btn">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # Save locally too
                data.to_csv("hackathon_data.csv", index=False)
                st.success("Dataset also saved locally as 'hackathon_data.csv'")
                
    # Option to upload existing dataset
    st.markdown("### Or Upload Existing Dataset")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.session_state.hackathon_data = data
        st.success(f"Successfully loaded dataset with {len(data)} entries!")
        st.dataframe(data.head())
    
    return st.session_state.get('hackathon_data', None)

def generate_dataset(num_participants, domains, states, seed=42):
    """Generate a synthetic dataset for hackathon participants without using Faker"""
    random.seed(seed)
    np.random.seed(seed)
    
    # Lists of first and last names for generating participant names
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", 
        "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Nancy", 
        "Christopher", "Lisa", "Daniel", "Margaret", "Matthew", "Betty", "Anthony", "Sandra", "Donald", "Ashley", 
        "Mark", "Dorothy", "Paul", "Kimberly", "Steven", "Emily", "Andrew", "Donna", "Kenneth", "Michelle", 
        "Joshua", "Carol", "Kevin", "Amanda", "Brian", "Melissa", "George", "Deborah", "Edward", "Stephanie", 
        "Ronald", "Rebecca", "Timothy", "Laura", "Jason", "Helen", "Jeffrey", "Sharon", "Ryan", "Cynthia", 
        "Rajesh", "Priya", "Sanjay", "Neha", "Vikram", "Ananya", "Arun", "Kavita", "Amit", "Deepika"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", 
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", 
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", 
        "Patel", "Sharma", "Singh", "Kumar", "Shah", "Gupta", "Verma", "Joshi", "Malhotra", "Chopra"
    ]
    
    # List of colleges (unchanged)
    colleges = [
        "IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", "IIT Kharagpur",
        "BITS Pilani", "BITS Hyderabad", "BITS Goa", "NIT Trichy", "NIT Warangal",
        "NIT Surathkal", "Delhi Technological University", "VIT Vellore", "IIIT Hyderabad",
        "Manipal Institute of Technology", "SRM University", "Amrita University", "Thapar University",
        "College of Engineering Pune", "PES University", "SSN College of Engineering",
        "RV College of Engineering", "BMS College of Engineering", "MS Ramaiah Institute of Technology",
        "Jadavpur University", "Anna University", "KIIT University", "LNM Institute of Technology",
        "Chandigarh University", "Amity University", "Lovely Professional University", "Shiv Nadar University"
    ]
    
    # Feedback templates (unchanged)
    positive_feedback = [
        "I loved the {domain} hackathon! The mentors were very helpful.",
        "Great experience in the {domain} event. Would definitely participate again!",
        "The {domain} challenge was tough but rewarding. Learned a lot!",
        "Amazing organization and support at the {domain} track!",
        "Very insightful {domain} hackathon. Made great connections!",
        "Thoroughly enjoyed working on {domain} projects. The workshops were excellent!",
        "Well-structured {domain} challenges. Got valuable industry exposure.",
        "The {domain} event was eye-opening! Can't wait for the next one.",
        "Gained practical knowledge about {domain}. Very beneficial for my career.",
        "Excellent facilities and resources for the {domain} hackathon!"
    ]
    
    neutral_feedback = [
        "The {domain} hackathon was okay. Some aspects could be improved.",
        "Average experience at the {domain} event. Nothing special.",
        "The {domain} track had some good and bad moments.",
        "Decent organization of the {domain} hackathon. Expected more mentorship.",
        "The {domain} challenge was moderately difficult. Internet connection was spotty.",
        "Food could be better at the {domain} event, but overall it was fine.",
        "The {domain} workshops were informative but too short.",
        "Mixed feelings about the {domain} track. Some judges seemed biased.",
        "The {domain} hackathon schedule was too tight. Barely had time to complete.",
        "Moderate learning experience in {domain}. Not sure if I'll participate again."
    ]
    
    negative_feedback = [
        "The {domain} hackathon was disappointing. Poor organization.",
        "Not enough guidance in the {domain} track. Felt lost most of the time.",
        "Too many technical issues during the {domain} challenge.",
        "The {domain} event was overcrowded and noisy. Couldn't focus.",
        "Unclear instructions for the {domain} hackathon. Very frustrating.",
        "The {domain} mentors were rarely available when needed.",
        "The {domain} track was too advanced for beginners. More tutorials needed.",
        "Poor facilities at the {domain} event. No proper rest areas.",
        "The {domain} hackathon was exhausting with minimal benefits.",
        "Didn't learn much from the {domain} workshops. Too basic content."
    ]
    
    # Function to generate random date time between start and end
    def random_date_time(start_date, end_date):
        delta = end_date - start_date
        random_days = random.random() * delta.days
        random_seconds = random.random() * 86400  # 86400 seconds in a day
        return start_date + timedelta(days=random_days, seconds=random_seconds)
    
    # Generate participant data
    data = []
    
    for i in range(1, num_participants + 1):
        participant_id = f"P{i:03d}"
        name = random.choice(first_names) + " " + random.choice(last_names)
        age = random.randint(18, 35)
        gender = random.choice(["Male", "Female", "Other"])
        college = random.choice(colleges)
        state = random.choice(states)
        domain = random.choice(domains)
        day = random.randint(1, 3)
        
        # Generate random registration time
        start_date = datetime(2023, 3, 15)
        end_date = datetime(2023, 3, 15 + day - 1, 23, 59, 59)
        registration_time = random_date_time(start_date, end_date)
        
        time_spent = round(random.uniform(4, 10), 1)  # Hours spent
        
        # Generate feedback based on sentiment distribution
        sentiment = random.choices(
            ["positive", "neutral", "negative"], 
            weights=[0.6, 0.3, 0.1]
        )[0]
        
        if sentiment == "positive":
            feedback = random.choice(positive_feedback).format(domain=domain)
        elif sentiment == "neutral":
            feedback = random.choice(neutral_feedback).format(domain=domain)
        else:
            feedback = random.choice(negative_feedback).format(domain=domain)
            
        # Add some domain-specific keywords to the feedback
        domain_keywords = {
            "Web Development": ["HTML", "CSS", "JavaScript", "React", "frontend", "backend", "API", "responsive"],
            "Mobile App Development": ["Android", "iOS", "Flutter", "React Native", "UI/UX", "mobile", "app"],
            "AI/ML": ["machine learning", "neural networks", "algorithms", "data", "models", "tensorflow", "pytorch"],
            "Blockchain": ["crypto", "smart contracts", "decentralized", "ethereum", "tokens", "web3", "ledger"],
            "IoT": ["sensors", "devices", "connectivity", "embedded", "Arduino", "Raspberry Pi", "automation"],
            "Cybersecurity": ["security", "encryption", "vulnerability", "firewall", "protection", "hacking", "privacy"],
            "Game Development": ["Unity", "Unreal", "gameplay", "graphics", "mechanics", "levels", "characters"],
            "Data Science": ["visualization", "analytics", "big data", "pandas", "prediction", "statistics", "insights"]
        }
        
        if domain in domain_keywords:
            keywords = domain_keywords[domain]
            extra_phrase = f" The {random.choice(keywords)} component was particularly interesting."
            feedback += extra_phrase
        
        # Project completion status
        project_completion = random.randint(60, 100) if sentiment != "negative" else random.randint(30, 85)
        
        data.append({
            "Participant_ID": participant_id,
            "Name": name,
            "Age": age,
            "Gender": gender,
            "College": college,
            "State": state,
            "Domain": domain,
            "Day": day,
            "Registration_Time": registration_time,
            "Time_Spent": time_spent,
            "Project_Completion": project_completion,
            "Feedback": feedback
        })
    
    return pd.DataFrame(data)

def analytics_dashboard(data):
    st.markdown("<h2 class='sub-header'>Analytics Dashboard</h2>", unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.markdown("### Filters")
    
    # Domain filter
    all_domains = data['Domain'].unique().tolist()
    selected_domains = st.sidebar.multiselect(
        "Select Domains",
        all_domains,
        default=all_domains
    )
    
    # State filter
    all_states = data['State'].unique().tolist()
    selected_states = st.sidebar.multiselect(
        "Select States",
        all_states,
        default=all_states[:5] if len(all_states) > 5 else all_states
    )
    
    # College filter
    all_colleges = data['College'].unique().tolist()
    selected_colleges = st.sidebar.multiselect(
        "Select Colleges",
        all_colleges,
        default=all_colleges[:5] if len(all_colleges) > 5 else all_colleges
    )
    
    # Day filter
    all_days = sorted(data['Day'].unique().tolist())
    selected_days = st.sidebar.multiselect(
        "Select Days",
        all_days,
        default=all_days
    )
    
    # Filter data based on selections
    filtered_data = data[
        (data['Domain'].isin(selected_domains)) &
        (data['State'].isin(selected_states)) &
        (data['College'].isin(selected_colleges)) &
        (data['Day'].isin(selected_days))
    ]
    
    if filtered_data.empty:
        st.warning("No data available with the selected filters. Please adjust your selection.")
        return
    
    # Show filter summary
    st.markdown(f"""
    <div class='insights-text'>
        <b>Current Filters:</b> Showing data for {len(filtered_data)} participants from 
        {len(selected_domains)} domains, {len(selected_states)} states, 
        {len(selected_colleges)} colleges, across {len(selected_days)} days.
    </div>
    """, unsafe_allow_html=True)
    
    # Create visualizations in a grid layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='sub-header'>Domain-wise Distribution</h3>", unsafe_allow_html=True)
        domain_counts = filtered_data['Domain'].value_counts().reset_index()
        domain_counts.columns = ['Domain', 'Count']
        
        fig = px.pie(
            domain_counts, 
            names='Domain', 
            values='Count',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("<h3 class='sub-header'>Day-wise Participation</h3>", unsafe_allow_html=True)
        day_counts = filtered_data['Day'].value_counts().sort_index().reset_index()
        day_counts.columns = ['Day', 'Count']
        
        fig = px.bar(
            day_counts,
            x='Day',
            y='Count',
            text='Count',
            color='Count',
            color_continuous_scale='Viridis',
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='sub-header'>State-wise Distribution</h3>", unsafe_allow_html=True)
        
        state_counts = filtered_data['State'].value_counts().reset_index()
        state_counts.columns = ['State', 'Count']
        state_counts = state_counts.sort_values('Count', ascending=True).tail(10)
        
        fig = px.bar(
            state_counts,
            y='State',
            x='Count',
            orientation='h',
            color='Count',
            color_continuous_scale='Plasma',
            text='Count'
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis={'categoryorder':'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("<h3 class='sub-header'>Top Colleges</h3>", unsafe_allow_html=True)
        
        college_counts = filtered_data['College'].value_counts().reset_index()
        college_counts.columns = ['College', 'Count']
        college_counts = college_counts.sort_values('Count', ascending=False).head(10)
        
        fig = px.bar(
            college_counts,
            x='College',
            y='Count',
            color='Count',
            color_continuous_scale='Viridis',
            text='Count'
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis={'categoryorder':'total descending', 'tickangle': 45}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='sub-header'>Domain Participation by Day</h3>", unsafe_allow_html=True)
        
        domain_day = filtered_data.groupby(['Domain', 'Day']).size().reset_index(name='Count')
        
        fig = px.bar(
            domain_day,
            x='Domain',
            y='Count',
            color='Day',
            barmode='group',
            text='Count'
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis={'tickangle': 45}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("<h3 class='sub-header'>Gender Distribution</h3>", unsafe_allow_html=True)
        
        gender_counts = filtered_data['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        
        fig = px.pie(
            gender_counts,
            names='Gender',
            values='Count',
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='sub-header'>Age Distribution</h3>", unsafe_allow_html=True)
        
        fig = px.histogram(
            filtered_data,
            x='Age',
            nbins=20,
            color_discrete_sequence=['#3949AB'],
            opacity=0.8
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            bargap=0.1
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("<h3 class='sub-header'>Project Completion Rate by Domain</h3>", unsafe_allow_html=True)
        
        domain_completion = filtered_data.groupby('Domain')['Project_Completion'].mean().reset_index()
        domain_completion.columns = ['Domain', 'Average Completion Rate']
        
        fig = px.bar(
            domain_completion,
            x='Domain',
            y='Average Completion Rate',
            color='Average Completion Rate',
            text=domain_completion['Average Completion Rate'].round(1),
            color_continuous_scale='RdYlGn',
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis={'tickangle': 45},
            yaxis={'range': [0, 100]}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation heatmap
    st.markdown("<h3 class='sub-header'>Correlation Between Metrics</h3>", unsafe_allow_html=True)
    
    numerical_data = filtered_data[['Age', 'Day', 'Time_Spent', 'Project_Completion']]
    correlation = numerical_data.corr()
    
    fig = px.imshow(
        correlation,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        aspect="auto",
        zmin=-1, zmax=1
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights section
    st.markdown("<h3 class='sub-header'>Key Insights</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        most_popular_domain = filtered_data['Domain'].value_counts().idxmax()
        domain_count = filtered_data['Domain'].value_counts().max()
        domain_percent = (domain_count / len(filtered_data)) * 100
        
        st.markdown(f"""
        <div class='insights-text'>
            <h4>Most Popular Domain</h4>
            <p>{most_popular_domain} with {domain_count} participants ({domain_percent:.1f}% of total)</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        avg_time_spent = filtered_data['Time_Spent'].mean()
        max_time_spent = filtered_data['Time_Spent'].max()
        
        st.markdown(f"""
        <div class='insights-text'>
            <h4>Participation Time</h4>
            <p>Average time spent: {avg_time_spent:.1f} hours<br>
            Maximum time spent: {max_time_spent:.1f} hours</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        avg_completion = filtered_data['Project_Completion'].mean()
        completion_gt_90 = (filtered_data['Project_Completion'] > 90).sum()
        completion_gt_90_pct = (completion_gt_90 / len(filtered_data)) * 100
        
        st.markdown(f"""
        <div class='insights-text'>
            <h4>Project Completion</h4>
            <p>Average completion rate: {avg_completion:.1f}%<br>
            Projects with >90% completion: {completion_gt_90} ({completion_gt_90_pct:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)

def feedback_analysis(data):
    st.markdown("<h2 class='sub-header'>Feedback Analysis</h2>", unsafe_allow_html=True)
    
    # Sidebar filters for feedback analysis
    st.sidebar.markdown("### Feedback Filters")
    
    # Domain filter for feedback
    all_domains = data['Domain'].unique().tolist()
    selected_domains_feedback = st.sidebar.multiselect(
        "Select Domains for Feedback",
        all_domains,
        default=all_domains[0] if all_domains else None,
        key="feedback_domains"
    )
    
    if not selected_domains_feedback:
        st.warning("Please select at least one domain for feedback analysis.")
        return
    
    # Word cloud customization
    st.sidebar.markdown("### Word Cloud Settings")
    max_words = st.sidebar.slider("Maximum words in cloud", 50, 200, 100)
    color_theme = st.sidebar.selectbox(
        "Color Theme", 
        ["viridis", "plasma", "inferno", "magma", "cividis", "Blues", "Greens", "Reds"]
    )
    
    # Introduction text
    st.markdown("""
    This section analyzes participant feedback using text mining techniques. 
    The word clouds display frequently occurring terms in feedback, with larger words indicating higher frequency.
    """)
    
    # Creating tabs for each selected domain
    if len(selected_domains_feedback) > 1:
        domain_tabs = st.tabs(selected_domains_feedback)
        
        for i, domain in enumerate(selected_domains_feedback):
            with domain_tabs[i]:
                domain_feedback_analysis(data, domain, max_words, color_theme)
    else:
        domain = selected_domains_feedback[0]
        domain_feedback_analysis(data, domain, max_words, color_theme)
    
    # Common words across domains
    if len(selected_domains_feedback) > 1:
        st.markdown("<h3 class='sub-header'>Common Feedback Themes Across Domains</h3>", unsafe_allow_html=True)
        
        # Combine all feedback from selected domains
        combined_feedback = data[data['Domain'].isin(selected_domains_feedback)]['Feedback'].str.cat(sep=' ')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Generate word cloud for combined feedback
            plt.figure(figsize=(10, 6))
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap=color_theme,
                max_words=max_words,
                contour_width=1,
                contour_color='steelblue'
            ).generate(combined_feedback)
            
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(plt)
            
        with col2:
            # Extract and count most common words
            import re
            from collections import Counter
            
            # Common English stopwords
            stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
                         "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
                         'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 
                         'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 
                         'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 
                         'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
                         'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
                         'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
                         'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
                         'with', 'about', 'against', 'between', 'into', 'through', 'during', 
                         'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                         'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 
                         'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 
                         'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
                         'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 
                         'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 
                         "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 
                         've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', 
                         "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 
                         'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 
                         'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', 
                         "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 
                         'wouldn', "wouldn't", 'the', 'was', 'and', 'for', 'would']
            
            # Extract words from feedback
            words = re.findall(r'\b[a-zA-Z]{3,15}\b', combined_feedback.lower())
            words = [word for word in words if word not in stopwords]
            
            # Count word frequencies
            word_counts = Counter(words).most_common(15)
            
            # Display as a bar chart
            word_df = pd.DataFrame(word_counts, columns=['Word', 'Frequency'])
            
            fig = px.bar(
                word_df,
                y='Word',
                x='Frequency',
                orientation='h',
                color='Frequency',
                color_continuous_scale=color_theme,
                text='Frequency'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=10, b=20),
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class='insights-text'>
                <h4>Insight</h4>
                <p>The chart shows the most common meaningful words across all selected domains' feedback, 
                helping to identify overall themes and sentiments.</p>
            </div>
            """, unsafe_allow_html=True)

def domain_feedback_analysis(data, domain, max_words, color_theme):
    """Analyze feedback for a specific domain"""
    domain_data = data[data['Domain'] == domain]
    
    if domain_data.empty:
        st.warning(f"No feedback data available for {domain}.")
        return
    
    # Combine all feedback for this domain
    all_feedback = domain_data['Feedback'].str.cat(sep=' ')
    
    st.markdown(f"<h3 class='sub-header'>Feedback Analysis for {domain}</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Generate and display word cloud
        plt.figure(figsize=(10, 6))
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap=color_theme,
            max_words=max_words,
            contour_width=1,
            contour_color='steelblue'
        ).generate(all_feedback)
        
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        st.pyplot(plt)
        
    with col2:
        # Stats about the feedback
        num_participants = len(domain_data)
        avg_feedback_length = domain_data['Feedback'].str.len().mean()
        
        st.markdown(f"""
        <div class='insights-text'>
            <h4>Feedback Statistics</h4>
            <p>
            Number of participants: {num_participants}<br>
            Average feedback length: {avg_feedback_length:.1f} characters
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple sentiment analysis based on keywords
        positive_keywords = ['loved', 'great', 'amazing', 'excellent', 'insightful', 
                            'enjoyed', 'beneficial', 'helpful', 'rewarding', 'best']
        negative_keywords = ['disappointing', 'poor', 'issues', 'frustrating', 'unclear',
                            'exhausting', 'minimal', 'bad', 'lost', 'overcrowded']
        
        # Count occurrences of positive and negative keywords
        positive_count = sum(domain_data['Feedback'].str.contains(word, case=False).sum() 
                           for word in positive_keywords)
        negative_count = sum(domain_data['Feedback'].str.contains(word, case=False).sum() 
                           for word in negative_keywords)
        
        total_keywords = positive_count + negative_count
        positive_percent = (positive_count / total_keywords * 100) if total_keywords > 0 else 0
        negative_percent = (negative_count / total_keywords * 100) if total_keywords > 0 else 0
        
        # Display sentiment gauge
        st.markdown("<h4>Sentiment Indicator</h4>", unsafe_allow_html=True)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = positive_percent,
            title = {'text': "Positive Sentiment"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "rgb(106, 168, 79)"},
                'steps': [
                    {'range': [0, 30], 'color': "rgb(230, 124, 115)"},
                    {'range': [30, 70], 'color': "rgb(246, 178, 107)"},
                    {'range': [70, 100], 'color': "rgb(106, 168, 79)"}
                ],
            }
        ))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    
    # Display sample feedback
    st.markdown("<h4>Sample Feedback</h4>", unsafe_allow_html=True)
    
    # Get 5 random feedback samples
    if len(domain_data) > 5:
        sample_feedback = domain_data.sample(5)
    else:
        sample_feedback = domain_data
    
    for i, (_, row) in enumerate(sample_feedback.iterrows()):
        st.markdown(f"""
        <div style='padding: 10px; background-color: #d92329; border-radius: 5px; margin-bottom: 10px;'>
            <b>Participant {row['Participant_ID']}</b> (Completion: {row['Project_Completion']}%)<br>
            "{row['Feedback']}"
        </div>
        """, unsafe_allow_html=True)

def image_gallery_and_processing():
    st.markdown("<h2 class='sub-header'>Image Gallery & Processing</h2>", unsafe_allow_html=True)
    
    # Create tabs for Gallery and Processing
    gallery_tab, processing_tab = st.tabs(["🖼️ Event Gallery", "🔧 Image Processing"])
    
    with gallery_tab:
        show_image_gallery()
    
    with processing_tab:
        image_processing()

def show_image_gallery():
    st.markdown("<h3 class='sub-header'>Hackathon Event Gallery</h3>", unsafe_allow_html=True)
    
    # Select day
    day = st.radio("Select Day", ["Day 1", "Day 2", "Day 3"], horizontal=True)
    
    # Domains to show images for
    domains = st.multiselect(
        "Select Domains to Display",
        ["Web Development", "Mobile App Development", "AI/ML", "Blockchain", "IoT"],
        ["Web Development", "Mobile App Development", "AI/ML", "Blockchain", "IoT"]
    )
    
    # Generate placeholder images based on domain and day
    # In a real app, you would use actual event photos
    if domains:
        st.markdown(f"<h4>Images from {day}</h4>", unsafe_allow_html=True)
        
        # Create a grid layout for images
        cols = st.columns(3)
        
        # Dictionary mapping domains to relevant image URLs
        domain_images = {
            "Web Development": [
                "https://img.freepik.com/free-photo/programming-background-with-person-working-with-codes-computer_23-2150010125.jpg?w=740&t=st=1714045118~exp=1714045718~hmac=0db297e2eaf71fe84aad5f0c6f4f8e95c6e4749e60edd02173bc1ba21da65eb0",
                "https://img.freepik.com/free-photo/close-up-image-programer-working-his-desk-office_1098-18707.jpg?w=740&t=st=1714045140~exp=1714045740~hmac=05be58ebcc20d07e4f741237320b44e8541681aa7bbde0b10c3a5985ec35ae8c",
                "https://img.freepik.com/free-photo/rear-view-programmer-working-all-night-long_1098-18697.jpg?w=740&t=st=1714045168~exp=1714045768~hmac=72de24f9e5705399a1d6fb5f3d1ecc166be0149fc5a252e5c2fdbad8b2c98cd9"
            ],
            "Mobile App Development": [
                "https://img.freepik.com/free-vector/app-development-banner_33099-1720.jpg",
                "https://media.istockphoto.com/id/1174690086/photo/software-developer-freelancer-working-at-home.jpg?s=612x612&w=0&k=20&c=loFqul06ggwtkwqSmzZnYfA72Vk7nFQOvDSzAN6YbtQ=",
                "https://lh4.googleusercontent.com/-z2_WPcZpaj3lKM_KpyyklucmrEi7SGyo8RvBJuF2GVYsTMGCRVP7-8_0bQ8_-40PN-P9K8ugGU1T2r-a92qjkndpp1J84I3s2Fyc0a-f0L-dp4V-YpfzOdEuOvDHXUN79vpFUM-q7PI7B7i9pW1CEw"
            ],
            "AI/ML": [
                "https://eu-images.contentstack.com/v3/assets/blt8eb3cdfc1fce5194/bltf3fad4d36b8893e7/662109ea5dcbd66010a70c19/2CND889.jpg?width=1280&auto=webp&quality=95&format=jpg&disable=upscale",
                "https://www.igtsolutions.com/wp-content/uploads/2021/10/ai-featured-img.jpg",
                "https://www.supermomos.com/_next/image?url=https%3A%2F%2Fsupermomos-app-resources-us.s3.amazonaws.com%2Fpublic%2Fsocial_banners%2F1ab33d01-3c39-434a-be4e-3cf85fd8f4ce.png&w=1920&q=75"
            ],
            "Blockchain": [
                "https://fintechweekly.s3.amazonaws.com/article/191/shutterstock_1016393917.jpg",
                "https://bernardmarr.com/wp-content/uploads/2023/05/The-5-Biggest-Problems-With-Blockchain-Technology-Everyone-Must-Know-About-1.jpg",
                "https://www.accesswire.com/imagelibrary/42fbae3c-c412-43bf-a1e5-15073781f7b1/927945/Future_Blockchain_Summit_beauty_shot.jpg"
            ],
            "IoT": [
                "https://online.keele.ac.uk/wp-content/uploads/2024/05/IoT.jpg",
                "https://studyonline.unsw.edu.au/sites/default/files/field/image/KP%20AUS%20UNSW%20Q2%202022%20Skyscraper%20%233%20What%20is%20the%20Internet%20of%20Things%20%28IoT%29-01%201000X667.jpg",
                "https://blog.raxsuite.com/wp-content/uploads/2023/07/IoT-Conference-2023-01.png"
            ]
        }
        
        # Map day to index for different images
        day_idx = {"Day 1": 0, "Day 2": 1, "Day 3": 2}
        
        # Display images for each selected domain
        for i, domain in enumerate(domains):
            if domain in domain_images:
                img_url = domain_images[domain][day_idx[day]]
                col_idx = i % 3
                with cols[col_idx]:
                    st.image(img_url, caption=f"{domain} - {day}", use_column_width=True)
        
    else:
        st.warning("Please select at least one domain to display images.")

def image_processing():
    st.markdown("<h3 class='sub-header'>Custom Image Processing</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    Upload an image to apply various effects and filters. This tool can be used to process and prepare
    hackathon event photos for presentations, reports, or social media.
    """)
    
    # Image upload
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Read the uploaded image
        image = Image.open(uploaded_file)
        
        # Display original image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<h4>Original Image</h4>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)
        
        # Image processing options
        st.markdown("<h4>Image Processing Options</h4>", unsafe_allow_html=True)
        
        # Create two columns for controls
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Basic adjustments
            brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.1)
            contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.1)
            saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
            
        with col2:
            # Filter options
            filter_option = st.selectbox(
                "Apply Filter",
                ["None", "Blur", "Sharpen", "Contour", "Detail", "Edge Enhance", "Emboss", "Grayscale", "Sepia"]
            )
            
            # Add text overlay option
            add_text = st.checkbox("Add Text Overlay")
            if add_text:
                text_content = st.text_input("Text Content", "Hackathon 2023")
                text_size = st.slider("Text Size", 10, 50, 24)
                text_position = st.selectbox("Text Position", ["Top", "Center", "Bottom"])
        
        # Process the image based on selected options
        processed_image = image.copy()
        
        # Apply basic adjustments
        enhancer = ImageEnhance.Brightness(processed_image)
        processed_image = enhancer.enhance(brightness)
        
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(contrast)
        
        enhancer = ImageEnhance.Color(processed_image)
        processed_image = enhancer.enhance(saturation)
        
        # Apply selected filter
        if filter_option == "Blur":
            processed_image = processed_image.filter(ImageFilter.BLUR)
        elif filter_option == "Sharpen":
            processed_image = processed_image.filter(ImageFilter.SHARPEN)
        elif filter_option == "Contour":
            processed_image = processed_image.filter(ImageFilter.CONTOUR)
        elif filter_option == "Detail":
            processed_image = processed_image.filter(ImageFilter.DETAIL)
        elif filter_option == "Edge Enhance":
            processed_image = processed_image.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_option == "Emboss":
            processed_image = processed_image.filter(ImageFilter.EMBOSS)
        elif filter_option == "Grayscale":
            processed_image = processed_image.convert("L").convert("RGB")
        elif filter_option == "Sepia":
            # Implement sepia filter
            width, height = processed_image.size
            pixels = processed_image.load()
            for py in range(height):
                for px in range(width):
                    r, g, b = processed_image.getpixel((px, py))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    if tr > 255: tr = 255
                    if tg > 255: tg = 255
                    if tb > 255: tb = 255
                    pixels[px, py] = (tr, tg, tb)
        
        # Add text overlay if selected
        if add_text:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(processed_image)
            
            # Use default font if custom font isn't available
            try:
                font = ImageFont.truetype("arial.ttf", text_size)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            width, height = processed_image.size
            text_width, text_height = draw.textsize(text_content, font)
            
            if text_position == "Top":
                position = ((width - text_width) // 2, 20)
            elif text_position == "Center":
                position = ((width - text_width) // 2, (height - text_height) // 2)
            else:  # Bottom
                position = ((width - text_width) // 2, height - text_height - 20)
            
            # Add shadow for better visibility
            shadow_offset = max(1, text_size // 15)
            draw.text((position[0] + shadow_offset, position[1] + shadow_offset), text_content, 
                      font=font, fill=(0, 0, 0, 180))
            
            # Draw the main text
            draw.text(position, text_content, font=font, fill=(255, 255, 255, 255))
        
        # Display processed image
        with col2:
            st.markdown("<h4>Processed Image</h4>", unsafe_allow_html=True)
            st.image(processed_image, use_column_width=True)
        
        # Option to download the processed image
        buf = io.BytesIO()
        processed_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="Download Processed Image",
                data=byte_im,
                file_name="processed_hackathon_image.png",
                mime="image/png"
            )
    else:
        # Show demo image if no file is uploaded
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px;'>
            <h4>No Image Uploaded</h4>
            <p>Upload an image to try out the processing features. You can add filters, adjust brightness/contrast, 
            and add text overlays to customize your hackathon images.</p>
            <p>Ideal for preparing images for presentations, social media posts, or event reports.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()