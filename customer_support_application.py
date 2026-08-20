import streamlit as st
import pandas as pd
import numpy as  np
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="Customer Support",
    page_icon="https://cdn-icons-png.flaticon.com/128/9119/9119160.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_data():
  df=pd.read_csv("customer_support.csv")
  return df

data=load_data()

st.title("🎧 Customer Support Analytics")
st.write("Analyze customer issues, support performance,"
          "customer satisfaction and resolution time.")

st.divider()


# Create separate clean_dataset
clean_data =data.copy()

# Handle missing values
clean_data["Customer_Name"]=clean_data["Customer_Name"].fillna("New Customer")
clean_data["Message_Device"]=clean_data["Message_Device"].replace(to_replace=np.nan,value="Mobile")
clean_data["Customer_Sentiment"]=clean_data["Customer_Sentiment"].ffill()
clean_data["Customer_Specific_Problem"]=clean_data["Customer_Specific_Problem"].bfill()
clean_data["Priority"]=clean_data["Priority"].ffill()
    

st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Use the filters below to explore customer support data.")

st.sidebar.divider()


with st.sidebar.expander("🎫 Ticket Filters"):
    clean_data["Ticket_Created_Date"]=pd.to_datetime(clean_data["Ticket_Created_Date"],errors="coerce")

    min_date=clean_data["Ticket_Created_Date"].min()
    max_date=clean_data["Ticket_Created_Date"].max()

    date_range=st.date_input("📅 Ticket Created Date",value=(min_date,max_date),
                                min_value=min_date,
                                max_value=max_date,
                                key="date_range")

    clean_data["Response_Time_Hours"]=pd.to_numeric(clean_data["Response_Time_Hours"],errors="coerce")

    min_response=float(clean_data["Response_Time_Hours"].min())
    max_response=float(clean_data["Response_Time_Hours"].max())

    response_range=st.slider("⏱️ Response Time (Hours)",value=(min_response,max_response),
                                    min_value=min_response,
                                    max_value=max_response)

    filter_df=clean_data.copy()

    if len(date_range)==2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])

        filter_df = filter_df[
            (filter_df["Ticket_Created_Date"] >= start_date)&(filter_df["Ticket_Created_Date"] <= end_date)]

    filter_df = filter_df[
        (filter_df["Response_Time_Hours"] >= response_range[0]) &
        (filter_df["Response_Time_Hours"] <= response_range[1])
    ]


    st.write("Tickets")
    priority=st.multiselect("🚨 Priority",
                                    clean_data["Priority"].unique(),
                                    key="priority")

    customer_issue=st.multiselect("⚠️ Issue",
                                        clean_data["Customer_Issue"].unique(),
                                        key="customer_issue")

    customer_type=st.multiselect("Customer Type",
                                        clean_data["Customer_Type"].unique(),
                                        key="customer_type")

with st.sidebar.expander("Customer Filters"):
    st.subheader("Customer Filters")

    region=st.multiselect("🌍 Region :",
                                clean_data["Customer_Region"].unique(),
                                key ="region")

    department=st.multiselect("🏢 Department :",
                                    clean_data["Department"].unique(),
                                    key="department")
    sentiment=st.multiselect("😊 Sentiment",clean_data["Customer_Sentiment"].unique(),
                                            key="sentiment")

    



if region:
    filter_df=filter_df[filter_df["Customer_Region"].isin(region)]
    
if department:
    filter_df=filter_df[filter_df["Department"].isin(department)]

if priority:
    filter_df=filter_df[filter_df["Priority"].isin(priority)]

if customer_issue:
    filter_df=filter_df[filter_df["Customer_Issue"].isin(customer_issue)]

if sentiment:
    filter_df=filter_df[filter_df["Customer_Sentiment"].isin(sentiment)]

if customer_type:
    filter_df=filter_df[filter_df["Customer_Type"].isin(customer_type)]

if st.sidebar.button("🔄 Reset Filters"):
    st.rerun()

st.sidebar.divider()

st.sidebar.caption("🎧 Customer Support Analytics")


tab1,tab2,tab3=st.tabs(["Dashboard","Insight","Raw Data"])
with tab1:
    dash_col1, dash_col2, dash_col3, dash_col4,dash_col5=st.columns(5)
    with dash_col1:
        st.metric("🎫 Total Tickets ",f"{len(filter_df)} ")

    with dash_col2:
        st.metric("👥 Customers ",f"{filter_df["Customer_Name"].nunique()} ")

    with dash_col3:
        high_priority = (
            filter_df["Priority"]
            .astype(str)
            .str.lower()
            .eq("high")
            .sum())
        st.metric(
            "🚨 High Priority",
            f"{high_priority:.2f}")

    with dash_col4:
        st.metric("⭐ Satisfaction",f"{filter_df["Customer_Satisfaction"].mean():.2f}%")

    with dash_col5:
        avg_response = filter_df["Response_Time_Hours"].mean()
        st.metric( "⏱️ Avg Response",f"{avg_response:.2f} hrs")

    st.subheader("📊 Support Performance",text_alignment="center")

    column1,column2=st.columns(2)
    with column1:

        st.subheader("⏱️ Department Response ",text_alignment="center")
        issue=filter_df.groupby("Department")["Response_Time_Hours"].mean().sort_values().head(10)

        fig1,ax1=plt.subplots(figsize=(7,6),facecolor="#FFDADA")
        ax1.set_title(
        "Average Response Time by Department",
        fontsize=16,
        fontweight="bold")
        ax1.set_xlabel("Department",)
        ax1.set_ylabel("Average Response Time")

        ax1.bar(issue.index,
            issue.values,color="#FF788D")
        
        plt.xticks(rotation=45)
        plt.grid(axis="y")
        plt.gca().set_axisbelow(True)
        plt.tight_layout()
        st.pyplot(fig1)

    with column2:
        st.subheader("📅 Response Time Trend",text_alignment="center")
        time=filter_df.groupby(filter_df["Ticket_Created_Date"].dt.date)["Response_Time_Hours"].mean().sort_values().head(10)
        fig2,ax2=plt.subplots(figsize=(7,6),facecolor="#F9F0E0")
        ax2.set_title("Response Time Trend",fontsize=16,fontweight="bold")
        ax2.set_xlabel("Ticket Created date")
        ax2.set_ylabel("Response Time")
        ax2.plot(time.index,time.values,marker="H",mfc="#007979",ms=10)
        plt.xticks(rotation=45)
        plt.grid()
        plt.gca().set_axisbelow(True)
        plt.tight_layout()
        st.pyplot(fig2)

    st.divider()
    st.subheader("👥 Customer & Issue Analysis",text_alignment="center")

    c1,c2=st.columns(2)
    with c1:
        st.subheader("🌟 Top 5 Customers with Most Issues",text_alignment="center")

        top_customers =(filter_df["Customer_Name"].value_counts().head(5))

        fig3, ax3 = plt.subplots(figsize=(7, 6))
        colors=["#BD4444","#124D1C","#E4B028","#458393","#B49292"]
        ax3.pie(
            top_customers.values,
            labels=top_customers.index,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90
            )

        ax3.set_title(
            "Top 5 Customers with Most Issues",fontsize=16,fontweight="bold")
        plt.legend()
        plt.tight_layout()
        st.pyplot(fig3)

    with c2:
        st.subheader("📌 Top 5 Specific Problem")
        problem=filter_df.groupby("Customer_Specific_Problem")["Contact_Attempt_Count"].mean().sort_values(ascending=False).head(5)
        fig4,ax4=plt.subplots(figsize=(7,6),facecolor="#FFF2DB")
        ax4.set_title("Top 5 Problem")
        ax4.set_ylabel("Specific Problem")
        ax4.set_xlabel("Contact attempt")
        ax4.barh(problem.index,
                 problem.values,color="#B2054C")
        plt.xticks([1,2,3,4,5,6,7])
        plt.grid(linestyle="--",alpha=0.6)
        plt.gca().set_axisbelow(True)
        plt.tight_layout()
        st.pyplot(fig4)

    st.divider()
    st.subheader("📈 Relationship Analysis",text_alignment="center") 

     
    first,second=st.columns(2)
    with first:
        st.subheader("⏱️ Response Time vs Customer Satisfaction")

        fig5, ax5 = plt.subplots(figsize=(7, 6),facecolor="#FFF1D1")

        ax5.scatter(
            filter_df["Response_Time_Hours"],
            filter_df["Customer_Satisfaction"],
            alpha=0.6,color="#450C3F")

        ax5.set_title(
            "Response Time vs Customer Satisfaction",fontsize=16,fontweight="bold")

        ax5.set_xlabel("Response Time (Hours)")
        ax5.set_ylabel("Customer Satisfaction")

        ax5.grid(linestyle="--",alpha=0.3)

        plt.tight_layout()

        st.pyplot(fig5)

    with second:
        st.subheader("🛍️ Product Service Analysis",text_alignment="center")
        fig6,ax6=plt.subplots(figsize=(7,6),facecolor="#F3E4C9")
        ax6.hist(filter_df["Product_Service"],color="#BA5A5A")
        ax6.set_title("Product Service",fontsize=16,fontweight="bold")
        ax6.set_xlabel("Product Service")
        ax6.set_ylabel("Customers")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.grid()
        plt.gca().set_axisbelow(True)
        st.pyplot(fig6)




    if filter_df.empty:
        st.warning("⚠️ No clean_data available for the selected filters.")

    st.divider()
    

    st.subheader("📥 Export Data")

    st.caption(
        "Download the currently filtered customer support data."
    )
    csv = filter_df.to_csv(index=False)

    st.download_button(
        "📥 Download Filtered clean_Data",
        csv,
        "filtered_customer_support.csv",
        "text/csv"
    )

with tab2:
    st.subheader("🧠 Customer Support Insights")
    st.caption(
        "Key findings from the selected customer support data."
    )

    st.divider()
    if filter_df.empty:

        st.warning("⚠️ No data available for the selected filters.")

    else:
        
        total_ticket = len(filter_df)

        avg_response = filter_df["Response_Time_Hours"].mean()

        avg_satisfaction = filter_df["Customer_Satisfaction"].mean()

        high_priority = (
            filter_df["Priority"]
            .astype(str)
            .str.lower()
            .eq("high")
            .sum()
        )

        # Top Customer
        customer = filter_df["Customer_Name"].value_counts()

        top_customer = customer.index[0]
        customer_count = customer.iloc[0]

        # Top Issue
        issue = filter_df["Customer_Specific_Problem"].value_counts()

        top_issue = issue.index[0]
        issue_count = issue.iloc[0]


        #Used device 
        device = filter_df["Message_Device"].value_counts()

        top_device = device.index[0]
        device_count = device.iloc[0]

        repeat_contact = filter_df[ filter_df["Contact_Attempt_Count"] > 1]

        repeat_count = len(repeat_contact)

        repeat_percentage = (
            repeat_count / len(filter_df) * 100
        )
        
        # Department Response
        dept_response = (
            filter_df.groupby("Department")["Response_Time_Hours"]
            .mean()
            .sort_values(ascending=False))

        slow_dept = dept_response.index[0]
        slow_time = dept_response.iloc[0]

        sentiment = filter_df["Customer_Sentiment"].value_counts()

        top_sentiment = sentiment.index[0]
        sentiment_count = sentiment.iloc[0]


        knowledge = filter_df["Knowledge_Base_Used"].value_counts()

        top_knowledge = knowledge.index[0]
        knowledge_count = knowledge.iloc[0]


        st.subheader("📊 Overall Performance")


        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"""
                ⏱️ **Response Time**

                Average response time is **{avg_response:.2f} hours**.

                **{slow_dept}** has the highest average response
                time of **{slow_time:.2f} hours**.
                """
            )

        with col2:
            st.warning(
                f"""
                🚨 **Priority Tickets**

                There are **{high_priority} high priority tickets**
                in the selected data.

                These tickets need faster attention from the
                support team.
                """
            )


        st.subheader("👥 Customer & Issue Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.success(
                f"""
                👤 **Top Customer**

                **{top_customer}** has the highest number of
                support tickets with **{customer_count} issues**.

                This customer may require more focused support.
                """
            )

        with col2:
            st.error(
                f"""
                🛠️ **Most Reported Issue**

                **{top_issue}** is the most common customer problem
                with **{issue_count} occurrences**.

                This issue can be investigated for a permanent
                solution.
                """
            )

        st.subheader("📱 Device & Customer Sentiment")

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"""
                📱 **Most Used Device**

                Most customers used **{top_device}** to create
                their support tickets.

                Total **{device_count} tickets** came from this device.
                """
            )

        with col2:
            st.success(
                f"""
                😊 **Customer Sentiment**

                Most customers have **{top_sentiment}** sentiment.

                This sentiment is found in **{sentiment_count} tickets**.
                """)

        st.subheader("🔁 Contact Attempt Analysis")

        st.warning(
            f"""
            🔁 **Repeat Contact**

            **{repeat_count} tickets** needed more than one
            contact attempt.

            This is around **{repeat_percentage:.1f}%** of the
            selected tickets.

            More contact attempts can mean that some customer
            issues are not getting solved in the first contact.
            Improving first-contact resolution can help reduce
            repeated support work.
            """
        )
        
        st.subheader("⭐ Customer Satisfaction")

        st.write(
            f"""
            The average customer satisfaction score is
            **{avg_satisfaction:.2f}**.

            Response time and customer satisfaction can be compared
            to understand the support performance and identify
            possible improvement areas.
            """
        )

        st.info(
                f"""
                📚 **Knowledge Base**                                     
                 **{top_knowledge}** was used the most for customer issues.
            
                It was used in **{knowledge_count} tickets**.
                This knowledge base can be improved by adding more
                solutions and information about common customer problems.
                """)
                        

        st.divider()

        st.subheader("🎯 Final Insight")

        st.write(
            f"""
            The selected data contains **{total_ticket} support tickets**
            with an average response time of **{avg_response:.2f} hours**.

            The analysis shows that **{top_issue}** is the most common
            customer issue, while **{slow_dept}** has the highest
            average response time.

            These findings can help the support team improve response
            efficiency, focus on repeated customer problems and
            provide better customer service.
            """
        )


with tab3:
    st.header("🗃️ Dataset & Data Profiling")

    st.caption(
        "Explore dataset structure, missing values and statistics."
    )
    st.header("🗃️ Main dataset")
    st.dataframe(data)
        
   
    st.divider()

    st.header("🧹 Analysis Missing Values")

    total_sum=data.isna().sum().sum()

    shape=data.shape[0]*data.shape[1]

    percentage=(total_sum / shape)*100


    col1,col2,col3,col4=st.columns(4)
    
    with col1:
        st.metric("Total dataset Rows",f"{data.shape[0]}")

    with col2:
        st.metric("Total dataset Columns",f"{data.shape[1]}")
        
    with col3:
        st.metric("Total Missing Values",f"{total_sum}")

    with col4:
        st.metric("Percentage of Missing values",f"{percentage:.2f}")

    
    st.divider()
    

    st.header("🧪 data Profiling Studio")
    col1,col2,col3,col4,col5 = st.columns(5)

    col1.metric("📊 Rows", data.shape[0])
    col2.metric("📋 Columns ",data.shape[1])
    col3.metric("🔢 Numeric Columns", data.select_dtypes("number").shape[1])
    col4.metric("🔤 Text Columns",data.select_dtypes("object").shape[1])
    col5.metric("🧿 Duplicates Values :",data.duplicated().sum().sum())


    for_tab1, for_tab2, for_tab3, for_tab4, for_tab5, for_tab6 = st.tabs([
        "📐 Shape",
        "📋 Columns",
        "🔤 Dtype",
        "🔢 Index",
        "📦 Values",
        "ℹ️ Info"
    ])

    with for_tab1:
        st.write(data.shape)

    with for_tab2:
        st.write(data.columns)

    with for_tab3:
        st.write(data.dtypes)

    with for_tab4:
        st.write(data.index)

    with for_tab5:
        st.write(data.values)

    with for_tab6:
        import io
        buffer = io.StringIO()
        data.info(buf=buffer)
        st.text(buffer.getvalue())

    st.subheader("📈 Statistical Summary")

    st.dataframe(data.describe())

    unique_data = pd.DataFrame({"Column": data.columns,"Unique Values": [
        data[col].nunique()
        for col in data.columns
    ]
    })
   
    st.subheader("🔎 Unique Values")
    st.dataframe(unique_data)

    memory = data.memory_usage(deep=True).sum() / 1024**2

    st.metric(
        "💾 Memory Usage",
        f"{memory:.2f} MB"
    )