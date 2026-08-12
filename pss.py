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
# SERVER-SIDE ROOM STORAGE
# ============================================================

if "rooms" not in st.session_state:
    st.session_state.rooms = {}


# IMPORTANT:
# Streamlit session_state is per browser session.
# For a simple demo, we use a module-level dictionary.
#
# This dictionary is shared between users connected to
# the same Streamlit process.

if "initialized" not in st.session_state:
    st.session_state.initialized = True


# Module-level storage
if "GAME_ROOMS" not in globals():
    GAME_ROOMS = {}


# ============================================================
# ROOM CODE
# ============================================================

def generate_room_code(length=6):
    characters = string.ascii_uppercase + string.digits

    while True:
        code = "".join(random.choice(characters) for _ in range(length))

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

        "host_color": "white",
        "player_color": "black",

        "board": chess.Board(),

        "created_at": time.time(),

        "winner": None,
        "game_over": False,

        "resigned_by": None,

        "last_move": None,

        "move_number": 0
    }

    return room_code


# ============================================================
# RESET ROOM
# ============================================================

def reset_game(room):

    room["board"] = chess.Board()
    room["winner"] = None
    room["game_over"] = False
    room["resigned_by"] = None
    room["last_move"] = None
    room["move_number"] = 0


# ============================================================
# CLEAN OLD ROOMS
# ============================================================

def cleanup_rooms():

    current_time = time.time()

    expired_rooms = []

    for code, room in GAME_ROOMS.items():

        # Remove rooms older than 6 hours
        if current_time - room["created_at"] > 21600:
            expired_rooms.append(code)

    for code in expired_rooms:
        del GAME_ROOMS[code]


cleanup_rooms()


# ============================================================
# SESSION VARIABLES
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
# WELCOME SCREEN
# ============================================================

def welcome_screen():

    st.title("♟️ Private Chess")

    st.markdown(
        """
        ### Play chess with a friend anywhere in the world.

        No account required.
        No login required.
        Just create a private room and share the code.
        """
    )

    st.divider()

    st.subheader("Choose your role")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # HOST
    # --------------------------------------------------------

    with col1:

        st.markdown("### 👑 Host")

        st.write(
            "Create a private room and share the room code."
        )

        if st.button(
            "Create Room",
            use_container_width=True
        ):

            st.session_state.screen = "host"

            st.rerun()

    # --------------------------------------------------------
    # PLAYER
    # --------------------------------------------------------

    with col2:

        st.markdown("### ♟️ Player")

        st.write(
            "Join a room using the code given by the host."
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

    st.title("👑 Create Chess Room")

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

        if not name.strip():

            st.warning("Please enter your name.")

            return

        room_code = create_room(name.strip())

        st.session_state.player_name = name.strip()
        st.session_state.player_role = "host"
        st.session_state.room_code = room_code
        st.session_state.screen = "waiting"

        st.rerun()

    st.divider()

    if st.button("← Back"):

        st.session_state.screen = "welcome"

        st.rerun()


# ============================================================
# WAITING SCREEN
# ============================================================

def waiting_screen():

    room_code = st.session_state.room_code

    if room_code not in GAME_ROOMS:

        st.error("Room no longer exists.")

        if st.button("Return Home"):

            st.session_state.screen = "welcome"
            st.rerun()

        return

    room = GAME_ROOMS[room_code]

    st.title("♟️ Your Chess Room")

    st.success("Room created successfully!")

    st.markdown("### Share this room code")

    st.code(room_code, language=None)

    st.info(
        "Send this code to your opponent. "
        "They can enter it from anywhere."
    )

    st.markdown(
        f"**Host:** {room['host']}"
    )

    if room["player"] is None:

        st.warning(
            "Waiting for your opponent to join..."
        )

        # Refresh every second
        st_autorefresh(
            interval=1000,
            key="waiting_refresh"
        )

    else:

        st.success(
            f"Opponent joined: {room['player']}"
        )

        st.session_state.screen = "game"

        st.rerun()


# ============================================================
# PLAYER JOIN SCREEN
# ============================================================

def player_screen():

    st.title("♟️ Join Chess Room")

    name = st.text_input(
        "Your name",
        max_chars=20,
        placeholder="Enter your name"
    )

    room_code = st.text_input(
        "Room code",
        max_chars=6,
        placeholder="Example: A7K92P"
    ).upper()

    if st.button(
        "Join Game",
        type="primary",
        use_container_width=True
    ):

        if not name.strip():

            st.warning("Please enter your name.")

            return

        if not room_code:

            st.warning("Please enter the room code.")

            return

        if room_code not in GAME_ROOMS:

            st.error(
                "Room not found. Check the room code."
            )

            return

        room = GAME_ROOMS[room_code]

        if room["player"] is not None:

            st.error(
                "This room already has two players."
            )

            return

        if name.strip().lower() == room["host"].lower():

            st.error(
                "Player name must be different from the host."
            )

            return

        room["player"] = name.strip()

        st.session_state.player_name = name.strip()
        st.session_state.player_role = "player"
        st.session_state.room_code = room_code
        st.session_state.screen = "game"

        st.rerun()

    st.divider()

    if st.button("← Back"):

        st.session_state.screen = "welcome"

        st.rerun()


# ============================================================
# DRAW BOARD
# ============================================================

def draw_board(room):

    board = room["board"]

    # Board orientation
    if st.session_state.player_role == "player":

        svg = chess.svg.board(
            board=board,
            size=600,
            orientation=chess.BLACK
        )

    else:

        svg = chess.svg.board(
            board=board,
            size=600,
            orientation=chess.WHITE
        )

    st.image(
        svg,
        use_container_width=True
    )


# ============================================================
# GAME SCREEN
# ============================================================

def game_screen():

    room_code = st.session_state.room_code

    if room_code not in GAME_ROOMS:

        st.error("This room no longer exists.")

        return

    room = GAME_ROOMS[room_code]

    board = room["board"]

    my_name = st.session_state.player_name

    # --------------------------------------------------------
    # DETERMINE COLOR
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

        st.caption("White")

    with col2:

        if room["player"]:

            st.markdown(
                f"### ♚ {room['player']}"
            )

        else:

            st.markdown("### Waiting...")

        st.caption("Black")

    st.divider()

    # --------------------------------------------------------
    # GAME STATUS
    # --------------------------------------------------------

    if room["game_over"]:

        if room["winner"]:

            st.success(
                f"🏆 {room['winner']} wins!"
            )

        elif room["resigned_by"]:

            if room["resigned_by"] == room["host"]:

                winner = room["player"]

            else:

                winner = room["host"]

            st.success(
                f"🏆 {winner} wins by resignation!"
            )

    else:

        if board.turn == chess.WHITE:

            turn_name = room["host"]

        else:

            turn_name = room["player"]

        if turn_name == my_name:

            st.info("🟢 Your turn")

        else:

            st.warning(
                f"🟡 Waiting for {turn_name}"
            )

    # --------------------------------------------------------
    # BOARD
    # --------------------------------------------------------

    draw_board(room)

    # --------------------------------------------------------
    # MOVE INPUT
    # --------------------------------------------------------

    if not room["game_over"]:

        st.subheader("Make a move")

        move_text = st.text_input(
            "Enter move",
            placeholder="Example: e2e4",
            key=f"move_{room_code}"
        )

        if st.button(
            "Make Move",
            use_container_width=True
        ):

            # Check turn
            if board.turn != my_color:

                st.error("It is not your turn.")

                return

            move_text = move_text.strip()

            try:

                move = chess.Move.from_uci(
                    move_text
                )

            except ValueError:

                st.error(
                    "Invalid move format. "
                    "Use format like e2e4."
                )

                return

            if move not in board.legal_moves:

                st.error("Illegal chess move.")

                return

            # Make move
            board.push(move)

            room["last_move"] = move_text

            room["move_number"] += 1

            # Check game result
            if board.is_checkmate():

                room["game_over"] = True

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

            st.rerun()

    # --------------------------------------------------------
    # RESIGN
    # --------------------------------------------------------

    if not room["game_over"]:

        st.divider()

        if st.button(
            "🏳️ Resign Game",
            use_container_width=True
        ):

            room["game_over"] = True

            room["resigned_by"] = my_name

            st.rerun()

    # --------------------------------------------------------
    # GAME INFORMATION
    # --------------------------------------------------------

    st.divider()

    st.subheader("Game Information")

    st.write(
        f"Room: `{room_code}`"
    )

    if room["last_move"]:

        st.write(
            f"Last move: `{room['last_move']}`"
        )

    st.write(
        f"Moves played: {room['move_number']}"
    )

    # --------------------------------------------------------
    # MOVE HISTORY
    # --------------------------------------------------------

    st.subheader("Move History")

    if board.move_stack:

        history = []

        temp_board = chess.Board()

        for index, move in enumerate(
            board.move_stack
        ):

            san = temp_board.san(move)

            move_number = index // 2 + 1

            if index % 2 == 0:

                history.append(
                    f"{move_number}. {san}"
                )

            else:

                history[-1] += f" {san}"

            temp_board.push(move)

        for move in history:

            st.write(move)

    else:

        st.caption("No moves yet.")

    # --------------------------------------------------------
    # REMATCH
    # --------------------------------------------------------

    if room["game_over"]:

        st.divider()

        if st.button(
            "🔄 Rematch",
            use_container_width=True
        ):

            reset_game(room)

            st.rerun()

    # --------------------------------------------------------
    # AUTO REFRESH
    # --------------------------------------------------------

    st_autorefresh(
        interval=1000,
        key=f"game_refresh_{room_code}"
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

elif st.session_state.screen == "waiting":

    waiting_screen()

elif st.session_state.screen == "game":

    game_screen()
