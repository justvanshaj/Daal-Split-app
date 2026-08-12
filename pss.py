import streamlit as st
import chess
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
# SHARED SERVER MEMORY
# ============================================================

@st.cache_resource
def get_game_rooms():
    return {}


GAME_ROOMS = get_game_rooms()


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

if "selected_square" not in st.session_state:
    st.session_state.selected_square = None


# ============================================================
# ROOM CODE
# ============================================================

def generate_room_code():

    chars = string.ascii_uppercase + string.digits

    while True:

        code = "".join(
            random.choices(chars, k=6)
        )

        if code not in GAME_ROOMS:
            return code


# ============================================================
# CREATE ROOM
# ============================================================

def create_room(host_name):

    code = generate_room_code()

    GAME_ROOMS[code] = {

        "host": host_name,

        "player": None,

        "board": chess.Board(),

        "created_at": time.time(),

        "last_activity": time.time(),

        "game_over": False,

        "winner": None,

        "draw_reason": None,

        "resigned_by": None,

        "last_move": None,

        "move_number": 0,

        "version": 0
    }

    return code


# ============================================================
# RESET GAME
# ============================================================

def reset_game(room):

    room["board"] = chess.Board()

    room["game_over"] = False
    room["winner"] = None
    room["draw_reason"] = None
    room["resigned_by"] = None
    room["last_move"] = None
    room["move_number"] = 0
    room["version"] += 1
    room["last_activity"] = time.time()

    st.session_state.selected_square = None


# ============================================================
# HOME
# ============================================================

def return_home():

    st.session_state.screen = "welcome"
    st.session_state.room_code = None
    st.session_state.player_name = None
    st.session_state.player_role = None
    st.session_state.selected_square = None

    st.rerun()


# ============================================================
# WELCOME
# ============================================================

def welcome_screen():

    st.title("♟️ Private Chess")

    st.markdown(
        """
        ### Play chess with anyone, anywhere.

        No account • No login • No registration
        """
    )

    st.divider()

    st.subheader("Choose how you want to play")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 👑 Host")

        st.write("Create a private room.")

        if st.button(
            "Create Room",
            type="primary",
            use_container_width=True
        ):

            st.session_state.screen = "host"
            st.rerun()

    with col2:

        st.markdown("### ♟️ Player")

        st.write("Join using a room code.")

        if st.button(
            "Join Room",
            use_container_width=True
        ):

            st.session_state.screen = "player"
            st.rerun()


# ============================================================
# HOST
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

        code = create_room(name)

        st.session_state.player_name = name
        st.session_state.player_role = "host"
        st.session_state.room_code = code
        st.session_state.screen = "waiting"

        st.rerun()

    st.divider()

    if st.button("← Back"):

        return_home()


# ============================================================
# WAITING ROOM
# ============================================================

def waiting_screen():

    code = st.session_state.room_code

    if not code or code not in GAME_ROOMS:

        st.error("This room no longer exists.")

        if st.button("Return Home"):
            return_home()

        return

    room = GAME_ROOMS[code]

    room["last_activity"] = time.time()

    st.title("♟️ Private Chess Room")

    st.success("Room created!")

    st.subheader("Share this code")

    st.code(code)

    st.info(
        "Your opponent should choose "
        "**Player → Join Room** and enter this code."
    )

    st.write(f"👑 Host: **{room['host']}**")

    if room["player"] is None:

        st.warning(
            "Waiting for your opponent..."
        )

        st_autorefresh(
            interval=1000,
            key="waiting_refresh"
        )

    else:

        st.success(
            f"♟️ {room['player']} joined the game!"
        )

        st.session_state.screen = "game"

        st.rerun()

    st.divider()

    if st.button(
        "Cancel Room",
        use_container_width=True
    ):

        if code in GAME_ROOMS:
            del GAME_ROOMS[code]

        return_home()


# ============================================================
# PLAYER JOIN
# ============================================================

def player_screen():

    st.title("♟️ Join Private Room")

    name = st.text_input(
        "Your name",
        max_chars=20,
        placeholder="Enter your name"
    )

    code = st.text_input(
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

        if not code:

            st.warning("Please enter the room code.")
            return

        if code not in GAME_ROOMS:

            st.error(
                "Room not found. Please check the code."
            )

            return

        room = GAME_ROOMS[code]

        if room["player"] is not None:

            st.error(
                "This room already has two players."
            )

            return

        if name.lower() == room["host"].lower():

            st.error(
                "Please choose a different name."
            )

            return

        room["player"] = name
        room["last_activity"] = time.time()
        room["version"] += 1

        st.session_state.player_name = name
        st.session_state.player_role = "player"
        st.session_state.room_code = code
        st.session_state.screen = "game"

        st.rerun()

    st.divider()

    if st.button("← Back"):

        return_home()


# ============================================================
# PIECES
# ============================================================

PIECES = {

    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",

    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚"
}


# ============================================================
# BOARD CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Chess board buttons */

    div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }

    .chess-square button {
        border-radius: 0 !important;
        min-height: 65px !important;
        height: 65px !important;
        padding: 0 !important;
        font-size: 42px !important;
        line-height: 1 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DRAW CLICKABLE BOARD
# ============================================================

def draw_board(room):

    board = room["board"]

    role = st.session_state.player_role

    if role == "host":

        # White perspective
        ranks = range(7, -1, -1)
        files = range(8)

    else:

        # Black perspective
        ranks = range(8)
        files = range(7, -1, -1)

    selected = st.session_state.selected_square

    legal_targets = set()

    if selected is not None:

        try:

            selected_square = chess.parse_square(selected)

            for move in board.legal_moves:

                if move.from_square == selected_square:

                    legal_targets.add(
                        chess.square_name(
                            move.to_square
                        )
                    )

        except ValueError:

            selected = None

    # --------------------------------------------------------
    # BOARD
    # --------------------------------------------------------

    for rank in ranks:

        columns = st.columns(8, gap="small")

        for index, file in enumerate(files):

            square = chess.square(
                file,
                rank
            )

            square_name = chess.square_name(
                square
            )

            piece = board.piece_at(square)

            if piece:

                symbol = PIECES[
                    piece.symbol()
                ]

            else:

                symbol = " "

            # ------------------------------------------------
            # Square colour
            # ------------------------------------------------

            is_light = (
                (file + rank) % 2 == 0
            )

            if is_light:

                background = "#F0D9B5"

            else:

                background = "#B58863"

            # ------------------------------------------------
            # Selected square
            # ------------------------------------------------

            if square_name == selected:

                background = "#FFD54F"

            # ------------------------------------------------
            # Legal destination
            # ------------------------------------------------

            if square_name in legal_targets:

                background = "#90EE90"

            # ------------------------------------------------
            # Button styling
            # ------------------------------------------------

            text_color = (
                "#000000"
                if piece is None
                else "#111111"
            )

            button_html = f"""
            <style>
            div[data-testid="stButton"] button {{
                background: {background} !important;
                color: {text_color} !important;
                border: 1px solid rgba(0,0,0,0.15) !important;
            }}
            </style>
            """

            columns[index].markdown(
                button_html,
                unsafe_allow_html=True
            )

            # ------------------------------------------------
            # Click
            # ------------------------------------------------

            if columns[index].button(
                symbol,
                key=f"square_{room['version']}_{square_name}",
                use_container_width=True
            ):

                handle_square_click(
                    room,
                    square_name
                )


# ============================================================
# HANDLE SQUARE CLICK
# ============================================================

def handle_square_click(room, square_name):

    board = room["board"]

    # --------------------------------------------------------
    # GAME OVER
    # --------------------------------------------------------

    if room["game_over"]:
        return

    # --------------------------------------------------------
    # CHECK PLAYER TURN
    # --------------------------------------------------------

    if st.session_state.player_role == "host":

        my_color = chess.WHITE

    else:

        my_color = chess.BLACK

    if board.turn != my_color:

        return

    # --------------------------------------------------------
    # NO PIECE SELECTED
    # --------------------------------------------------------

    selected = st.session_state.selected_square

    if selected is None:

        piece = board.piece_at(
            chess.parse_square(square_name)
        )

        # Empty square
        if piece is None:
            return

        # Wrong colour
        if piece.color != my_color:
            return

        st.session_state.selected_square = square_name

        st.rerun()

    # --------------------------------------------------------
    # SAME SQUARE
    # --------------------------------------------------------

    if selected == square_name:

        st.session_state.selected_square = None

        st.rerun()

    # --------------------------------------------------------
    # SECOND CLICK = MOVE
    # --------------------------------------------------------

    try:

        from_square = chess.parse_square(
            selected
        )

        to_square = chess.parse_square(
            square_name
        )

        move = chess.Move(
            from_square,
            to_square
        )

    except ValueError:

        st.session_state.selected_square = None

        st.rerun()

        return

    # --------------------------------------------------------
    # PROMOTION
    # --------------------------------------------------------

    piece = board.piece_at(from_square)

    if piece and piece.piece_type == chess.PAWN:

        target_rank = chess.square_rank(
            to_square
        )

        if target_rank in (0, 7):

            # Automatically promote to queen
            move = chess.Move(
                from_square,
                to_square,
                promotion=chess.QUEEN
            )

    # --------------------------------------------------------
    # LEGAL MOVE
    # --------------------------------------------------------

    if move in board.legal_moves:

        # Save SAN before pushing
        san = board.san(move)

        board.push(move)

        room["last_move"] = san

        room["move_number"] += 1

        room["last_activity"] = time.time()

        room["version"] += 1

        check_game_status(room)

    # --------------------------------------------------------
    # INVALID MOVE
    # --------------------------------------------------------

    else:

        # If clicked another friendly piece,
        # select that piece instead.

        target_piece = board.piece_at(
            to_square
        )

        if (
            target_piece is not None
            and target_piece.color == my_color
        ):

            st.session_state.selected_square = (
                square_name
            )

            st.rerun()

            return

    # Clear selection
    st.session_state.selected_square = None

    st.rerun()


# ============================================================
# GAME STATUS
# ============================================================

def check_game_status(room):

    board = room["board"]

    if board.is_checkmate():

        room["game_over"] = True

        if board.turn == chess.WHITE:

            room["winner"] = room["player"]

        else:

            room["winner"] = room["host"]

        return

    if board.is_stalemate():

        room["game_over"] = True
        room["draw_reason"] = "Stalemate"

        return

    if board.is_insufficient_material():

        room["game_over"] = True
        room["draw_reason"] = "Draw"

        return

    if board.is_fivefold_repetition():

        room["game_over"] = True
        room["draw_reason"] = "Repetition"

        return

    if board.is_seventyfive_moves():

        room["game_over"] = True
        room["draw_reason"] = "75-move rule"


# ============================================================
# MOVE HISTORY
# ============================================================

def get_history(board):

    history = []

    temp = chess.Board()

    for index, move in enumerate(
        board.move_stack
    ):

        san = temp.san(move)

        move_number = index // 2 + 1

        if index % 2 == 0:

            history.append(
                f"{move_number}. {san}"
            )

        else:

            history[-1] += f" {san}"

        temp.push(move)

    return history


# ============================================================
# GAME SCREEN
# ============================================================

def game_screen():

    code = st.session_state.room_code

    if not code or code not in GAME_ROOMS:

        st.error(
            "Room no longer exists."
        )

        if st.button(
            "Return Home",
            use_container_width=True
        ):

            return_home()

        return

    room = GAME_ROOMS[code]

    room["last_activity"] = time.time()

    board = room["board"]

    my_name = st.session_state.player_name

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

        st.markdown(
            f"### ♚ {room['player']}"
        )

        st.caption("BLACK")

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    st.divider()

    if room["game_over"]:

        if room["resigned_by"]:

            if room["resigned_by"] == room["host"]:

                winner = room["player"]

            else:

                winner = room["host"]

            st.success(
                f"🏆 {winner} wins!"
            )

        elif room["winner"]:

            st.success(
                f"🏆 {room['winner']} wins by checkmate!"
            )

        else:

            st.info(
                f"🤝 Draw — {room['draw_reason']}"
            )

    else:

        if board.turn == chess.WHITE:

            turn_name = room["host"]

        else:

            turn_name = room["player"]

        if turn_name == my_name:

            st.success(
                "🟢 Your turn — click a piece, then click where you want it to go."
            )

        else:

            st.info(
                f"🟡 Waiting for {turn_name}..."
            )

        if board.is_check():

            st.warning("⚠️ Check!")

    # --------------------------------------------------------
    # INSTRUCTIONS
    # --------------------------------------------------------

    st.caption(
        "♟️ Click a piece → click its destination"
    )

    # --------------------------------------------------------
    # BOARD
    # --------------------------------------------------------

    draw_board(room)

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📜 Move History")

    history = get_history(board)

    if history:

        for move in history:

            st.write(move)

    else:

        st.caption("No moves yet.")

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    st.divider()

    if not room["game_over"]:

        if st.button(
            "🏳️ Resign",
            use_container_width=True
        ):

            room["game_over"] = True
            room["resigned_by"] = my_name
            room["version"] += 1

            st.session_state.selected_square = None

            st.rerun()

    else:

        if st.button(
            "🔄 Rematch",
            type="primary",
            use_container_width=True
        ):

            reset_game(room)

            st.rerun()

    # --------------------------------------------------------
    # ROOM
    # --------------------------------------------------------

    st.divider()

    st.caption(f"Room: {code}")

    st.caption(
        f"Moves played: {room['move_number']}"
    )

    # --------------------------------------------------------
    # LEAVE
    # --------------------------------------------------------

    if st.button(
        "Leave Game",
        use_container_width=True
    ):

        if st.session_state.player_role == "host":

            if code in GAME_ROOMS:
                del GAME_ROOMS[code]

        else:

            if code in GAME_ROOMS:

                GAME_ROOMS[code]["player"] = None
                GAME_ROOMS[code]["version"] += 1

        return_home()

    # --------------------------------------------------------
    # AUTO REFRESH
    # --------------------------------------------------------

    st_autorefresh(
        interval=1000,
        key=f"game_refresh_{code}"
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
