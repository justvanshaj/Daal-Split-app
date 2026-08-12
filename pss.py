import streamlit as st
import chess
import chess.svg
import random
import string
import time
from streamlit_autorefresh import st_autorefresh


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Private Chess",
    page_icon="♟️",
    layout="centered"
)


# ============================================================
# SHARED SERVER-SIDE ROOM STORAGE
# ============================================================

@st.cache_resource
def get_game_rooms():
    return {}


GAME_ROOMS = get_game_rooms()


# ============================================================
# ROOM CLEANUP
# ============================================================

def cleanup_rooms():

    current_time = time.time()

    expired_rooms = []

    for code, room in GAME_ROOMS.items():

        # Delete rooms older than 6 hours
        if current_time - room["created_at"] > 21600:
            expired_rooms.append(code)

    for code in expired_rooms:
        del GAME_ROOMS[code]


cleanup_rooms()


# ============================================================
# SESSION STATE
# ============================================================

if "screen" not in st.session_state:
    st.session_state.screen = "welcome"

if "room_code" not in st.session_state:
    st.session_state.room_code = None

if "player_name" not in st.session_state:
    st.session_state.player_name = None

if "player_role" not in st.session_state:
    st.session_state.player_role = None


# ============================================================
# GENERATE ROOM CODE
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

        if code not in GAME_ROOMS:
            return code


# ============================================================
# CREATE ROOM
# ============================================================

def create_room(host_name):

    room_code = generate_room_code()

    GAME_ROOMS[room_code] = {

        "host": host_name,

        "player": None,

        "board": chess.Board(),

        "created_at": time.time(),

        "last_activity": time.time(),

        "game_over": False,

        "winner": None,

        "resigned_by": None,

        "last_move": None,

        "move_number": 0
    }

    return room_code


# ============================================================
# RESET GAME
# ============================================================

def reset_game(room):

    room["board"] = chess.Board()

    room["game_over"] = False

    room["winner"] = None

    room["resigned_by"] = None

    room["last_move"] = None

    room["move_number"] = 0

    room["last_activity"] = time.time()


# ============================================================
# RETURN HOME
# ============================================================

def return_home():

    st.session_state.screen = "welcome"

    st.session_state.room_code = None

    st.session_state.player_name = None

    st.session_state.player_role = None

    st.rerun()


# ============================================================
# WELCOME SCREEN
# ============================================================

def welcome_screen():

    st.title("♟️ Private Chess")

    st.markdown(
        """
        ### Play chess with anyone, anywhere.

        No account.  
        No login.  
        No registration.

        Create a private room and share the code with your opponent.
        """
    )

    st.divider()

    st.subheader("How do you want to play?")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 👑 Host")

        st.write(
            "Create a private room and invite another player."
        )

        if st.button(
            "Create Room",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.screen = "host"

            st.rerun()

    with col2:

        st.markdown("### ♟️ Player")

        st.write(
            "Join an existing room using its code."
        )

        if st.button(
            "Join Room",
            use_container_width=True
        ):

            st.session_state.screen = "player"

            st.rerun()


# ============================================================
# HOST SCREEN
# ============================================================

def host_screen():

    st.title("👑 Create Private Room")

    name = st.text_input(
        "Your name",
        max_chars=20,
        placeholder="Enter your name"
    )

    if st.button(
        "Create Private Room",
        type="primary",
        use_container_width=True
    ):

        name = name.strip()

        if not name:

            st.warning("Please enter your name.")

            return

        room_code = create_room(name)

        st.session_state.player_name = name

        st.session_state.player_role = "host"

        st.session_state.room_code = room_code

        st.session_state.screen = "waiting"

        st.rerun()

    st.divider()

    if st.button("← Back"):

        return_home()


# ============================================================
# WAITING ROOM
# ============================================================

def waiting_screen():

    room_code = st.session_state.room_code

    if not room_code:

        return_home()

        return

    if room_code not in GAME_ROOMS:

        st.error(
            "This room no longer exists."
        )

        if st.button(
            "Return Home",
            use_container_width=True
        ):

            return_home()

        return

    room = GAME_ROOMS[room_code]

    room["last_activity"] = time.time()

    st.title("♟️ Waiting for Opponent")

    st.success(
        "Your private chess room is ready!"
    )

    st.markdown("### Room Code")

    st.code(
        room_code,
        language=None
    )

    st.markdown(
        "Share this code with your opponent."
    )

    st.info(
        "Your opponent should choose "
        "**Player → Join Room** and enter this code."
    )

    st.divider()

    st.markdown(
        f"**Host:** {room['host']}"
    )

    if room["player"] is None:

        st.warning(
            "Waiting for opponent to join..."
        )

        st_autorefresh(
            interval=1000,
            key="waiting_room_refresh"
        )

    else:

        st.success(
            f"Opponent joined: {room['player']}"
        )

        time.sleep(0.5)

        st.session_state.screen = "game"

        st.rerun()

    st.divider()

    if st.button(
        "Cancel Room",
        use_container_width=True
    ):

        if room_code in GAME_ROOMS:

            del GAME_ROOMS[room_code]

        return_home()


# ============================================================
# PLAYER JOIN SCREEN
# ============================================================

def player_screen():

    st.title("♟️ Join Private Room")

    name = st.text_input(
        "Your name",
        max_chars=20,
        placeholder="Enter your name"
    )

    room_code = st.text_input(
        "Room code",
        max_chars=6,
        placeholder="Example: A7K92P"
    ).upper().strip()

    if st.button(
        "Join Game",
        type="primary",
        use_container_width=True
    ):

        name = name.strip()

        if not name:

            st.warning("Please enter your name.")

            return

        if not room_code:

            st.warning("Please enter the room code.")

            return

        if room_code not in GAME_ROOMS:

            st.error(
                "Room not found. Please check the code."
            )

            return

        room = GAME_ROOMS[room_code]

        if room["player"] is not None:

            st.error(
                "This room already has two players."
            )

            return

        if name.lower() == room["host"].lower():

            st.error(
                "Please use a different name from the host."
            )

            return

        room["player"] = name

        room["last_activity"] = time.time()

        st.session_state.player_name = name

        st.session_state.player_role = "player"

        st.session_state.room_code = room_code

        st.session_state.screen = "game"

        st.rerun()

    st.divider()

    if st.button("← Back"):

        return_home()


# ============================================================
# BOARD DISPLAY
# ============================================================

def display_board(room):

    board = room["board"]

    if st.session_state.player_role == "player":

        orientation = chess.BLACK

    else:

        orientation = chess.WHITE

    board_svg = chess.svg.board(
        board=board,
        orientation=orientation,
        size=650
    )

    st.image(
        board_svg,
        use_container_width=True
    )


# ============================================================
# MOVE HISTORY
# ============================================================

def get_move_history(board):

    if not board.move_stack:

        return []

    temp_board = chess.Board()

    history = []

    for index, move in enumerate(board.move_stack):

        san = temp_board.san(move)

        move_number = index // 2 + 1

        if index % 2 == 0:

            history.append(
                f"{move_number}. {san}"
            )

        else:

            history[-1] += f" {san}"

        temp_board.push(move)

    return history


# ============================================================
# GAME RESULT CHECK
# ============================================================

def update_game_result(room):

    board = room["board"]

    if board.is_checkmate():

        room["game_over"] = True

        # Board turn is the player who is checkmated
        if board.turn == chess.WHITE:

            room["winner"] = room["player"]

        else:

            room["winner"] = room["host"]

    elif board.is_stalemate():

        room["game_over"] = True

        room["winner"] = None

    elif board.is_insufficient_material():

        room["game_over"] = True

        room["winner"] = None

    elif board.is_fivefold_repetition():

        room["game_over"] = True

        room["winner"] = None

    elif board.is_seventyfive_moves():

        room["game_over"] = True

        room["winner"] = None


# ============================================================
# GAME SCREEN
# ============================================================

def game_screen():

    room_code = st.session_state.room_code

    if not room_code:

        return_home()

        return

    if room_code not in GAME_ROOMS:

        st.error(
            "Room no longer exists."
        )

        if st.button(
            "Return Home",
            use_container_width=True
        ):

            return_home()

        return

    room = GAME_ROOMS[room_code]

    room["last_activity"] = time.time()

    board = room["board"]

    my_name = st.session_state.player_name

    # --------------------------------------------------------
    # COLORS
    # --------------------------------------------------------

    if st.session_state.player_role == "host":

        my_color = chess.WHITE

        opponent_name = room["player"]

    else:

        my_color = chess.BLACK

        opponent_name = room["host"]

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("♟️ Private Chess")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"### ♔ {room['host']}"
        )

        st.caption("WHITE")

    with col2:

        if room["player"]:

            st.markdown(
                f"### ♚ {room['player']}"
            )

        else:

            st.markdown(
                "### ♚ Waiting..."
            )

        st.caption("BLACK")

    st.divider()

    # --------------------------------------------------------
    # GAME STATUS
    # --------------------------------------------------------

    if room["game_over"]:

        if room["resigned_by"]:

            if room["resigned_by"] == room["host"]:

                winner = room["player"]

            else:

                winner = room["host"]

            st.success(
                f"🏆 {winner} wins by resignation!"
            )

        elif room["winner"]:

            st.success(
                f"🏆 {room['winner']} wins!"
            )

        else:

            st.info(
                "🤝 Game drawn!"
            )

    else:

        if board.turn == chess.WHITE:

            turn_name = room["host"]

        else:

            turn_name = room["player"]

        if turn_name == my_name:

            st.success(
                "🟢 Your turn"
            )

        else:

            st.warning(
                f"🟡 Waiting for {turn_name}"
            )

        if board.is_check():

            st.error(
                "⚠️ CHECK!"
            )

    # --------------------------------------------------------
    # BOARD
    # --------------------------------------------------------

    display_board(room)

    # --------------------------------------------------------
    # MOVE INPUT
    # --------------------------------------------------------

    if not room["game_over"]:

        st.subheader("Make Your Move")

        move_input = st.text_input(
            "Move",
            placeholder="Example: e2e4",
            key=f"move_input_{room_code}_{room['move_number']}"
        )

        st.caption(
            "Enter moves using coordinates, e.g. e2e4 or g1f3."
        )

        if st.button(
            "Make Move",
            type="primary",
            use_container_width=True
        ):

            # Check whether player has joined
            if room["player"] is None:

                st.warning(
                    "Waiting for an opponent."
                )

                return

            # Check turn
            if board.turn != my_color:

                st.error(
                    "It is not your turn."
                )

                return

            move_input = move_input.strip().lower()

            # ------------------------------------------------
            # PARSE MOVE
            # ------------------------------------------------

            try:

                move = chess.Move.from_uci(
                    move_input
                )

            except ValueError:

                st.error(
                    "Invalid move format. "
                    "Example: e2e4"
                )

                return

            # ------------------------------------------------
            # LEGAL MOVE
            # ------------------------------------------------

            if move not in board.legal_moves:

                st.error(
                    "That is not a legal chess move."
                )

                return

            # ------------------------------------------------
            # MAKE MOVE
            # ------------------------------------------------

            board.push(move)

            room["last_move"] = move_input

            room["move_number"] += 1

            room["last_activity"] = time.time()

            update_game_result(room)

            st.rerun()

    # --------------------------------------------------------
    # MOVE HISTORY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📜 Move History")

    history = get_move_history(board)

    if history:

        for move in history:

            st.write(move)

    else:

        st.caption(
            "No moves have been played yet."
        )

    # --------------------------------------------------------
    # GAME CONTROLS
    # --------------------------------------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if not room["game_over"]:

            if st.button(
                "🏳️ Resign",
                use_container_width=True
            ):

                room["game_over"] = True

                room["resigned_by"] = my_name

                room["last_activity"] = time.time()

                st.rerun()

    with col2:

        if room["game_over"]:

            if st.button(
                "🔄 Rematch",
                use_container_width=True
            ):

                reset_game(room)

                st.rerun()

    # --------------------------------------------------------
    # ROOM INFO
    # --------------------------------------------------------

    st.divider()

    st.caption(
        f"Room: {room_code}"
    )

    st.caption(
        f"Moves played: {room['move_number']}"
    )

    # --------------------------------------------------------
    # LEAVE GAME
    # --------------------------------------------------------

    if st.button(
        "Leave Game",
        use_container_width=True
    ):

        # Host leaving destroys the room
        if st.session_state.player_role == "host":

            if room_code in GAME_ROOMS:

                del GAME_ROOMS[room_code]

        else:

            # Player leaving only removes player
            if room_code in GAME_ROOMS:

                GAME_ROOMS[room_code]["player"] = None

        return_home()

    # --------------------------------------------------------
    # AUTO REFRESH
    # --------------------------------------------------------

    st_autorefresh(
        interval=1000,
        key=f"game_refresh_{room_code}"
    )


# ============================================================
# APPLICATION ROUTER
# ============================================================

if st.session_state.screen == "welcome":

    welcome_screen()

elif st.session_state.screen == "host":

    host_screen()

elif st.session_state.screen == "player":

    player_screen()

elif st.session_state.screen == "waiting":

    waiting_screen()

elif st.session_state.screen == "game":

    game_screen()
