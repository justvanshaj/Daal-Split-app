import streamlit as st
import random
import string
import time
import threading
import html

from streamlit_autorefresh import st_autorefresh


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Kitty Housie",
    page_icon="🎉",
    layout="wide"
)


# ============================================================
# SHARED SERVER MEMORY
# ============================================================

@st.cache_resource
def get_rooms():
    return {}


ROOMS = get_rooms()

ROOM_LOCK = threading.Lock()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "screen": "welcome",
    "room_code": None,
    "player_name": None,
    "role": None,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# ROOM CODE
# ============================================================

def generate_room_code():

    characters = string.ascii_uppercase + string.digits

    while True:

        code = "".join(
            random.choices(
                characters,
                k=6
            )
        )

        if code not in ROOMS:
            return code


# ============================================================
# TICKET GENERATION
# ============================================================

def generate_ticket():

    """
    Standard Tambola/Housie ticket:

    3 rows × 9 columns
    15 numbers total
    5 numbers per row
    """

    while True:

        # ----------------------------------------------------
        # Choose how many numbers each column contains.
        # Each column must have at least one number.
        # Total = 15.
        # ----------------------------------------------------

        counts = [1] * 9

        remaining = 6

        while remaining > 0:

            possible = [
                i for i in range(9)
                if counts[i] < 3
            ]

            column = random.choice(possible)

            counts[column] += 1

            remaining -= 1

        # ----------------------------------------------------
        # Select rows for every column.
        # ----------------------------------------------------

        grid = [
            [None for _ in range(9)]
            for _ in range(3)
        ]

        valid = True

        for col in range(9):

            number_count = counts[col]

            rows = random.sample(
                range(3),
                number_count
            )

            for row in rows:

                grid[row][col] = True

        # ----------------------------------------------------
        # Every row must contain exactly 5 numbers.
        # ----------------------------------------------------

        for row in range(3):

            if sum(
                1 for x in grid[row]
                if x
            ) != 5:

                valid = False

        if not valid:
            continue

        # ----------------------------------------------------
        # Generate numbers for each column.
        # ----------------------------------------------------

        numbers = []

        for col in range(9):

            if col == 0:

                pool = list(range(1, 10))

            elif col == 8:

                pool = list(range(80, 91))

            else:

                start = col * 10

                pool = list(
                    range(
                        start,
                        start + 10
                    )
                )

            count = counts[col]

            selected = sorted(
                random.sample(
                    pool,
                    count
                )
            )

            numbers.append(selected)

        # ----------------------------------------------------
        # Put numbers into grid.
        # ----------------------------------------------------

        ticket = [
            [None for _ in range(9)]
            for _ in range(3)
        ]

        for col in range(9):

            selected_numbers = numbers[col]

            number_index = 0

            for row in range(3):

                if grid[row][col]:

                    ticket[row][col] = (
                        selected_numbers[
                            number_index
                        ]
                    )

                    number_index += 1

        return ticket


# ============================================================
# CREATE ROOM
# ============================================================

def create_room(host_name):

    code = generate_room_code()

    room = {

        "host": host_name,

        "players": {},

        "tickets": {},

        "called_numbers": [],

        "current_number": None,

        "number_sequence": random.sample(
            range(1, 91),
            90
        ),

        "next_number_index": 0,

        "game_started": False,

        "game_finished": False,

        "game_start_time": None,

        "last_draw_time": None,

        "interval": 15,

        "claims": [],

        "winners": {},

        "created_at": time.time(),

        "last_activity": time.time(),

        "version": 0
    }

    with ROOM_LOCK:

        ROOMS[code] = room

    return code


# ============================================================
# CLEAN OLD ROOMS
# ============================================================

def cleanup_rooms():

    now = time.time()

    expired = []

    with ROOM_LOCK:

        for code, room in list(ROOMS.items()):

            if now - room["last_activity"] > 21600:

                expired.append(code)

        for code in expired:

            del ROOMS[code]


cleanup_rooms()


# ============================================================
# HOME
# ============================================================

def return_home():

    st.session_state.screen = "welcome"

    st.session_state.room_code = None

    st.session_state.player_name = None

    st.session_state.role = None

    st.rerun()


# ============================================================
# WELCOME SCREEN
# ============================================================

def welcome_screen():

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:25px;
        ">

        <h1>🎉 KITTY HOUSIE 🎉</h1>

        <p style="font-size:20px;">
        Fun • Friends • Numbers • Prizes
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("## 👑 HOST")

        st.write(
            "Create the game and keep your device in the centre."
        )

        if st.button(
            "👑 CREATE GAME",
            type="primary",
            use_container_width=True
        ):

            st.session_state.screen = "host"

            st.rerun()

    with col2:

        st.markdown("## 🎟️ PLAYER")

        st.write(
            "Join using the room code provided by the host."
        )

        if st.button(
            "🎟️ JOIN GAME",
            use_container_width=True
        ):

            st.session_state.screen = "player"

            st.rerun()


# ============================================================
# HOST SETUP
# ============================================================

def host_screen():

    st.title("👑 Create Housie Game")

    name = st.text_input(
        "Host name",
        max_chars=25,
        placeholder="Enter your name"
    )

    if st.button(
        "CREATE GAME",
        type="primary",
        use_container_width=True
    ):

        name = name.strip()

        if not name:

            st.warning(
                "Please enter the host name."
            )

            return

        code = create_room(name)

        st.session_state.room_code = code

        st.session_state.player_name = name

        st.session_state.role = "host"

        st.session_state.screen = "host_room"

        st.rerun()

    if st.button("← Back"):

        return_home()


# ============================================================
# PLAYER JOIN
# ============================================================

def player_screen():

    st.title("🎟️ Join Housie Game")

    name = st.text_input(
        "Your name",
        max_chars=25,
        placeholder="Enter your name"
    )

    code = st.text_input(
        "Room code",
        max_chars=6,
        placeholder="Example: A7K92P"
    ).upper().strip()

    if st.button(
        "JOIN GAME",
        type="primary",
        use_container_width=True
    ):

        name = name.strip()

        if not name:

            st.warning(
                "Please enter your name."
            )

            return

        if not code:

            st.warning(
                "Please enter the room code."
            )

            return

        if code not in ROOMS:

            st.error(
                "Room not found. Please check the code."
            )

            return

        room = ROOMS[code]

        if name in room["players"]:

            st.error(
                "That name is already being used."
            )

            return

        ticket = generate_ticket()

        room["players"][name] = {
            "joined_at": time.time()
        }

        room["tickets"][name] = ticket

        room["last_activity"] = time.time()

        room["version"] += 1

        st.session_state.room_code = code

        st.session_state.player_name = name

        st.session_state.role = "player"

        st.session_state.screen = "player_room"

        st.rerun()

    if st.button("← Back"):

        return_home()


# ============================================================
# DRAW NEXT NUMBER
# ============================================================

def draw_next_number(room):

    if room["next_number_index"] >= 90:

        room["game_finished"] = True

        return

    number = room["number_sequence"][
        room["next_number_index"]
    ]

    room["next_number_index"] += 1

    room["current_number"] = number

    room["called_numbers"].append(number)

    room["last_draw_time"] = time.time()

    room["last_activity"] = time.time()

    room["version"] += 1


# ============================================================
# AUTOMATIC HOST DRAW
# ============================================================

def process_automatic_draw(room):

    if not room["game_started"]:
        return

    if room["game_finished"]:
        return

    if room["game_start_time"] is None:
        return

    now = time.time()

    elapsed = now - room["game_start_time"]

    expected_number_count = int(
        elapsed // room["interval"]
    ) + 1

    current_count = len(
        room["called_numbers"]
    )

    while (
        current_count
        < expected_number_count
        and current_count < 90
    ):

        draw_next_number(room)

        current_count = len(
            room["called_numbers"]
        )


# ============================================================
# START GAME
# ============================================================

def start_game(room):

    if not room["players"]:
        return False

    room["game_started"] = True

    room["game_finished"] = False

    room["game_start_time"] = time.time()

    room["last_draw_time"] = None

    room["last_activity"] = time.time()

    room["version"] += 1

    # First number immediately
    draw_next_number(room)

    return True


# ============================================================
# GET REMAINING TIME
# ============================================================

def seconds_until_next(room):

    if not room["game_started"]:
        return 15

    if room["game_finished"]:
        return 0

    if room["last_draw_time"] is None:
        return 15

    elapsed = (
        time.time()
        - room["last_draw_time"]
    )

    remaining = room["interval"] - elapsed

    return max(
        0,
        int(remaining)
    )


# ============================================================
# NUMBER WORD
# ============================================================

def number_word(number):

    words = {
        1: "ONE",
        2: "TWO",
        3: "THREE",
        4: "FOUR",
        5: "FIVE",
        6: "SIX",
        7: "SEVEN",
        8: "EIGHT",
        9: "NINE",
        10: "TEN",
        11: "ELEVEN",
        12: "TWELVE",
        13: "THIRTEEN",
        14: "FOURTEEN",
        15: "FIFTEEN",
        16: "SIXTEEN",
        17: "SEVENTEEN",
        18: "EIGHTEEN",
        19: "NINETEEN",
        20: "TWENTY",
        21: "TWENTY ONE",
        22: "TWENTY TWO",
        23: "TWENTY THREE",
        24: "TWENTY FOUR",
        25: "TWENTY FIVE",
        26: "TWENTY SIX",
        27: "TWENTY SEVEN",
        28: "TWENTY EIGHT",
        29: "TWENTY NINE",
        30: "THIRTY",
        31: "THIRTY ONE",
        32: "THIRTY TWO",
        33: "THIRTY THREE",
        34: "THIRTY FOUR",
        35: "THIRTY FIVE",
        36: "THIRTY SIX",
        37: "THIRTY SEVEN",
        38: "THIRTY EIGHT",
        39: "THIRTY NINE",
        40: "FORTY",
        41: "FORTY ONE",
        42: "FORTY TWO",
        43: "FORTY THREE",
        44: "FORTY FOUR",
        45: "FORTY FIVE",
        46: "FORTY SIX",
        47: "FORTY SEVEN",
        48: "FORTY EIGHT",
        49: "FORTY NINE",
        50: "FIFTY",
        51: "FIFTY ONE",
        52: "FIFTY TWO",
        53: "FIFTY THREE",
        54: "FIFTY FOUR",
        55: "FIFTY FIVE",
        56: "FIFTY SIX",
        57: "FIFTY SEVEN",
        58: "FIFTY EIGHT",
        59: "FIFTY NINE",
        60: "SIXTY",
        61: "SIXTY ONE",
        62: "SIXTY TWO",
        63: "SIXTY THREE",
        64: "SIXTY FOUR",
        65: "SIXTY FIVE",
        66: "SIXTY SIX",
        67: "SIXTY SEVEN",
        68: "SIXTY EIGHT",
        69: "SIXTY NINE",
        70: "SEVENTY",
        71: "SEVENTY ONE",
        72: "SEVENTY TWO",
        73: "SEVENTY THREE",
        74: "SEVENTY FOUR",
        75: "SEVENTY FIVE",
        76: "SEVENTY SIX",
        77: "SEVENTY SEVEN",
        78: "SEVENTY EIGHT",
        79: "SEVENTY NINE",
        80: "EIGHTY",
        81: "EIGHTY ONE",
        82: "EIGHTY TWO",
        83: "EIGHTY THREE",
        84: "EIGHTY FOUR",
        85: "EIGHTY FIVE",
        86: "EIGHTY SIX",
        87: "EIGHTY SEVEN",
        88: "EIGHTY EIGHT",
        89: "EIGHTY NINE",
        90: "NINETY",
    }

    return words.get(
        number,
        str(number)
    )


# ============================================================
# TICKET HTML
# ============================================================

def ticket_html(ticket, called_numbers):

    called = set(called_numbers)

    output = """
    <div style="
        width:100%;
        max-width:700px;
        margin:auto;
        border:4px solid #333;
        border-radius:15px;
        overflow:hidden;
        box-shadow:0 5px 20px rgba(0,0,0,0.2);
    ">
    """

    for row in ticket:

        output += """
        <div style="
            display:grid;
            grid-template-columns:repeat(9,1fr);
        ">
        """

        for number in row:

            if number is None:

                output += """
                <div style="
                    height:65px;
                    background:#eeeeee;
                    border:1px solid #999;
                ">
                </div>
                """

            else:

                if number in called:

                    background = "#58d68d"
                    text_color = "#083b1c"

                    mark = "✓"

                else:

                    background = "#ffffff"
                    text_color = "#111111"

                    mark = ""

                output += f"""
                <div style="
                    height:65px;
                    background:{background};
                    color:{text_color};
                    border:1px solid #777;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:27px;
                    font-weight:800;
                    position:relative;
                ">

                    {number}

                    <span style="
                        position:absolute;
                        right:5px;
                        bottom:1px;
                        font-size:14px;
                    ">
                    {mark}
                    </span>

                </div>
                """

        output += "</div>"

    output += "</div>"

    return output


# ============================================================
# CLAIM VALIDATION
# ============================================================

def validate_claim(
    room,
    player_name,
    claim_type
):

    ticket = room["tickets"][player_name]

    called = set(
        room["called_numbers"]
    )

    numbers = [
        number
        for row in ticket
        for number in row
        if number is not None
    ]

    # --------------------------------------------------------
    # EARLY FIVE
    # --------------------------------------------------------

    if claim_type == "Early Five":

        return sum(
            1 for number in numbers
            if number in called
        ) >= 5

    # --------------------------------------------------------
    # TOP LINE
    # --------------------------------------------------------

    if claim_type == "Top Line":

        return all(
            number is None
            or number in called
            for number in ticket[0]
        )

    # --------------------------------------------------------
    # MIDDLE LINE
    # --------------------------------------------------------

    if claim_type == "Middle Line":

        return all(
            number is None
            or number in called
            for number in ticket[1]
        )

    # --------------------------------------------------------
    # BOTTOM LINE
    # --------------------------------------------------------

    if claim_type == "Bottom Line":

        return all(
            number is None
            or number in called
            for number in ticket[2]
        )

    # --------------------------------------------------------
    # FOUR CORNERS
    # --------------------------------------------------------

    if claim_type == "Four Corners":

        first = None
        last = None

        # First number
        for number in ticket[0]:

            if number is not None:

                first = number
                break

        # Last number
        for number in reversed(ticket[0]):

            if number is not None:

                last = number
                break

        # Bottom first
        bottom_first = None

        for number in ticket[2]:

            if number is not None:

                bottom_first = number
                break

        # Bottom last
        bottom_last = None

        for number in reversed(ticket[2]):

            if number is not None:

                bottom_last = number
                break

        corners = [
            first,
            last,
            bottom_first,
            bottom_last
        ]

        return all(
            number in called
            for number in corners
            if number is not None
        )

    # --------------------------------------------------------
    # FULL HOUSE
    # --------------------------------------------------------

    if claim_type == "Full House":

        return all(
            number in called
            for number in numbers
        )

    return False


# ============================================================
# CLAIM
# ============================================================

def make_claim(
    room,
    player_name,
    claim_type
):

    # Don't allow same claim twice
    existing = room["claims"]

    for claim in existing:

        if (
            claim["player"] == player_name
            and claim["type"] == claim_type
        ):

            return

    valid = validate_claim(
        room,
        player_name,
        claim_type
    )

    claim = {

        "player": player_name,

        "type": claim_type,

        "valid": valid,

        "time": time.time()
    }

    room["claims"].append(claim)

    if valid:

        room["winners"].setdefault(
            claim_type,
            []
        )

        room["winners"][claim_type].append(
            player_name
        )

    room["last_activity"] = time.time()

    room["version"] += 1


# ============================================================
# HOST ROOM
# ============================================================

def host_room():

    code = st.session_state.room_code

    if code not in ROOMS:

        st.error(
            "Room no longer exists."
        )

        return

    room = ROOMS[code]

    # Automatic caller
    process_automatic_draw(room)

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            text-align:center;
        ">
        <h1>🎉 KITTY HOUSIE 🎉</h1>
        <p style="font-size:20px;">
        Official Number Caller
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --------------------------------------------------------
    # ROOM
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:10px;
        ">

        <div style="font-size:18px;">
        ROOM CODE
        </div>

        <div style="
            font-size:38px;
            font-weight:bold;
            letter-spacing:8px;
        ">
        {code}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --------------------------------------------------------
    # PLAYERS
    # --------------------------------------------------------

    st.subheader(
        f"👩 Players Joined: {len(room['players'])}"
    )

    if room["players"]:

        st.write(
            ", ".join(
                room["players"].keys()
            )
        )

    else:

        st.info(
            "Waiting for ladies to join..."
        )

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    if not room["game_started"]:

        st.divider()

        st.markdown(
            """
            ### 🎯 Ready?

            Keep this device in the centre of the group.

            Once started, a new number will automatically
            appear every **15 seconds**.
            """
        )

        if st.button(
            "▶️ START HOUSIE",
            type="primary",
            use_container_width=True
        ):

            if not room["players"]:

                st.warning(
                    "At least one player must join first."
                )

            else:

                start_game(room)

                st.rerun()

    else:

        # ----------------------------------------------------
        # CURRENT NUMBER
        # ----------------------------------------------------

        current = room["current_number"]

        if current:

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:25px;
                    border-radius:25px;
                    background:#f8f9fa;
                    border:5px solid #333;
                ">

                <div style="
                    font-size:25px;
                    font-weight:bold;
                ">
                🔊 NUMBER CALLED
                </div>

                <div style="
                    font-size:130px;
                    font-weight:900;
                    line-height:1;
                    margin:20px;
                ">
                {current}
                </div>

                <div style="
                    font-size:30px;
                    font-weight:bold;
                ">
                {number_word(current)}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        # ----------------------------------------------------
        # COUNTDOWN
        # ----------------------------------------------------

        if not room["game_finished"]:

            remaining = seconds_until_next(room)

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    margin:20px;
                ">

                <div style="
                    font-size:20px;
                ">
                Next number in
                </div>

                <div style="
                    font-size:55px;
                    font-weight:bold;
                ">
                {remaining}
                </div>

                seconds

                </div>
                """,
                unsafe_allow_html=True
            )

        # ----------------------------------------------------
        # CALLED NUMBERS
        # ----------------------------------------------------

        st.subheader("🎱 Numbers Called")

        called = room["called_numbers"]

        cols = st.columns(10)

        for index, number in enumerate(called):

            cols[
                index % 10
            ].markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:8px;
                    margin:3px;
                    border-radius:8px;
                    background:#eeeeee;
                    font-weight:bold;
                    font-size:18px;
                ">
                {number}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ----------------------------------------------------
        # CLAIMS
        # ----------------------------------------------------

        st.divider()

        st.subheader("🏆 Winner Claims")

        if room["claims"]:

            for claim in room["claims"]:

                if claim["valid"]:

                    st.success(
                        f"🏆 {claim['player']} — "
                        f"{claim['type']} — VALID"
                    )

                else:

                    st.error(
                        f"❌ {claim['player']} — "
                        f"{claim['type']} — INVALID"
                    )

        else:

            st.caption(
                "No claims yet."
            )

    # --------------------------------------------------------
    # NEW GAME
    # --------------------------------------------------------

    st.divider()

    if st.button(
        "🔄 NEW GAME",
        use_container_width=True
    ):

        new_room = create_room(
            room["host"]
        )

        # Move existing players into new room
        new_room_data = ROOMS[new_room]

        for player in room["players"]:

            new_room_data["players"][player] = {
                "joined_at": time.time()
            }

            new_room_data["tickets"][player] = (
                generate_ticket()
            )

        del ROOMS[code]

        st.session_state.room_code = new_room

        st.rerun()

    # --------------------------------------------------------
    # AUTO REFRESH
    # --------------------------------------------------------

    st_autorefresh(
        interval=1000,
        key=f"host_refresh_{code}"
    )


# ============================================================
# PLAYER ROOM
# ============================================================

def player_room():

    code = st.session_state.room_code

    if code not in ROOMS:

        st.error(
            "Room no longer exists."
        )

        return

    room = ROOMS[code]

    player_name = st.session_state.player_name

    # --------------------------------------------------------
    # AUTOMATIC UPDATE
    # --------------------------------------------------------

    st_autorefresh(
        interval=1000,
        key=f"player_refresh_{code}"
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            text-align:center;
        ">

        <h1>🎟️ MY HOUSIE TICKET</h1>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        f"👩 Player: **{player_name}**"
    )

    # --------------------------------------------------------
    # CURRENT NUMBER
    # --------------------------------------------------------

    current = room["current_number"]

    if current:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                padding:15px;
                border-radius:18px;
                background:#fff3cd;
                border:4px solid #f1c40f;
            ">

            <div style="
                font-size:18px;
                font-weight:bold;
            ">
            🔴 JUST CALLED
            </div>

            <div style="
                font-size:75px;
                font-weight:900;
                line-height:1;
            ">
            {current}
            </div>

            <div style="
                font-size:22px;
                font-weight:bold;
            ">
            {number_word(current)}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # TICKET
    # --------------------------------------------------------

    st.divider()

    ticket = room["tickets"][player_name]

    st.markdown(
        ticket_html(
            ticket,
            room["called_numbers"]
        ),
        unsafe_allow_html=True
    )

    st.caption(
        "Numbers are automatically marked when the host calls them."
    )

    # --------------------------------------------------------
    # CALLED NUMBERS
    # --------------------------------------------------------

    st.divider()

    st.subheader("🎱 Called Numbers")

    called = room["called_numbers"]

    if called:

        st.write(
            " • ".join(
                str(number)
                for number in called
            )
        )

    # --------------------------------------------------------
    # CLAIMS
    # --------------------------------------------------------

    st.divider()

    st.subheader("🏆 Make a Claim")

    st.caption(
        "The server will automatically verify your ticket."
    )

    claim_types = [
        "Early Five",
        "Top Line",
        "Middle Line",
        "Bottom Line",
        "Four Corners",
        "Full House",
    ]

    cols = st.columns(2)

    for index, claim_type in enumerate(
        claim_types
    ):

        with cols[index % 2]:

            if st.button(
                f"🏆 {claim_type}",
                use_container_width=True,
                key=f"claim_{claim_type}_{code}"
            ):

                make_claim(
                    room,
                    player_name,
                    claim_type
                )

                st.rerun()

    # --------------------------------------------------------
    # CLAIM STATUS
    # --------------------------------------------------------

    my_claims = [
        claim
        for claim in room["claims"]
        if claim["player"] == player_name
    ]

    if my_claims:

        st.divider()

        st.subheader("Your Claims")

        for claim in my_claims:

            if claim["valid"]:

                st.success(
                    f"🏆 {claim['type']} — VALID"
                )

            else:

                st.error(
                    f"❌ {claim['type']} — NOT YET COMPLETE"
                )


# ============================================================
# ROUTER
# ============================================================

if st.session_state.screen == "welcome":

    welcome_screen()

elif st.session_state.screen == "host":

    host_screen()

elif st.session_state.screen == "player":

    player_screen()

elif st.session_state.screen == "host_room":

    host_room()

elif st.session_state.screen == "player_room":

    player_room()
