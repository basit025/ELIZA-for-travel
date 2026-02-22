import re
import random

# =======================================================================
# ELIZA-Style Travel Assistance Chatbot
# =======================================================================
# This chatbot uses pure Python regular expressions to match user intents
# and respond accordingly. It extracts relevant context using capture
# groups and reflects it back with pronoun substitution, just like ELIZA.
# =======================================================================

# Pronoun reflections to swap user perspectives in captured phrases.
# For example, if a user says "I want to fly to my home", the bot captures
# "my home", reflects it to "your home", and responds appropriately.
REFLECTIONS = {
    "i": "you",
    "me": "you",
    "my": "your",
    "mine": "yours",
    "am": "are",
    "you": "I",
    "your": "my",
    "yours": "mine",
    "are": "am",
    "i'm": "you're",
    "i've": "you've",
    "i'll": "you'll",
    "i'd": "you'd",
    "you're": "I'm",
    "you've": "I've",
    "you'll": "I'll",
    "you'd": "I'd"
}

def reflect(text):
    """
    Splits the extracted text into words, swaps pronouns using REFLECTIONS,
    and returns the reflected string.
    """
    words = text.lower().split()
    reflected_words = [REFLECTIONS.get(word, word) for word in words]
    return " ".join(reflected_words)

# =======================================================================
# PATTERN MATCHING RULES
# =======================================================================
# The dictionary uses compiled regular expressions as keys.
# Order matters: more specific patterns (like checking both origin and 
# destination) are evaluated before broader patterns.
# The `(.*)` or `(.*?)` groups capture information to be substituted into 
# the `{0}`, `{1}` placeholders in the response strings.
# =======================================================================

RULES = {
    # ---------------------------------------------------------------------
    # COMPLETE TRAVEL FUNNEL: HOTELS & FLIGHTS (Strict Order of Operations)
    # ---------------------------------------------------------------------

    # 1. Final Confirmations: Number of Rooms or Tickets
    re.compile(r'^\s*(?:i\s*want\s*)?(?:for\s+)?(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s*(?:room|rooms)\s*$', re.IGNORECASE): [
        "Perfect! I have initiated the booking for {0} room(s). Thank you! Your reservation is confirmed! Let me know if you need to book a flight next.",
        "Excellent. Booking {0} room(s) for your stay. Thank you! You're all set! Do you need help booking flights?"
    ],
    re.compile(r'^\s*(?:i\s*want\s*)?(?:for\s+)?(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s*(?:ticket|tickets|seat|seats|passenger|passengers)\s*$', re.IGNORECASE): [
        "Perfect! I have booked {0} flight ticket(s) for you. Thank you! Your flight is confirmed. Need a hotel now?",
        "Excellent. Generating {0} ticket(s) for your flight. Thank you! Your booking is complete!"
    ],
    re.compile(r'.*\b(\d+)\s*(?:room|rooms)\b.*', re.IGNORECASE): [
        "Got it! Booking {0} rooms for you right away. Thank you! The total amount has been calculated. Your hotel reservation is complete!",
        "Confirmed! {0} rooms have been reserved for your stay. Thank you and have a wonderful trip!"
    ],
    re.compile(r'.*\b(\d+)\s*(?:ticket|tickets|seat|seats|passenger|passengers)\b.*', re.IGNORECASE): [
        "Got it! Reserving {0} flight tickets for you. Thank you! Your flight booking is complete!",
        "Confirmed! {0} seats have been booked. Thank you and have a wonderful flight!"
    ],
    
    # Generic numbers fallback (assuming it applies to whatever context they were just in)
    re.compile(r'^\s*(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s*$', re.IGNORECASE): [
        "Understood. I am processing your booking for {0}. Thank you! Your transaction is successfully confirmed. What's next on your travel list?",
        "Booking {0} completed! Thank you very much. Is there anything else you need, like a flight or hotel?"
    ],

    # 2. FLIGHTS: Catching Trip Type (One way vs Round trip)
    re.compile(r'.*\b(one[-\s]?way)\b.*', re.IGNORECASE): [
        "A one-way ticket is a great choice. Would you prefer Economy ($500) or Business class ($1500)?",
        "Noted, one-way trip. Are you flying Economy or Business class today?"
    ],
    re.compile(r'.*\b(round[-\s]?trip|two[-\s]?way|return)\b.*', re.IGNORECASE): [
        "Round-trip it is! That will ensure you get back home safely. Do you want Economy ($500) or Business class ($1500)?",
        "A round-trip ticket works best. Which class were you looking to fly in: Economy or Business?"
    ],

    # 3. FLIGHTS: Catching Date references
    re.compile(r'.*\b(tomorrow|next week|today|next month|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b.*(?:flight|ticket|travel).*', re.IGNORECASE): [
        "Traveling {0} sounds like a great plan. Is this a one-way flight or a round-trip?",
        "Going {0} gives us options. Do you need a one-way or a round-trip flight?"
    ],

    # 4. FLIGHTS: Catching Specific Airlines
    re.compile(r'.*\b(emirates|qatar|delta|american|united|british|pia|ryanair|lufthansa|singapore)\b.*(?:airlines|airways|air)?.*', re.IGNORECASE): [
        "{0} is a reputable airline! Should I look up flights for Economy or Business class with them?",
        "Flying with {0} is a popular choice. Would you prefer a one-way or round-trip ticket?"
    ],

    # 5. FLIGHTS: Catching Class preference
    re.compile(r'.*\b(economy|coach|standard)\b.*', re.IGNORECASE): [
        "Economy class is a great way to save! The price is $500 per ticket. How many flight tickets do you need?",
        "I've selected Economy class for your flight at $500 per seat. Please enter the number of tickets you'd like to book."
    ],
    re.compile(r'.*\b(business|first class|first-class)\b.*', re.IGNORECASE): [
        "Treating yourself! Business/First class tickets are $1500 per ticket. How many tickets should I book for you?",
        "I have selected premium class for your flight at $1500 per seat. How many passengers will be traveling?"
    ],

    # 6. FLIGHTS: Inquiring about flights with Origin AND Destination
    re.compile(r'.*\b(?:flight|flights|fly|travel|ticket(?:s)?)\b(?:.*?)(?:from|out of)\s+(.*?)\s+(?:to|towards)\s+([a-zA-Z]+)\b.*', re.IGNORECASE): [
        "A flight from {0} to {1} sounds exciting! Are you looking for a one-way or round-trip ticket?",
        "Checking available flights from {0} to {1}. Do you have a preferred airline, or should I find the cheapest option?"
    ],

    # 7. FLIGHTS: Inquiring about flights with Destination only
    re.compile(r'.*\b(?:flight|flights|fly|travel|ticket(?:s)?)\b(?:.*?)(?:to|towards|for)\s+([a-zA-Z]+)\b.*', re.IGNORECASE): [
        "Let me help you book a flight to {0}. Is this a one-way or round-trip journey?",
        "Looking for flights to {0}... What month or day are you planning to travel?"
    ],

    # 5. HOTELS: Catching specific Hotel selections
    re.compile(r'.*\b(hotel\s*[1-6]|hotel\s*(?:one|two|three|four|five|six))\b.*', re.IGNORECASE): [
        "Great choice! {0} is a fantastic property. Please enter the number of rooms you would like to book.",
        "I can certainly book you into {0}. How many rooms do you need?"
    ],
    
    # 6. HOTELS: Catching Luxury vs Budget preference
    re.compile(r'.*\bluxury\b.*', re.IGNORECASE): [
        "For luxury accommodations, we offer Hotel 1, Hotel 2, and Hotel 3. The price is 15000Rs/room. Which hotel would you prefer?",
        "Our luxury options include Hotel 1, Hotel 2, and Hotel 3 at 15000Rs per room. Which one of these catches your eye?"
    ],
    re.compile(r'.*\bbudget(?:-friendly)?\b.*', re.IGNORECASE): [
        "For budget-friendly stays, we have Hotel 4, Hotel 5, and Hotel 6. The price is 8000Rs/room. Which hotel would you prefer?",
        "Our budget options are Hotel 4, Hotel 5, and Hotel 6 at 8000Rs per room. Which of these would you like to book?"
    ],

    # 7. HOTELS: Catching City combined with a hotel request
    re.compile(r'.*\b(?:hotel(?:s)?|accommodation(?:s)?|stay(?:s)?|motel(?:s)?|resort(?:s)?|room(?:s)?)\b(?:.*?)(?:in|at|near|around)\s+([a-zA-Z]+)\b.*', re.IGNORECASE): [
        "I can help you book a hotel in {0}. Would you prefer a luxury option or a budget-friendly option?",
        "Searching for hotels in {0}... Are you looking for luxury or budget-friendly accommodations?"
    ],

    # 8. Initial generic requests to find a hotel or flight without a city
    re.compile(r'.*\b(?:book|find|want(?: a)?)\b.*(?:hotel|accom?modat(?:ion)?|stay|motel|resort|room).*', re.IGNORECASE): [
        "I'd be happy to help you book a hotel! Which city are you traveling to?",
        "Let's get your accommodation sorted. Which city do you need a hotel in?"
    ],
    re.compile(r'.*\b(?:book|find|want(?: a)?)\b.*(?:flight|ticket).*', re.IGNORECASE): [
        "I can definitely help you book a flight. Where are you planning to fly to?",
        "Flights are my specialty! What is your destination city?"
    ],

    # 9. Simple isolated city names (Catch-all for when the bot asks for a city)
    re.compile(r'^\s*([a-zA-Z]{3,15}(?:\s+[a-zA-Z]{3,15})?)\s*$', re.IGNORECASE): [
        "Got it, {0}. Would you like me to book a flight there, or find some accommodation?",
        "Looking into {0}. Should we start with booking a flight or finding a hotel?"
    ],

    # 10. Greetings
    re.compile(r'^\b(hello|hi|hey|greetings|good\s?(morning|afternoon|evening))\b.*', re.IGNORECASE): [
        "Hello! I am your Travel Booking Assistant. Do you want to book a flight, or find a hotel room?",
        "Greetings! Ready to travel? Let me know if you need to book a flight to your destination, or find a hotel."
    ],

    # 11. User gets frustrated (e.g. "shut up", "stupid")
    re.compile(r'.*\b(shut up|stupid|dumb|idiot|hate|bad|useless)\b.*', re.IGNORECASE): [
        "I'm sorry to frustrate you! Let's start over: Do you need to book a flight or a hotel?",
        "My apologies! I can handle both flight and hotel bookings. What can I do for you today?"
    ],

    # 12. Farewells
    re.compile(r'^\b(bye|goodbye|see ya|cya|adios|quit|exit)\b.*', re.IGNORECASE): [
        "Goodbye! Have a great trip and enjoy your flights and hotel stays.",
        "See you! Safe travels on your upcoming journey."
    ]
}

# =======================================================================
# FALLBACK RESPONSES
# =======================================================================
DEFAULT_RESPONSES = [
    "I handle flight and hotel bookings! Do you want to book a flight somewhere, or find a hotel room?",
    "I'm here to help you travel! Please tell me if you need a flight to a city, or a luxury/budget hotel.",
    "Could you rephrase that? Try asking for 'a flight to London' or a 'hotel in Tokyo'.",
    "I am a travel booking bot. Are you interested in sorting out your flights or your accommodation today?"
]

def respond(user_input):
    """
    Takes the user input, matches it against predefined regex patterns,
    extracts info using capture groups, reflects pronouns, and formats 
    the selected response.
    """
    # Clean up input slightly to remove trailing punctuation that might mess up capture groups
    clean_input = re.sub(r'[?!.]+$', '', user_input.strip())

    # Iterate through our compiled regex patterns
    for pattern, responses in RULES.items():
        match = pattern.match(clean_input)
        
        # If the input matches a regex pattern
        if match:
            # Pick a random response from the mapped list
            chosen_response = random.choice(responses)
            
            # Extract the captured groups (e.g., Target destinations or origins)
            groups = match.groups()
            
            # If there are groups to reflect and substitute
            if groups:
                # Apply word reflection and stripping
                reflected_groups = [reflect(g.strip()) for g in groups if g is not None]
                
                try:
                    # Substitute the groups into the response template using positional formatting
                    return chosen_response.format(*reflected_groups)
                except IndexError:
                    # Fallback if there's a mismatch between format tokens and captured groups
                    return chosen_response
            else:
                return chosen_response

    # If no pattern matched, return a random fallback response
    return random.choice(DEFAULT_RESPONSES)

def main():
    """
    The main chat loop that interacting with the user via standard input/output.
    """
    print("=" * 60)
    print("✈️🏨   Travel Booking Assistant Initialized   🏨✈️")
    print("=" * 60)
    print("Tips:")
    print(" - FLIGHTS: Try 'book a flight to Paris', choose 'Economy' or 'Business', tell me ticket count.")
    print(" - HOTELS:  Try 'hotel in Lahore', choose 'Luxury' or 'Budget', select a hotel, tell me room count.")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("-" * 60)
    
    print("\nBot: Hello! I am your Travel Booking Assistant. Do you want to book a flight or a hotel today?")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for a clean exit command BEFORE processing further
            if user_input.strip().lower() in ['quit', 'exit', 'bye']:
                print("\nBot: Goodbye! Have a safe and wonderful trip!")
                break
            
            # Skip empty inputs
            if not user_input.strip():
                continue
                
            # Get the bot's response and print it
            reply = respond(user_input)
            print(f"Bot: {reply}")
            
        except KeyboardInterrupt:
            # Handle CTRL+C gracefully
            print("\nBot: Safe travels! Goodbye!")
            break
        except EOFError:
            # Handle end of file gracefully
            print("\nBot: Goodbye!")
            break

if __name__ == "__main__":
    main()
