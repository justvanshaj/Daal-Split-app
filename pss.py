import streamlit as st
import streamlit.components.v1 as components
import chess
import random
import string
import time
import html

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

defaults = {
    "screen": "welcome",
    "room_code": None,
    "player_name": None,
    "player_role": None,
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
            random.choices(characters, k=6)
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

        "version": 0,
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

    room["last_activity"] = time.time()

    room["version"] += 1


# ============================================================
# CLEAN OLD ROOMS
# ============================================================

def cleanup_rooms():

    now = time.time()

    expired = []

    for code, room in GAME_ROOMS.items():

        if now - room["last_activity"] > 21600:
            expired.append(code)

    for code in expired:

        del GAME_ROOMS[code]


cleanup_rooms()


# ============================================================
# HOME
# ============================================================

def return_home():

    st.session_state.screen = "welcome"
    st.session_state.room_code = None
    st.session_state.player_name = None
    st.session_state.player_role = None

    st.rerun()


# ============================================================
# WELCOME
# ============================================================

def welcome_screen():

    st.title("♟️ Private Chess")

    st.markdown(
        """
        ### Play chess with anyone, anywhere.

        No account.  
        No login.  
        No registration.

        Create a private room and share the code.
        """
    )

    st.divider()

    st.subheader("Choose how you want to play")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 👑 Host")

        st.write(
            "Create a private room."
        )

        if st.button(
            "Create Room",
            type="primary",
            use_container_width=True
        ):

            st.session_state.screen = "host"

            st.rerun()

    with col2:

        st.markdown("### ♟️ Player")

        st.write(
            "Join a room using a room code."
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

        if st.button(
            "Return Home",
            use_container_width=True
        ):
            return_home()

        return

    room = GAME_ROOMS[code]

    room["last_activity"] = time.time()

    st.title("♟️ Your Private Room")

    st.success("Room created successfully!")

    st.subheader("Share this code")

    st.code(code)

    st.info(
        "Your opponent should choose "
        "**Player → Join Room** and enter this code."
    )

    st.write(
        f"👑 Host: **{room['host']}**"
    )

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
            f"♟️ {room['player']} joined!"
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
# PLAYER SCREEN
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
# CHESS PIECES
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
    "k": "♚",
}


# ============================================================
# BOARD DATA
# ============================================================

def board_to_data(board):

    data = []

    for rank in range(7, -1, -1):

        row = []

        for file in range(8):

            square = chess.square(file, rank)

            piece = board.piece_at(square)

            if piece:

                row.append({
                    "square": chess.square_name(square),
                    "piece": PIECES[piece.symbol()],
                    "color": "white" if piece.color else "black",
                })

            else:

                row.append({
                    "square": chess.square_name(square),
                    "piece": "",
                    "color": "",
                })

        data.append(row)

    return data


# ============================================================
# INTERACTIVE CHESSBOARD
# ============================================================

def interactive_board(room):

    board = room["board"]

    if st.session_state.player_role == "host":

        orientation = "white"

    else:

        orientation = "black"

    board_data = board_to_data(board)

    board_json = str(board_data)

    # Convert Python representation to safe JS data
    import json

    board_json = json.dumps(board_data)

    component_code = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: Arial, sans-serif;
}}

.board-wrapper {{
    width: min(92vw, 620px);
    margin: auto;
}}

.board {{
    width: 100%;
    aspect-ratio: 1 / 1;

    display: grid;
    grid-template-columns: repeat(8, 1fr);

    border-radius: 8px;
    overflow: hidden;

    box-shadow:
        0 4px 18px rgba(0,0,0,0.20);
}}

.square {{
    position: relative;

    display: flex;
    align-items: center;
    justify-content: center;

    cursor: pointer;

    user-select: none;

    font-size: clamp(32px, 8vw, 68px);

    transition: filter 0.1s;
}}

.square:hover {{
    filter: brightness(1.08);
}}

.light {{
    background: #f0d9b5;
}}

.dark {{
    background: #b58863;
}}

.selected {{
    box-shadow:
        inset 0 0 0 5px #ffd54f;
}}

.possible {{
    box-shadow:
        inset 0 0 0 5px rgba(60, 180, 75, 0.8);
}}

.possible::after {{
    content: "";
    position: absolute;

    width: 24%;
    height: 24%;

    border-radius: 50%;

    background: rgba(40, 160, 70, 0.75);
}}

.capture {{
    box-shadow:
        inset 0 0 0 5px rgba(220, 60, 60, 0.9);
}}

.rank {{
    position: absolute;
    top: 3px;
    left: 5px;

    font-size: 12px;
    font-weight: bold;

    opacity: 0.65;
}}

.file {{
    position: absolute;
    bottom: 2px;
    right: 5px;

    font-size: 12px;
    font-weight: bold;

    opacity: 0.65;
}}

.white-piece {{
    color: #ffffff;

    text-shadow:
        0 2px 2px #000,
        0 0 2px #000;
}}

.black-piece {{
    color: #111111;

    text-shadow:
        0 1px 1px rgba(255,255,255,0.5);
}}

</style>

</head>

<body>

<div class="board-wrapper">

<div id="board" class="board"></div>

</div>

<script>

const boardData = {board_json};

const orientation = "{orientation}";

let selectedSquare = null;

let possibleSquares = [];

const files = ["a","b","c","d","e","f","g","h"];

const ranks = ["8","7","6","5","4","3","2","1"];

function findSquare(square) {{

    for (const row of boardData) {{

        for (const cell of row) {{

            if (cell.square === square) {{
                return cell;
            }}

        }}

    }}

    return null;
}}

function renderBoard() {{

    const board = document.getElementById("board");

    board.innerHTML = "";

    let displayFiles = [...files];

    let displayRanks = [...ranks];

    if (orientation === "black") {{

        displayFiles.reverse();
        displayRanks.reverse();

    }}

    for (let rankIndex = 0; rankIndex < 8; rankIndex++) {{

        for (let fileIndex = 0; fileIndex < 8; fileIndex++) {{

            const file = displayFiles[fileIndex];

            const rank = displayRanks[rankIndex];

            const squareName = file + rank;

            const fileNumber = files.indexOf(file);

            const rankNumber = parseInt(rank);

            const isLight =
                (fileNumber + rankNumber) % 2 === 1;

            const square = document.createElement("div");

            square.className =
                "square " +
                (isLight ? "light" : "dark");

            if (selectedSquare === squareName) {{
                square.classList.add("selected");
            }}

            if (possibleSquares.includes(squareName)) {{

                const target = findSquare(squareName);

                if (target && target.piece) {{
                    square.classList.add("capture");
                }} else {{
                    square.classList.add("possible");
                }}

            }}

            const cell = findSquare(squareName);

            if (cell && cell.piece) {{

                const piece = document.createElement("div");

                piece.textContent = cell.piece;

                piece.className =
                    cell.color === "white"
                    ? "white-piece"
                    : "black-piece";

                square.appendChild(piece);

            }}

            if (fileIndex === 0) {{

                const rankLabel =
                    document.createElement("span");

                rankLabel.className = "rank";

                rankLabel.textContent = rank;

                square.appendChild(rankLabel);

            }}

            if (rankIndex === 7) {{

                const fileLabel =
                    document.createElement("span");

                fileLabel.className = "file";

                fileLabel.textContent = file;

                square.appendChild(fileLabel);

            }}

            square.onclick = () => handleClick(squareName);

            board.appendChild(square);
        }}

    }}

}}

function handleClick(square) {{

    // First click
    if (selectedSquare === null) {{

        const cell = findSquare(square);

        if (!cell || !cell.piece) {{
            return;
        }}

        selectedSquare = square;

        // We don't know legal moves in browser.
        // Python will validate the attempted move.
        possibleSquares = [];

        renderBoard();

        // Send selection to Python
        window.parent.postMessage(
            {{
                type: "streamlit:setComponentValue",
                value: "select:" + square
            }},
            "*"
        );

        return;
    }}

    // Second click
    const move =
        selectedSquare + square;

    window.parent.postMessage(
        {{
            type: "streamlit:setComponentValue",
            value: "move:" + move
        }},
        "*"
    );

    selectedSquare = null;

    possibleSquares = [];

    renderBoard();

}}

renderBoard();

</script>

</body>

</html>
"""

    result = components.html(
        component_code,
        height=650,
        scrolling=False
    )

    return result


# ============================================================
# APPLY MOVE
# ============================================================

def apply_move(room, move_text):

    board = room["board"]

    try:

        move = chess.Move.from_uci(move_text)

    except ValueError:

        return False

    # Illegal move = simply ignore it.
    if move not in board.legal_moves:

        return False

    board.push(move)

    room["last_move"] = move_text
    room["move_number"] += 1
    room["last_activity"] = time.time()
    room["version"] += 1

    # Checkmate
    if board.is_checkmate():

        room["game_over"] = True

        if board.turn == chess.WHITE:
            room["winner"] = room["player"]
        else:
            room["winner"] = room["host"]

    # Draw
    elif board.is_stalemate():

        room["game_over"] = True
        room["draw_reason"] = "Stalemate"

    elif board.is_insufficient_material():

        room["game_over"] = True
        room["draw_reason"] = "Insufficient material"

    elif board.is_seventyfive_moves():

        room["game_over"] = True
        room["draw_reason"] = "75-move rule"

    elif board.is_fivefold_repetition():

        room["game_over"] = True
        room["draw_reason"] = "Fivefold repetition"

    return True


# ============================================================
# MOVE HISTORY
# ============================================================

def get_history(board):

    history = []

    temp = chess.Board()

    for index, move in enumerate(board.move_stack):

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

    if st.session_state.player_role == "host":

        my_color = chess.WHITE

    else:

        my_color = chess.BLACK

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
                f"🏆 {winner} wins by resignation!"
            )

        elif room["winner"]:

            st.success(
                f"🏆 {room['winner']} wins!"
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
                "🟢 Your turn — click a piece, then click where you want to move it."
            )

        else:

            st.info(
                f"🟡 Waiting for {turn_name}..."
            )

        if board.is_check():

            st.warning(
                "⚠️ Check!"
            )

    # --------------------------------------------------------
    # INTERACTIVE BOARD
    # --------------------------------------------------------

    result = interactive_board(room)

    # --------------------------------------------------------
    # PROCESS CLICK
    # --------------------------------------------------------

    if result:

        if isinstance(result, str):

            if result.startswith("move:"):

                move_text = result.replace(
                    "move:",
                    "",
                    1
                )

                # Only allow the correct player to move
                if not room["game_over"]:

                    if board.turn == my_color:

                        apply_move(
                            room,
                            move_text
                        )

                        st.rerun()

    # --------------------------------------------------------
    # MOVE HISTORY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📜 Moves")

    history = get_history(board)

    if history:

        for move in history:

            st.write(move)

    else:

        st.caption(
            "The game has not started yet."
        )

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
            room["last_activity"] = time.time()
            room["version"] += 1

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
    # ROOM INFORMATION
    # --------------------------------------------------------

    st.divider()

    st.caption(
        f"Room: {code}"
    )

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
