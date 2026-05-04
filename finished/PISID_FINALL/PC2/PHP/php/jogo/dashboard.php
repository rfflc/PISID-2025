<?php
session_start();
if (!isset($_SESSION['username'])) {
    header("Location: index.php");
    exit();
}

$conn = new mysqli($_SESSION['server_ip'], "root", "", "pisid", $_SESSION['server_port']);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle game updates
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['description'])) {
        // Create new game
        $description = $_POST['description'];
        $user_id = $_SESSION['user_id'];
        $stmt = $conn->prepare("INSERT INTO jogo (idutilizador, descricao, estado) VALUES (?, ?, 'por_iniciar')");
        $stmt->bind_param("is", $user_id, $description);
        $stmt->execute();
        $stmt->close();
        header("Location: dashboard.php");
        exit();
    } elseif (isset($_POST['update_game'])) {
        // Update existing game
        $game_id = $_POST['game_id'];
        $description = $_POST['edit_description'];
        $stmt = $conn->prepare("UPDATE jogo SET descricao = ? WHERE idjogo = ? AND idutilizador = ?");
        $stmt->bind_param("sii", $description, $game_id, $_SESSION['user_id']);
        $stmt->execute();
        $stmt->close();
        header("Location: dashboard.php");
        exit();
    } elseif (isset($_POST['delete_game'])) {
        // Delete game
        $game_id = $_POST['game_id'];
        $stmt = $conn->prepare("DELETE FROM jogo WHERE idjogo = ? AND idutilizador = ? AND estado = 'por_iniciar'");
        $stmt->bind_param("ii", $game_id, $_SESSION['user_id']);
        $stmt->execute();
        $stmt->close();
        header("Location: dashboard.php");
        exit();
    } elseif (isset($_POST['start_game'])) {
        // Start game
        $game_id = $_POST['game_id'];
        $stmt = $conn->prepare("UPDATE jogo SET estado = 'ativo', inicio = NOW() WHERE idjogo = ? AND idutilizador = ? AND estado = 'por_iniciar'");
        $stmt->bind_param("ii", $game_id, $_SESSION['user_id']);
        $stmt->execute();
        $stmt->close();
        $group = $_SESSION['group']; 
        #$p = popen('start "" cmd /K init_jogo.bat ' . escapeshellarg($group), 'r');
        $p = popen('start "" cmd /K init_jogo.bat ' . escapeshellarg($game_id) . ' ' . escapeshellarg($group), 'r');
        pclose($p);
        header("Location: dashboard.php");
        exit();
    }
}

$user_id = $_SESSION['user_id'];
$stmt = $conn->prepare("SELECT idjogo, descricao, inicio, fim, estado FROM jogo WHERE idutilizador = ? ORDER BY idjogo DESC");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$result = $stmt->get_result();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Jogo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
        }

        .header {
            background-color: white;
            padding: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .user-info {
            font-size: 1.1rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .new-game-btn {
            background-color: #1a73e8;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }

        .delete-btn {
            background-color: #dc3545;
        }

        .start-btn {
            background-color: #28a745;
        }

        .modal {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }

        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 500px;
        }

        .close {
            float: right;
            cursor: pointer;
            font-size: 1.5rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }

        tr:hover {
            background-color: #f8f9fa;
            cursor: pointer;
        }

        .button-group {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .read-only-field {
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 4px;
            margin: 0.5rem 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="user-info">
            Bem-Vindo, <strong><?php echo htmlspecialchars($_SESSION['username']); ?></strong> 
            (Grupo: <?php echo htmlspecialchars($_SESSION['group']); ?>)
        </div>
        <button class="new-game-btn" onclick="document.getElementById('newGameModal').style.display='block'">
            Criar novo jogo
        </button>
    </div>

    <div class="container">
        <!-- New Game Modal -->
        <div id="newGameModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="document.getElementById('newGameModal').style.display='none'">&times;</span>
                <h2>Criar novo jogo</h2>
                <form method="POST">
                    <div style="margin-bottom: 1rem;">
                        <label for="description">Descrição do jogo:</label><br>
                        <textarea id="description" name="description" rows="4" style="width: 100%; margin-top: 0.5rem;" required></textarea>
                    </div>
                    <button type="submit" class="new-game-btn">Criar jogo</button>
                </form>
            </div>
        </div>

        <!-- Game Details Modal -->
        <div id="gameDetailsModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="document.getElementById('gameDetailsModal').style.display='none'">&times;</span>
                <h2>Detalhes do jogo</h2>
                <form method="POST" id="gameDetailsForm">
                    <input type="hidden" id="game_id" name="game_id">
                    <div style="margin-bottom: 1rem;">
                        <label>ID jogo:</label>
                        <div class="read-only-field" id="modal_game_id"></div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label for="edit_description">Descrição:</label><br>
                        <textarea id="edit_description" name="edit_description" rows="4" style="width: 100%; margin-top: 0.5rem;"></textarea>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label>Início:</label>
                        <div class="read-only-field" id="modal_start_time"></div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label>Fim:</label>
                        <div class="read-only-field" id="modal_end_time"></div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label>Estado:</label>
                        <div class="read-only-field" id="modal_status"></div>
                    </div>
                    <div class="button-group" id="action_buttons">
                        <button type="submit" name="update_game" class="new-game-btn">Editar descrição</button>
                        <button type="submit" name="start_game" class="new-game-btn start-btn">Iniciar jogo</button>
                        <button type="submit" name="delete_game" class="new-game-btn delete-btn">Apagar jogo</button>
                        <button type="button" class="new-game-btn" onclick="document.getElementById('gameDetailsModal').style.display='none'">Fechar</button>
                    </div>
                </form>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>ID jogo</th>
                    <th>Descrição</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                <?php
                if ($result->num_rows > 0) {
                    while($row = $result->fetch_assoc()) {
                        echo "<tr onclick='showGameDetails(" . 
                            json_encode($row) . 
                            ")'>";
                        echo "<td>" . htmlspecialchars($row['idjogo']) . "</td>";
                        echo "<td>" . htmlspecialchars($row['descricao']) . "</td>";
                        echo "<td>" . (is_null($row['inicio']) ? 'N/A' : htmlspecialchars($row['inicio'])) . "</td>";
                        echo "<td>" . (is_null($row['fim']) ? 'N/A' : htmlspecialchars($row['fim'])) . "</td>";
                        echo "<td>" . htmlspecialchars($row['estado']) . "</td>";
                        echo "</tr>";
                    }
                } else {
                    echo "<tr><td colspan='5' style='text-align: center;'>Nenhum jogo encontrado!!!</td></tr>";
                }
                ?>
            </tbody>
        </table>
    </div>

    <script>
        // Close modals when clicking outside
        window.onclick = function(event) {
            if (event.target.className === 'modal') {
                event.target.style.display = "none";
            }
        }

        function showGameDetails(game) {
            const modal = document.getElementById('gameDetailsModal');
            const form = document.getElementById('gameDetailsForm');
            const actionButtons = document.getElementById('action_buttons');
            
            // Set values in the modal
            document.getElementById('game_id').value = game.idjogo;
            document.getElementById('modal_game_id').textContent = game.idjogo;
            document.getElementById('edit_description').value = game.descricao;
            document.getElementById('modal_start_time').textContent = game.inicio || 'N/A';
            document.getElementById('modal_end_time').textContent = game.fim || 'N/A';
            document.getElementById('modal_status').textContent = game.estado;

            // Show/hide action buttons based on status
            const updateBtn = form.querySelector('[name="update_game"]');
            const startBtn = form.querySelector('[name="start_game"]');
            const deleteBtn = form.querySelector('[name="delete_game"]');

            if (game.estado === 'por_iniciar') {
                updateBtn.style.display = 'block';
                startBtn.style.display = 'block';
                deleteBtn.style.display = 'block';
                document.getElementById('edit_description').disabled = false;
            } else {
                updateBtn.style.display = 'none';
                startBtn.style.display = 'none';
                deleteBtn.style.display = 'none';
                document.getElementById('edit_description').disabled = true;
            }

            modal.style.display = 'block';
        }
    </script>
</body>
</html>

<?php
$stmt->close();
$conn->close();
?>