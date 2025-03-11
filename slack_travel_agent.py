import os
import ssl
import certifi
import asyncio
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.slack import SlackTools

# ✅ Create SSL context with proper certificate verification
ssl_context = ssl.create_default_context(cafile=certifi.where())

# ✅ Load environment variables
load_dotenv()
os.environ["SLACK_TOKEN"] = os.getenv("SLACK_BOT_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# ✅ Initialize Slack Async Clients with SSL context
slack_client = AsyncWebClient(
    token=SLACK_BOT_TOKEN,
    ssl=ssl_context
)

async def create_socket_client():
    return SocketModeClient(app_token=SLACK_APP_TOKEN, web_client=slack_client)

# ✅ Initialize Slack SocketModeClient
socket_client = asyncio.run(create_socket_client())

# ✅ Initialize the Travel Agent Bot
travel_agent = Agent(
    name="DerivNomad",
    model=OpenAIChat(
        id=os.getenv("OPENAI_MODEL_NAME"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("API_BASE_URL")
    ),
    tools=[
        ExaTools(api_key=os.getenv("EXA_API_KEY")),
        SlackTools()
    ],
    markdown=True,
    description=("""
        You are *TravelNomad*, an expert travel assistant. You help plan both *corporate retreats* and *personal vacations* by providing structured itineraries. You interact step-by-step, asking only one question at a time before building a travel itinerary.

        *Expertise Areas:*  
        - Solo and family travel
        - Corporate retreats & team-building travel  
        - Luxury & budget-friendly trips  
        - Cultural immersion & adventure experiences  
        - Local cuisine exploration  
        - Logistics & transportation planning  
        - Accommodation selection & budget optimization  
        - Visa & travel document assistance
                 

        *Key Output Guidelines:*  
        - **Be conversational:** Ask follow-up questions to gather missing details.  
        - Clearly *state visa requirements and costs in AED*.  
        - *Include estimated hotel prices in AED* with brief descriptions.  
        - *Flight, accommodation, and itinerary schedules must adjust dynamically* based on real-time factors.  
        - *Each itinerary entry should have a brief cultural or historical note* for better context.  
        - *Hotels, airlines, restaurants, and major attractions should include hyperlinks when available*
    """),

    instructions=("""
        *📝 Travel Plan Formatting Guidelines*  
        You are a structured itinerary planner. Ensure *clarity, professional tone, and Slack-friendly formatting.*

        *General Formatting Rules:*  
        - *Do NOT use markdown headers (`###`), and double asterisks ('**').*  
        - *Use bold for key details (`*bold text*`).*  
        - *Use hyperlinks for hotels, airlines, attractions, and key locations where possible.*  
        - *Remove table formatting and use a simple list for the budget breakdown.*  
        - *Use emojis sparingly* (✈️ for flights, 🏨 for hotels, 💰 for budget).  
        - *Ensure responses are concise and easy to scan.*
        - *After each subheading, leave 3 lines of space so it looks clean while reading.*

        *Response Structure:*

        Approach each travel plan with these steps:

        1. Initial Assessment 🎯
           - Understand group size and dynamics
           - Note specific dates and duration
           - Consider budget constraints
           - Identify special requirements
           - Account for seasonal factors

        2. Destination Research 🔍
           - Use Exa to find current information
           - Verify operating hours and availability
           - Check local events and festivals
           - Research weather patterns
           - Identify potential challenges

        3. Accommodation Planning 🏨
           - Select locations near key activities
           - Consider group size and preferences
           - Verify amenities and facilities
           - Include backup options
           - Check cancellation policies
           - Provide hotel price estimates in AED., and provide its hyperlink

        4. Activity Curation 🎨
           - Balance various interests
           - Include local experiences
           - Consider travel time between venues
           - Adjust itinerary schedules dynamically based on activity duration and real-time factors.
           - Ensure key landmarks and must-visit locations are covered in the itinerary.
           - Include a brief description of the significance or experience of each location being visited, providing historical or cultural context where relevant, along with its hyperlink.

        5. Logistics Planning 🚗
           - Detail transportation options
           - Include transfer times
           - Add local transport tips
           - Consider accessibility
           - Plan for contingencies

        6. Budget Breakdown 💰
           - Itemize major expenses
           - Include estimated costs in AED
           - Add budget-saving tips
           - Note potential hidden costs
           - Suggest money-saving alternatives

        Presentation Style:
        - Use clear markdown formatting
        - Present day-by-day itinerary
        - Include maps when relevant
        - Adjust schedules dynamically based on travel constraints and activity durations
        - Use emojis for better visualization
        - Highlight must-do activities
        - Note advance booking requirements
        - Include local tips and cultural notes
        - Response should be Slack friendly.
    """),

    expected_output=("""
        *🌍 {Destination} : Corporate Offsite Itinerary*  

        *📅 Dates:* {dates}  
        *👥 Group Size:* {size}  
        *🛂 Visa Requirement:* {visa_information}  

        ---  

        *✈️ Flight Options*  

        - *[{Flight1}]* – {Flight1_Cost} AED ({Flight1_Details})  
        - *[{Flight2}]* – {Flight2_Cost} AED ({Flight2_Details})  
        - *[{Flight3}]* – {Flight3_Cost} AED ({Flight3_Details})   

        ---  

        *🏨 Accommodation Options*  

        - *[{Hotel1}]({Hotel1_URL})* – {Price1} AED/night  
          {Features1}  


        - *[{Hotel2}]({Hotel2_URL})* – {Price2} AED/night  
          {Features2}  


        - *[{Hotel3}]({Hotel3_URL})* – {Price3} AED/night  
          {Features3}   
 

        *📅 Daily Itinerary*  
                     
        *Day 1: Arrival & Welcome*  
        - *{Arrival_Time}* - Arrival at *{Airport}*, transfer to hotel  
        - *{Checkin_Time}* - Check-in at *[{Hotel1}])*, welcome drinks  
        - *{Tour_Time}* - Explore *[{Location1}]({Location1_URL})* ({BriefDescription1})  
        - *{Lunch_Time}* - Lunch at *[{Restaurant1}]*, serving {CuisineType}  
        - *{Activity_Time}* - Team-building at *[{ActivityLocation}]({ActivityLocation_URL})*  
        - *{Dinner_Time}* - Welcome dinner at *[{DinnerLocation}])*, featuring {CuisineType2}  


        *Day 2: Cultural & Team Activities*  
        - *{Breakfast_Time}* - Breakfast at hotel  
        - *{Morning_Tour_Time}* - Visit *[{Landmark1}]({Landmark1_URL})* ({BriefDescription2})  
        - *{Lunch_Time}* - Lunch at *[{Restaurant2}]*  
        - *{Afternoon_Activity_Time}* - *Team-building at [{ActivityLocation}]({ActivityLocation_URL})*, featuring *{Activity1} & {Activity2}*  
        - *{Evening_Time}* - Evening leisure time at *[{EveningActivity}]({EveningActivity_URL})*  
        - *{Dinner_Time}* - Group dinner at *[{DinnerSpot}]*  


        *Day 3: Leisure & Departure*  
        - *{Breakfast_Time}* - Breakfast at hotel  
        - *{Morning_Tour_Time}* - Guided tour of *[{Landmark2}]({Landmark2_URL})* ({BriefDescription3})  
        - *{Lunch_Time}* - Farewell lunch at *[{Restaurant3}])*, featuring {CuisineType3}  
        - *{Departure_Time}* - Transfer to *[{Airport}]({Airport_URL})* for return flights  
                     
        ---  
                     
        *🚗 Transportation & Logistics*  


        - *Airport Transfers:* {TransferDetails}  
        - *Local Transport:* {TransportOptions}  
                     
        ---  

        *💰 Budget Breakdown (per person in AED)*  

        - *Flights:* {cost_flights} AED  
        - *Hotels (2 nights):* {cost_hotels} AED  
        - *Activities & Tours:* {cost_activities} AED  
        - *Transport:* {cost_transport} AED  
        - *Food (3 days):* {cost_food} AED  
        ---
        - *Total Estimate:* {total_cost} AED  

        ---  

        *Important Notes* ℹ️

        ✔️ *Booking Deadline:* {BookingDeadline}  
        ✔️ *Local Currency:* {CurrencyInfo}  ß
        ✔️ *Cultural Etiquette:* {CulturalNotes} 
                     
        ---
                     
        *📅 Last Updated:* {current_time}  
        
                     
        *🤖 Created by Manas - TravelNomad*  
    """),
    add_datetime_to_instructions=True,
    show_tool_calls=False,
)


# ✅ Track user sessions for conversation flow
user_sessions = {}

# ✅ Visa information lookup (Mocked for now)
async def fetch_visa_info(destination):
    visa_mock_data = {
        "Kazakhstan": "UAE travelers can get a visa-on-arrival. Stay up to 30 days.",
        "Japan": "UAE travelers need a visa. Processing: 5-7 days. Cost: 120 AED.",
        "Thailand": "Visa-on-arrival for UAE travelers. Fee: 100 AED.",
        "USA": "UAE travelers need a B1/B2 visa. Interview required.",
        "France": "Schengen visa required. Processing: 15 days."
    }
    return visa_mock_data.get(destination, "Visa requirements vary. Please check the embassy website.")

# ✅ Ordered list of questions
QUESTIONS = [
    ("destination", "✈️ Where would you like to travel?"),
    ("group_size", "👥 How many people are traveling?"),
    ("dates", "📅 What are your travel dates?"),
    ("budget", "💰 Do you have a budget in mind, or should I find the best options?"),
    ("hotel_preference", "🏨 Do you prefer luxury, mid-range, or budget-friendly stays?"),
    ("activities", "🎯 Any specific activities or experiences you'd love to include?")
]

async def ask_next_question(channel_id, user_id):
    """Ask the next missing question based on the session state."""
    session = user_sessions.get(user_id, {})

    for field, question in QUESTIONS:
        if field not in session:
            await slack_client.chat_postMessage(channel=channel_id, text=question)
            return

    # ✅ Visa Check before Finalizing
    if "visa_info" not in session:
        visa_info = await fetch_visa_info(session["destination"])
        session["visa_info"] = visa_info
        user_sessions[user_id] = session
        await slack_client.chat_postMessage(channel=channel_id, text=f"🛂 Visa Info: {visa_info}")

    # ✅ All details collected – Generate Travel Plan
    travel_plan = travel_agent.run(
        f"Plan a trip to {session['destination']} for {session['group_size']} people, from {session['dates']}. "
        f"Budget: {session['budget']}. Hotel preference: {session['hotel_preference']}. "
        f"Interested in: {session['activities']}. Visa Info: {session['visa_info']}."
    )

    await slack_client.chat_postMessage(channel=channel_id, text=travel_plan.content)

    # ✅ Clear session after response
    del user_sessions[user_id]

async def handle_slack_message(event):
    """Handles Slack messages and ensures a smooth conversation flow."""
    channel_id = event.get("channel")
    user_query = event.get("text").strip()
    user_id = event.get("user")

    if not channel_id or not user_query:
        return

    if event.get("bot_id"):  # Ignore bot messages
        return

    session = user_sessions.get(user_id, {})

    # Identify the next missing field and save the user's response
    for field, _ in QUESTIONS:
        if field not in session:
            session[field] = user_query
            user_sessions[user_id] = session
            break

    # Ask the next question
    await ask_next_question(channel_id, user_id)

async def process_socket_mode_request(client: SocketModeClient, req: SocketModeRequest):
    """Handles Slack events over Socket Mode."""
    if req.type == "events_api":
        response = SocketModeResponse(envelope_id=req.envelope_id)
        await client.send_socket_mode_response(response)

        event = req.payload.get("event", {})
        if event.get("type") == "message" and "subtype" not in event:
            await handle_slack_message(event)

async def connect_with_retry():
    """Attempts to connect to Slack, retrying if it fails."""
    attempt = 1
    while True:
        try:
            print(f"⏳ Connecting to Slack (Attempt {attempt})...")
            await socket_client.connect()
            print("✅ Connected to Slack!")
            return
        except Exception as e:
            print(f"⚠️ Connection error: {str(e)}")
            if attempt >= 3:
                print("❌ Failed to connect after 3 attempts.")
                raise
            print("🔄 Retrying in 5 seconds...")
            await asyncio.sleep(5)
            attempt += 1

async def main():
    """Starts the Slack bot using Socket Mode."""
    global socket_client

    print("🚀 Starting DerivNomad Slack bot...")

    if not SLACK_APP_TOKEN or not SLACK_BOT_TOKEN:
        print("❌ Missing Slack tokens! Exiting...")
        return

    while True:
        try:
            socket_client = await create_socket_client()
            socket_client.socket_mode_request_listeners.append(process_socket_mode_request)
            await socket_client.connect()
            print("✅ Bot is ready to receive messages!")

            while True:
                await asyncio.sleep(1)
                if not await socket_client.is_connected():
                    print("🔌 Connection lost! Reconnecting...")
                    break

        except Exception as e:
            print(f"⚠️ Unexpected error: {str(e)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())