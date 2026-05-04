<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jogo Marsamis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .login-container {
            background-color: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }

        .login-title {
            text-align: center;
            margin-bottom: 1.5rem;
            color: #1a73e8;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }

        input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 1rem;
        }

        input:focus {
            outline: none;
            border-color: #1a73e8;
            box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.2);
        }

        button {
            width: 100%;
            padding: 0.75rem;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        button:hover {
            background-color: #1557b0;
        }

        .error-message {
            color: #dc3545;
            margin-top: 1rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2 class="login-title">Login Jogo</h2>
        <form method="POST" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="group">Grupo</label>
                <input type="text" id="group" name="group" required>
            </div>
            
            <div class="form-group">
                <label for="server_ip">Ip Server</label>
                <input type="text" id="server_ip" name="server_ip" required>
            </div>
            
            <div class="form-group">
                <label for="server_port">Porta Server</label>
                <input type="number" id="server_port" name="server_port" min="1" max="65535" required>
            </div>
            
            <button type="submit">Login</button>
        </form>
        <?php
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $username = $_POST["username"] ?? '';
            $group = $_POST["group"] ?? '';
            $server_ip = $_POST["server_ip"] ?? '';
            $server_port = $_POST["server_port"] ?? '';

            try {
                $conn = new mysqli($server_ip, "root", "", "pisid", $server_port);
                
                if ($conn->connect_error) {
                    throw new Exception("Conexão falhou com o erro: " . $conn->connect_error);
                }

                $stmt = $conn->prepare("SELECT utilizador_id, nome, grupo FROM utilizador WHERE nome = ? AND grupo = ?");
                $stmt->bind_param("si", $username, $group);
                $stmt->execute();
                $result = $stmt->get_result();

                if ($result->num_rows > 0) {
                    $user = $result->fetch_assoc();
                    session_start();
                    $_SESSION['user_id'] = $user['utilizador_id'];
                    $_SESSION['username'] = $user['nome'];
                    $_SESSION['group'] = $user['grupo'];
                    $_SESSION['server_ip'] = $server_ip;
                    $_SESSION['server_port'] = $server_port;
                    
                    header("Location: dashboard.php");
                    exit();
                } else {
                    echo "<p class='error-message'>Utilizador Inválido ou grupo!!!</p>";
                }

                $stmt->close();
                $conn->close();
            } catch (Exception $e) {
                echo "<p class='error-message'>Conexão falhou com o erro: " . $e->getMessage() . "</p>";
            }
        }
        ?>
    </div>
</body>
</html>